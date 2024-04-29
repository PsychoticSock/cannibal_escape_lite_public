from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

xs_test_script_path = "C:\\Users\\Username\\PycharmProjects\\cannibal_escape_lite_aoe2de\\xs_test_bed"
xs_test_scenario_source = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\xs_test_scenario.aoe2scenario"
xs_test_scenario_target = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\xs_test_scenario_out.aoe2scenario"

scenario = AoE2DEScenario.from_file(xs_test_scenario_source)

tm, um, mm, xm, pm = scenario.trigger_manager, scenario.unit_manager, scenario.map_manager, scenario.xs_manager, \
                     scenario.player_manager

tm.triggers = []  # Uncomment this in order to wipe all triggers from the map at start
tm.variables = []  # Uncomment this in order to wipe all variables from the map at start

xm.add_script(xs_test_script_path)

scenario.write_to_file(xs_test_scenario_target)