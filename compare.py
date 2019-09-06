import json
import difflib
import markdown

def compare(new_file, old_file):
    new_file_json = json.load(open(new_file, "r"))
    old_file_json = json.load(open(old_file, "r"))

    print_string = "[TOC]\n"

    new_keys = set(new_file_json.keys())
    old_keys = set(old_file_json.keys())

    deleted_keys = old_keys - new_keys
    added_keys = new_keys - old_keys
    same_keys = set.intersection(new_keys,old_keys)

    if len(deleted_keys) > 0:
        print_string += "# DELETED MODS\n"
        for deleted_key in deleted_keys:
            print_string += f"#### {deleted_key}\n"
            print_string += f"```\n{json.dumps(old_file_json[deleted_key], indent=4, sort_keys=True)}\n```\n"

    if len(added_keys) > 0:
        print_string += "# ADDED MODS\n"


        added_dict = {}
        for added_key in added_keys:
            added_domain = new_file_json[added_key]["domain"]
            added_generation_type = new_file_json[added_key]["generation_type"]
            if added_domain not in added_dict:
                added_dict[added_domain] = {}
            if added_generation_type not in added_dict[added_domain]:
                added_dict[added_domain][added_generation_type] = []
            added_dict[added_domain][added_generation_type].append(added_key)


        for added_domain in added_dict:
            print_string += f"## {added_domain}\n"
            for added_generation_type in added_dict[added_domain]:
                print_string += f"### {added_generation_type}\n"
                for added_key in added_dict[added_domain][added_generation_type]:
                    print_string += f"#### {added_key}\n"
                    print_string += f"```\n {json.dumps(new_file_json[added_key], indent=4, sort_keys=True)}\n```\n"

    print_string += f"# CHANGED MODS\n"
    for same_key in same_keys:
        if str(new_file_json[same_key]) != str(old_file_json[same_key]):
            new_item = new_file_json[same_key]
            old_item = old_file_json[same_key]

            print_string += f"#### {same_key}\n"
            for key in new_item:
                if str(new_item[key]) != str(old_item[key]):
                    print_string += f"##### {key}\n"
                    print_string += f"```\n-new-\n"
                    print_string += f"{new_item[key]} \n"
                    print_string += f"-old-\n"
                    print_string += f"{old_item[key]} \n```\n"


    return print_string



if __name__ == "__main__":
    md_compare = compare("3.7.0/mods.json", "3.6.0/mods.json")
    print(md_compare)
