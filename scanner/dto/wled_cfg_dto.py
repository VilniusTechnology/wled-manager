
class WLEDCfgDTO:
    def __init__(self, data):
        self.rev = data.get("rev")
        self.vid = data.get("vid")
        self.id = data.get("id", {})
        self.nw = data.get("nw", {})  # Contains espnow and linked_remote
        self.ap = data.get("ap", {})
        self.wifi = data.get("wifi", {})
        self.eth = data.get("eth", {})
        self.hw = data.get("hw", {})
        self.light = data.get("light", {})
        self.def_ = data.get("def", {})
        self.iface = data.get("if", {})
        self.remote = data.get("remote", {})
        self.ol = data.get("ol", {})
        self.timers = data.get("timers", {})
        self.ota = data.get("ota", {})
        self.um = data.get("um", {})

        # Extract MQTT if present in iface
        self.mqtt = self.iface.get("mqtt", {})

    def to_dict(self):
        return {
            "rev": self.rev,
            "vid": self.vid,
            "id": self.id,
            "nw": self.nw,
            "ap": self.ap,
            "wifi": self.wifi,
            "eth": self.eth,
            "hw": self.hw,
            "light": self.light,
            "def": self.def_,
            "if": self.iface,
            "mqtt": self.mqtt,
            "remote": self.remote,
            "ol": self.ol,
            "timers": self.timers,
            "ota": self.ota,
            "um": self.um
        }
