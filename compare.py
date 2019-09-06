import json
import difflib
import markdown


def generate_added_keys_for_mods(added_keys, new_file_json):
    print_string = ""
    if len(added_keys) > 0:
        print_string += "# ADDED\n"


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
    return print_string

def compare(new_file, old_file, mods=True):
    new_file_json = json.load(open(new_file, "r"))
    old_file_json = json.load(open(old_file, "r"))

    print_string = ""

    new_keys = set(new_file_json.keys())
    old_keys = set(old_file_json.keys())

    deleted_keys = old_keys - new_keys
    added_keys = new_keys - old_keys
    same_keys = set.intersection(new_keys,old_keys)

    if len(deleted_keys) > 0:
        print_string += "# DELETED\n"
        for deleted_key in deleted_keys:
            print_string += f"#### {deleted_key}\n"
            print_string += f"```\n{json.dumps(old_file_json[deleted_key], indent=4, sort_keys=True)}\n```\n"

    if mods:
        print_string += generate_added_keys_for_mods(added_keys,new_file_json)
    else:
        if len(added_keys) > 0:
            print_string += "# ADDED\n"
            for added_key in added_keys:
                print_string += f"#### {added_key}\n"
                print_string += f"```\n{json.dumps(new_file_json[added_key], indent=4, sort_keys=True)}\n```\n"


    print_string += f"# CHANGED\n"
    for same_key in same_keys:
        if str(new_file_json[same_key]) != str(old_file_json[same_key]):
            new_item = new_file_json[same_key]
            old_item = old_file_json[same_key]

            print_string += f"#### {same_key}\n"
            all_keys = set(new_item.keys()).union(set(old_item.keys()))
            for key in all_keys:
                new_key = new_item.get(key,"")
                old_key = old_item.get(key,"")
                if str(new_key) != str(old_key):
                    print_string += f"##### {key}\n"
                    print_string += f"```\n-new-\n"
                    print_string += f"{new_key} \n"
                    print_string += f"-old-\n"
                    print_string += f"{old_key} \n```\n"


    return print_string


import md_toc

if __name__ == "__main__":
    compare_file = "gems"


    md_compare = compare(f"3.8.0/{compare_file}.json", f"3.7.0/{compare_file}.json",mods=False)

    output_file = f"3.7.0_3.8.0_{compare_file}.md"
    with open(output_file, "w") as f:
        f.write(md_compare)
