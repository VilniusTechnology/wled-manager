import logging
import time
import asyncio
import httpx
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

def determine_health_status_v2(
    is_online: bool,
    response_time: Optional[float],
    signal_dbm: Optional[int] = None,
    signal_pct: Optional[int] = None,
    uptime_sec: Optional[int] = None,
    free_heap: Optional[int] = None
) -> Tuple[str, int, Dict[str, Any]]:
    """
    Composite health assessment using multiple WLED metrics.
    Returns (status_label, grade, detail_dict).
    """
    if not is_online:
        return "offline", 1, {}

    score = 0.0
    details = {}

    # --- WiFi Signal (35% weight) ---
    if signal_dbm is not None:
        if signal_dbm >= -50:   signal_score = 100
        elif signal_dbm >= -65: signal_score = 80
        elif signal_dbm >= -75: signal_score = 50
        elif signal_dbm >= -85: signal_score = 20
        else:                   signal_score = 5
        score += signal_score * 0.35
        details['signal_dbm'] = signal_dbm
        details['signal_score'] = signal_score
    elif signal_pct is not None:
        # If we only have percentage
        score += signal_pct * 0.35
        details['signal_pct'] = signal_pct
    else:
        score += 50 * 0.35  # neutral if unknown

    # --- TCP Latency (25% weight) ---
    # WLED uses 25% weight because it lacks MQTT/Link stability metrics
    if response_time is not None:
        if response_time < 0.05:    latency_score = 100
        elif response_time < 0.1:   latency_score = 80
        elif response_time < 0.3:   latency_score = 50
        elif response_time < 1.0:   latency_score = 20
        else:                       latency_score = 5
        score += latency_score * 0.25
        details['response_time_ms'] = round(response_time * 1000, 1)
        details['latency_score'] = latency_score
    else:
        score += 50 * 0.25

    # --- Uptime (20% weight) ---
    if uptime_sec is not None:
        if uptime_sec > 86400:      up_score = 100  # > 1 day
        elif uptime_sec > 3600:     up_score = 70   # > 1 hour
        elif uptime_sec > 300:      up_score = 40   # > 5 min
        else:                       up_score = 10   # just booted
        score += up_score * 0.20
        details['uptime_sec'] = uptime_sec
        details['uptime_score'] = up_score
    else:
        score += 50 * 0.20

    # --- Free Heap (20% weight) ---
    if free_heap is not None:
        if free_heap > 20000:       heap_score = 100 # > 20KB
        elif free_heap > 10000:     heap_score = 70  # > 10KB
        elif free_heap > 5000:      heap_score = 40  # > 5KB
        else:                       heap_score = 10  # very low heap
        score += heap_score * 0.20
        details['free_heap'] = free_heap
        details['heap_score'] = heap_score
    else:
        score += 50 * 0.20

    # --- Map score to label and grade ---
    if score >= 80:   
        status, grade = "excellent", 5
    elif score >= 60: 
        status, grade = "good", 4
    elif score >= 40: 
        status, grade = "moderate", 3
    elif score >= 20: 
        status, grade = "slow", 2
    else:             
        status, grade = "poor", 1

    details['composite_score'] = round(score, 1)
    return status, grade, details


async def resolve_device_health_status(ip: str, timeout: float = 5.0, expected_mac: Optional[str] = None) -> Tuple[bool, Optional[float], str, int, Dict[str, Any], Optional[str], Optional[str]]:
    """
    Perform health check and resolve status for a WLED device.
    Returns: (is_online, response_time, status, grade, health_details, error_msg, mac)
    """
    start_time = time.time()
    is_online = False
    response_time = None
    error_msg = None
    mac = None

    # 1. TCP Port 80 Check (Reachability & Latency)
    actual_timeout = min(timeout, 5.0)
    try:
        coro = asyncio.open_connection(ip, 80)
        reader, writer = await asyncio.wait_for(coro, timeout=actual_timeout)
        response_time = time.time() - start_time
        is_online = True
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        logger.debug(f"TCP health check failed for {ip}: {e}, falling back to HTTP info")
        # Don't immediately fail; we might still be able to hit HTTP if TCP connect misbehaved

    # 2. Fetch /json/info for richer metrics
    signal_dbm = None
    signal_pct = None
    uptime_sec = None
    free_heap = None
    wifi_channel = None
    bssid = None
    
    try:
        async with httpx.AsyncClient(timeout=actual_timeout) as client:
            http_start = time.time()
            response = await client.get(f"http://{ip}/json/info")
            if response.status_code == 200:
                if not is_online:
                    # If TCP failed but HTTP worked (rare but possible), recalculate response time
                    is_online = True
                    response_time = time.time() - http_start
                    
                info = response.json()
                mac = info.get("mac", "")
                
                # Check MAC match if expected_mac provided
                if expected_mac and mac:
                    norm_expected = expected_mac.replace(":", "").lower()
                    norm_actual = mac.replace(":", "").lower()
                    if norm_expected != norm_actual:
                        logger.warning(f"MAC mismatch for {ip}: expected {expected_mac}, got {mac}")
                        return False, None, "offline", 1, {}, f"IP reassigned: expected MAC {expected_mac}, found {mac}", mac

                wifi_data = info.get("wifi", {})
                if isinstance(wifi_data, dict):
                    signal_dbm = wifi_data.get("rssi")
                    signal_pct = wifi_data.get("signal")
                    wifi_channel = wifi_data.get("channel")
                    bssid = wifi_data.get("bssid")
                
                uptime_sec = info.get("uptime")
                free_heap = info.get("freeheap")
            else:
                if not is_online:
                    error_msg = f"HTTP {response.status_code}"
    except Exception as e:
        logger.debug(f"HTTP info check failed for {ip}: {e}")
        if not is_online:
            error_msg = str(e)

    if not is_online:
        status, grade, details = determine_health_status_v2(False, None)
        return False, None, status, grade, details, error_msg, mac

    # 3. Calculate Composite Score
    status, grade, details = determine_health_status_v2(
        is_online=True,
        response_time=response_time,
        signal_dbm=signal_dbm,
        signal_pct=signal_pct,
        uptime_sec=uptime_sec,
        free_heap=free_heap
    )
    
    if wifi_channel:
        details['wifi_channel'] = wifi_channel
    if bssid:
        details['bssid'] = bssid

    return True, response_time, status, grade, details, error_msg, mac
