# Entidades do domínio: Classes puras para representar dados sem dependências externas

class SEPData:
    def __init__(self, date, sep_intensity, temperature, ice_extent, ozone_level, kp_index, cluster=None):
        self.date = date
        self.sep_intensity = sep_intensity
        self.temperature = temperature
        self.ice_extent = ice_extent
        self.ozone_level = ozone_level
        self.kp_index = kp_index
        self.cluster = cluster