from .dto.wled_dto import WLEDDeviceFullInfoDTO

class WLEDJsonBuilder:
    @staticmethod
    def build(dto: WLEDDeviceFullInfoDTO):
        return dto.to_dict()
