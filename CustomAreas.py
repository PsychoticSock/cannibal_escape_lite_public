
from enum import Enum

def getarea(area):
    if len(area.value) == 2:
        return {"area_x1": area.X1, "area_y1": area.Y1, "area_x1": area.X1, "area_y1": area.Y1}
    if len(area.value) == 4:
        return {"area_x1": area.X1, "area_y1": area.Y1, "area_x2": area.X2, "area_y2": area.Y2}

def getloc(location):
        return {"location_x": location.X1, "location_y": location.Y1}


class CustomAreas(Enum):
    @property
    def X1(self):
        return self.value[0]
    @property
    def Y1(self):
        return self.value[1]
    @property
    def X2(self):
        try:
            return self.value[2]
        except:
            return self.value[0]
    @property
    def Y2(self):
        try:
            return self.value[3]
        except:
            return self.value[1]
            
    shops_0 = (22, 0, 26, 3)
    shops_1 = (28, 0, 32, 3)
    shops_2 = (34, 0, 38, 3)
    shops_3 = (40, 0, 44, 3)
    shops_4 = (46, 0, 50, 3)
    tile_kingspawns_0 = (28, 10)
    tile_kingspawns_1 = (31, 10)
    tile_kingspawns_2 = (34, 10)
    tile_kingspawns_3 = (37, 10)
    tile_kingspawns_4 = (40, 10)
    tile_kingspawns_5 = (43, 10)
    tile_king_tps_0 = (35, 29)
    tile_king_tps_1 = (37, 29)
    tile_king_tps_2 = (39, 29)
    tile_king_tps_3 = (41, 29)
    tile_king_tps_4 = (43, 29)
    tile_king_tps_5 = (45, 29)
    tile_flags_0 = (95, 68)
    tile_flags_1 = (95, 87)
    tile_flags_2 = (78, 94)
    tile_flags_3 = (61, 86)
    tile_flags_4 = (61, 67)
    tile_flags_5 = (78, 60)