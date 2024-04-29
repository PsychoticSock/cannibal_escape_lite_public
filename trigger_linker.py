
from __future__ import annotations

from typing import List

from AoE2ScenarioParser.helper.list_functions import listify
from AoE2ScenarioParser.objects.data_objects.trigger import Trigger

from AoE2ScenarioParser.datasets.trigger_lists import DifficultyLevel
from AoE2ScenarioParser.datasets.units import UnitInfo
from AoE2ScenarioParser.objects.managers.de.trigger_manager_de import TriggerManagerDE

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
import shortuuid


def chain_triggers(
        trigger_list: List[Trigger],
        delay_list: int| List[int]|bool,
        tm: TriggerManagerDE,
        activate: bool = True
):
    trigger_list: List[Trigger] = listify(trigger_list)
    if delay_list != False:  # With delays:
        delay_list: List[int] = listify(delay_list)
    if delay_list == False:  #Without delays:
        for trigger_id, trigger in enumerate(trigger_list):
            next_trigger_id = trigger_id + 1
            if trigger_id < len(trigger_list)-1:
                if activate:
                    trigger.new_effect.activate_trigger(trigger_list[next_trigger_id].trigger_id)
                else:
                    trigger.new_effect.deactivate_trigger(trigger_list[next_trigger_id].trigger_id)
    else:  #With delays:
        for trigger_id, trigger in enumerate(trigger_list):
            next_trigger_id = trigger_id + 1
            if trigger_id < len(trigger_list)-1:
                if activate:
                    delay_trigger_name = f"Delay={delay_list[trigger_id]} " + trigger_list[next_trigger_id].name + " " + str(
                        shortuuid.ShortUUID().random(8))
                    delay_trigger_name = tm.add_trigger(delay_trigger_name, enabled=False, looping=False)
                    trigger_list[trigger_id].new_effect.activate_trigger(delay_trigger_name.trigger_id)
                    delay_trigger_name.new_condition.timer(delay_list[trigger_id])
                    delay_trigger_name.new_effect.activate_trigger(trigger_list[next_trigger_id].trigger_id)
                else:
                    delay_trigger_name = f"Delay={delay_list[trigger_id]} " + trigger_list[
                        next_trigger_id].name + " " + str(
                        shortuuid.ShortUUID().random(8))
                    delay_trigger_name = tm.add_trigger(delay_trigger_name, enabled=False, looping=False)
                    trigger_list[trigger_id].new_effect.activate_trigger(delay_trigger_name.trigger_id)
                    delay_trigger_name.new_condition.timer(delay_list[trigger_id])
                    delay_trigger_name.new_effect.deactivate_trigger(trigger_list[next_trigger_id].trigger_id)


def link_triggers(
        sources: Trigger | List[Trigger],
        targets: Trigger | List[Trigger],
        activate: bool = True,
        delay: int = 0,
        deactivate_other_sources=False,
):
    sources: List[Trigger] = listify(sources)
    targets: List[Trigger] = listify(targets)

    for source in sources:
        source.new_condition.timer(timer=delay)
        for target in targets:
            if activate:
                source.new_effect.activate_trigger(target.trigger_id)
            else:
                source.new_effect.deactivate_trigger(target.trigger_id)
        if deactivate_other_sources:
            for other_source in sources:
                if other_source is not source:
                    source.new_effect.deactivate_trigger(other_source.trigger_id)


def cascade_triggers(trigger_list: list[Trigger], delay_list=-1, same_delay: bool = True):
    if delay_list == -1:
        print("Link triggers with no delay")
        for x, trigger in enumerate(trigger_list):
            print(x, trigger.name)
            if x<(len(trigger_list)-1):
                trigger_list[x].new_effect.activate_trigger(trigger_list[x+1].trigger_id)
    else:
        if same_delay == False:
            if len(delay_list) != len(trigger_list)-1:
                print("raise_some_error: Trigger list and delay list must be of equal length if delays are not equal")
            else:
                print("link triggers with unequal delays")
                for x, trigger in enumerate(trigger_list):
                    print(x, trigger.name)
                    if x < (len(trigger_list) - 1):
                        delay_trigger_name = f"Delay={delay_list[x]} " + trigger_list[x + 1].name + " " + str(shortuuid.ShortUUID().random(8))
                        delay_trigger_name = trigger_manager.add_trigger(delay_trigger_name, enabled=True, looping=False)
                        trigger_list[x].new_effect.activate_trigger(delay_trigger_name.trigger_id)
                        delay_trigger_name.new_condition.timer(delay_list[x])
                        delay_trigger_name.new_effect.activate_trigger(trigger_list[x + 1].trigger_id)
                        print(delay_trigger_name)
        if same_delay == True:
            if len(delay_list) !=1:
                print("raise_some_error: Delay list has more than one item yet delays meant to be the same")
            else:
                print("link triggers with equal delays")


if __name__ == '__main__':

    input_path = "C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\TriggerLinkTest_Source.aoe2scenario"
    output_path = "C:\\Users\\User\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\TriggerLinkTest.aoe2scenario"  # Don't overwrite your source file!


    scenario = AoE2DEScenario.from_file(input_path)

    # Uncomment as applicable
    #mm = scenario.mm
    trigger_manager = scenario.trigger_manager
    #um = scenario.um
    trigger_manager.triggers = []


    hello_world = trigger_manager.add_trigger("Hello Parser!", enabled=True, looping=True)
    hello_world.new_condition.timer(10)
    for player in range(1, 9):
        hello_world.new_effect.send_chat(source_player=player,
                                         message=f"Hello player {player}. Welcome to your first experience with parser!")

    second_trigger = trigger_manager.add_trigger("Second trigger", enabled=True, looping=True)
    second_trigger.new_condition.difficulty_level(quantity=DifficultyLevel.HARDEST)
    second_trigger.new_effect.create_object(object_list_unit_id=UnitInfo.CHU_KO_NU.ID,
                                            source_player=player,
                                            location_x=10,
                                            location_y=10)

    third_trigger = trigger_manager.add_trigger("Third trigger", enabled=True, looping=True)
    third_trigger.new_condition.difficulty_level(quantity=DifficultyLevel.EASIEST)
    third_trigger.new_effect.create_object(object_list_unit_id=UnitInfo.HALBERDIER.ID,
                                            source_player=player,
                                            location_x=40,
                                            location_y=40)

    chain_triggers([hello_world, second_trigger, third_trigger], [2, 3], True)

    #chain_triggers([hello_world, second_trigger,third_trigger], False, True)
    #cascade_triggers([hello_world, second_trigger, third_trigger], [12, 24], False)
    scenario.write_to_file(output_path)






