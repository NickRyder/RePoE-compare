import json

def refactor_grants_effect(file):
    file_json = json.load(open(file, "r"))

    for key, value in file_json.items():
        if "grants_effect" in value:
            grants_effect = value.pop("grants_effect")
            if len(grants_effect) == 0:
                value["grants_effects"] = []
            else:
                value["grants_effects"] = [grants_effect]
    json.dump(file_json, open(file, "w"), indent=2, sort_keys=True)



if __name__=="__main__":
    refactor_grants_effect("3.6.0/mods.json")