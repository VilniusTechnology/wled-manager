class WLEDStateDTO:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return dict(self.data) if self.data else {}
