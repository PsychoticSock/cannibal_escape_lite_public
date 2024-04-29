from AoE2ScenarioParser.datasets.buildings import BuildingInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import csv

from cannibal_constants import dfu, getarea, CustomAreas

um_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\CannibalSourceMapClassesJuly2022.aoe2scenario"
um_test_scenario_target = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\Coordinate_Finder.aoe2scenario"

scenario = AoE2DEScenario.from_file(um_test_scenario_source)

tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, scenario.player_manager


map_width = mm.map_width
map_height = mm.map_height

x_coords = {}
y_coords = {}
get_coords = true
if get_coords == True:
    cursor_found = ([unit for unit in um.get_player_units(PlayerId.ONE) if unit.unit_const == dfu.COORDINATE_CURSOR.ID])
    if not cursor_found:
        um.add_unit(player=PlayerId.ONE, unit_const=dfu.COORDINATE_CURSOR.ID, x=0.5, y=0.5)

        declare_vars = tm.add_trigger("declare_vars", enabled=False, looping=False)
        declare_vars.new_condition.script_call("""int current_x_position = 0;
int current_y_position = 0;""")

        for x_coord in range(map_width):
            x_coords = tm.add_trigger(f"report_cursor_{x_coord}", enabled=True, looping=True)
            x_coords.new_condition.objects_in_area(quantity=1,
                                                   object_list=dfu.COORDINATE_CURSOR.ID,
                                                   source_player=PlayerId.ONE,
                                                   area_x1=x_coord,
                                                   area_y1=0,
                                                   area_x2=x_coord,
                                                   area_y2=map_height)
            x_coords.new_effect.script_call(message=f"""void set_x_{x_coord}(){{
current_x_position = {x_coord};
}}""")

        for y_coord in range(map_width):
            y_coords = tm.add_trigger(f"report_cursor_{y_coord}", enabled=True, looping=True)
            y_coords.new_condition.objects_in_area(quantity=1,
                                                   object_list=dfu.COORDINATE_CURSOR.ID,
                                                   source_player=PlayerId.ONE,
                                                   area_x1=0,
                                                   area_y1=y_coord,
                                                   area_x2=map_width,
                                                   area_y2=y_coord)
            y_coords.new_effect.script_call(message=f"""void set_y_{y_coord}(){{
    current_y_position = {y_coord};
}}""")
#tm.triggers = []
#scenario.write_to_file(um_test_scenario_target)