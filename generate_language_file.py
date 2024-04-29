###### String Mod Stuff Below Here ######
import os
import shutil

from cannibal_constants import dfu, CustomTechs, mod_prefix, creation_offset, language_file_help_offset, \
    help_converter_offset, tech_mod_prefix, \
    display_instructions_lookup, HIDE, hints
from local_paths import language_file_path, language_file_root

starting_unit = 2600

description_after_name = "<b> (<cost>) \\n"
stats_list = " \\n<hp> <attack> <armor> <piercearmor> <range>"

name = 0
verb = 1
description = 2

if __name__ == '__main__':
    string_list = []
    new_dfu = []
    sorted_units = [unit for unit in dfu]

    sorted_units = sorted((unit for unit in dfu),
           key=lambda x: x.ID)

    f = open("key-value-modded-strings-utf8.txt", "w")

    for unit in sorted_units: # type: dfu
        unit_id = str(unit.ID)
        unit_name = unit.DISPLAYED_UNIT_NAME
        unit_class = unit.OBJECT_CLASS
        unit_verb = unit.TRAIN_VERB
        unit_description = unit.UNIT_DESCRIPTION

        if not unit_description:
            unit_description = ""

        language_file_name = str(unit.ID + mod_prefix)
        language_file_creation = str(unit.ID + mod_prefix + creation_offset)
        language_file_help = str(unit.ID + mod_prefix + language_file_help_offset)
        help_converter = str(unit.ID + mod_prefix + creation_offset + help_converter_offset)

        #new_dfu.append(str(unit.name) + " = (" + str(unit.ID) + ", " + str(unit_class) + ', "' + unit_name + "," + unit_verb + ", " + unit_description + ")")

        if unit.DISPLAYED_UNIT_NAME is not None:
            if unit.OVERRIDE_STRINGS is not None:
                string_list.append(str(unit.OVERRIDE_STRINGS[0]) + " " + '"' + unit_name + '"')
            else:
                if unit_verb == HIDE:
                    string_list.append(language_file_name + ' ""')
                else:
                    string_list.append(language_file_name + " " + '"' + unit_name + '"')

        if unit.TRAIN_VERB is not None:
            if unit.OVERRIDE_STRINGS is not None:
                string_list.append(str(unit.OVERRIDE_STRINGS[1]) + " " + '"' + unit_verb + " <b>"
                                   + unit_name + description_after_name + " " + unit_description + stats_list + '"')

                string_list.append(str(unit.OVERRIDE_STRINGS[2]) + " " + '"' + unit_verb + " <b>"
                                   + unit_name + description_after_name + " " + unit_description + stats_list + '"')
            else:
                if unit_verb == HIDE:
                    string_list.append(language_file_creation + ' ""')
                    string_list.append(help_converter + ' ""')
                else:
                    string_list.append(language_file_creation + " " + '"' + unit_verb + " <b>"
                                       + unit_name + description_after_name + " " + unit_description + stats_list + '"')
                    string_list.append(help_converter + " " + '"' + unit_verb + " <b>"
                                       + unit_name + description_after_name + " " + unit_description + stats_list + '"')

    for language_string in string_list:
        f.write(f"{language_string}\n")
        print(language_string)

    #for language_string in new_dfu:
    #    print(language_string)

    tech_list = []

    for tech in CustomTechs: # type: CustomTechs
        tech_id = str(tech.ID)
        tech_name = str(tech.NAME).title().replace("_", " ")  #str(tech.NAME).title()
        tech_verb = tech.VERB
        tech_description = str(tech.DESCRIPTION)



        tech_language_file_name = str(tech.ID + tech_mod_prefix)

        tech_language_file_creation = str(tech.ID + tech_mod_prefix + creation_offset)
        tech_language_file_help = str(tech.ID + tech_mod_prefix + language_file_help_offset)
        tech_help_converter = str(tech.ID + tech_mod_prefix + creation_offset + help_converter_offset)

        if not tech_description:
            tech_description = ""

        if tech_verb == HIDE:
            tech_list.append(tech_language_file_name + ' ""')
            tech_list.append(tech_language_file_creation + ' ""')
            tech_list.append(tech_help_converter + ' ""')
        else:
            tech_list.append(tech_language_file_name + " " + '"' + tech_name + '"')
            tech_list.append(tech_language_file_creation + " " + '"' + tech_verb + " <b>"
                           + tech_name + description_after_name + " " + tech_description + '"')
            tech_list.append(tech_help_converter + " " + '"' + tech_verb + " <b>"
                           + tech_name + description_after_name + " " + tech_description + '"')

    for language_string in tech_list:
        f.write(f"{language_string}\n")
        print(language_string)
    f.close()

    all_string_file = []
    for language_string in string_list:
        all_string_file.append(language_string)
    for language_string in tech_list:
        all_string_file.append(language_string)
    for language_string in display_instructions_lookup.values():
        all_string_file.append(language_string)
    for language_string in hints:
        all_string_file.append(language_string.FULL_LANGUAGE_STRING)
    with open(language_file_path, 'w') as fp:
        fp.write('\n'.join(all_string_file))

    folder_list = ["br",
                   "de",
                   "es",
                   "fr",
                   "hi",
                   "it",
                   "jp",
                   "ko",
                   "ms",
                   "mx",
                   "pl",
                   "ru",
                   "tr",
                   "tw",
                   "vi",
                   "zh"]  # NB en is not included here
    for folder in folder_list:
        os.makedirs(os.path.dirname(f"{language_file_root}{folder}\\strings\\key-value\\key-value-modded-strings-utf8.txt"), exist_ok=True)
        shutil.copyfile(language_file_path, f"{language_file_root}{folder}\\strings\\key-value\\key-value-modded-strings-utf8.txt")
        print(f"{language_file_root}{folder}\\strings\\key-value\\key-value-modded-strings-utf8.txt")


# language file pitfalls:
# Don't include braces { }
# Don't include newlines except at the end of a string
# Ensure no double backslashes \\n, only \n is valid
# Can check for some valid strings using regex ^\d+\s".*"$
# Lines that don't match that regex are not valid