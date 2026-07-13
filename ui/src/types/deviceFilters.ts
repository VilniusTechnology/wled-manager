export interface DeviceFilters {
  status: string
  search: string
  hasBackups: boolean | null
  stateOn: boolean | null
  adopted: boolean | null // null = show all, true = only adopted, false = only unadopted
  hasStaticIp: boolean | null // null = show all, true = only static IP, false = only DHCP
  wifiSleep: boolean | null
  turnOnAfterPowerUp: boolean | null
}