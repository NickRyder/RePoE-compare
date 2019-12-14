import json


def get_stat_translations(json_obj):

    stat_translations = set()

    for entry in json_obj:
        for translation in entry.get("English", []):
            stat_translations.add(translation["string"])

    return stat_translations


def get_stat_translations_not_in(json_obj, not_in_stats=set()):

    stat_translations = set()

    for entry in json_obj:
        if not set(entry["ids"]).issubset(set(not_in_stats)):
            for translation in entry.get("English", []):
                stat_translations.add(translation["string"])

    return stat_translations


def compare_translations(new_file_path, old_file_path):

    new_file_json = json.load(open(new_file_path + "stat_translations.json", "r"))
    old_file_json = json.load(open(old_file_path + "stat_translations.json", "r"))

    new_mods = json.load(open(new_file_path + "mods.json", "r"))

    # new_gems = json.load(open(new_file_path + "gems.json", "r"))

    new_stat_translations = get_stat_translations(new_file_json)
    old_stat_translations = get_stat_translations(old_file_json)

    new_mod_stats = set()
    for mod_value in new_mods.values():
        for stat in mod_value.get("spawn_weights", []):
            new_mod_stats.add(stat["tag"])

    # for gem_value in new_gems.values():
    #     if "acvite_skill" in gem_value:
    #         for stat in gem_value["active_skill"]["stat_conversions"]:
    #             new_mod_stats.add(stat["tag"])

    new_stat_translations_not_mod = get_stat_translations_not_in(
        new_file_json, new_mod_stats
    )
    old_stat_translations_not_mod = get_stat_translations_not_in(
        old_file_json, new_mod_stats
    )
    to_print = "# Added stat translations\n\n"

    to_print += "## not mod translations\n\n"
    added_translations = new_stat_translations_not_mod.difference(old_stat_translations)
    for new_translation in added_translations:
        to_print += f" - ` {new_translation} ` \n\n"
    to_print += "## all translations\n\n"

    added_translations = new_stat_translations.difference(old_stat_translations)
    for new_translation in added_translations:
        to_print += f" - ` {new_translation} ` \n\n"
    return to_print


def compare_stats(new_file_path, old_file_path):

    new_file_json = json.load(open(new_file_path, "r"))
    old_file_json = json.load(open(old_file_path, "r"))

    new_stats = set(new_file_json.keys())
    old_stats = set(old_file_json.keys())

    print("##NEW##")
    print(new_stats.difference(old_stats))
    print("##OLD##")
    print(old_stats.difference(new_stats))


if __name__ == "__main__":
    compare_file = "stat_translations"

    md_compare = compare_translations(f"3.9.0/", f"3.8.0/")
    # compare_file = "stats"
    # md_compare = compare_stats(
    #     f"3.8.0/{compare_file}.json", f"3.7.0/{compare_file}.json"
    # )

    output_file = f"3.8.0_3.9.0_{compare_file}.md"
    with open(output_file, "w") as f:
        f.write(md_compare)

