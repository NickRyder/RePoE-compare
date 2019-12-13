import json
import difflib
from tqdm import tqdm


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


import re


def _strip_camel_case(string):
    return re.findall("[A-Z][a-z]*", string)


def longest_substring_finder(string1, string2):
    """https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
    generates longest substring of string1, string2"""
    answer = []
    string1, string2 = _strip_camel_case(string1), _strip_camel_case(string2)
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = []
        for j in range(len2):
            if i + j < len1 and string1[i + j] == string2[j]:
                match += [string2[j]]
            else:
                if len(match) > len(answer):
                    answer = match
                match = []
        if len(match) > len(answer):
            answer = match
    return "".join(answer)


import itertools


def cluster_keys(keys, minimum_shared_substring_length=5, minimum_cluster_size=6):
    """
    takes in set of keys, return clusters as a dict, and returns all remaining as a set
    """

    substring_clusters = {}

    for key_1, key_2 in tqdm(list(itertools.combinations(keys, 2))):
        common_substring = longest_substring_finder(key_1, key_2)
        if len(common_substring) >= minimum_shared_substring_length:
            if common_substring not in substring_clusters:
                substring_clusters[common_substring] = 0
            substring_clusters[common_substring] += 1

    trimmed_dict = {}
    trimmed_dict["OTHER"] = set()
    for cluster_key, cluster_count in substring_clusters.items():
        if cluster_count >= minimum_cluster_size:
            trimmed_dict[cluster_key] = set()

    for key in keys:
        key_name = "".join(_strip_camel_case(key))
        max_cluster_key = ""
        for cluster_key in trimmed_dict:
            if cluster_key in key_name and len(max_cluster_key) < len(cluster_key):
                max_cluster_key = cluster_key
        if max_cluster_key != "":
            trimmed_dict[max_cluster_key].add(key)
        else:
            trimmed_dict["OTHER"].add(key)

    final_dict = {}
    for key, value in trimmed_dict.items():
        if len(value) > 0:
            final_dict[key] = value


    return final_dict


def _create_collapsible_section(title, data):
    return f"<details>\n <summary>{title}</summary><blockquote> \n {data} \n </blockquote></details>\n"


def _json_code_block(json_entry):
    return f"\n```\n{json.dumps(json_entry, indent=4, sort_keys=True)}\n```\n"


def compare(new_file, old_file, mods=True):
    new_file_json = json.load(open(new_file, "r"))
    old_file_json = json.load(open(old_file, "r"))

    print_string = ""

    new_keys = set(new_file_json.keys())
    old_keys = set(old_file_json.keys())

    deleted_keys = old_keys - new_keys
    added_keys = new_keys - old_keys
    changed_keys = set.intersection(new_keys, old_keys)
    for key in list(changed_keys):
        if str(new_file_json[key]) == str(old_file_json[key]):
            changed_keys.remove(key)

    if len(deleted_keys) > 0:
        clusters_to_keys = cluster_keys(deleted_keys)
        deleted_text = ""
        for cluster in clusters_to_keys:
            cluster_text = ""
            for key in clusters_to_keys[cluster]:
                cluster_text += _create_collapsible_section(
                    key, _json_code_block(old_file_json[key])
                )
            deleted_text += _create_collapsible_section(cluster, cluster_text)
        print_string += _create_collapsible_section("DELETED", deleted_text)

    # if mods:
    #     print_string += generate_added_keys_for_mods(added_keys, new_file_json)
    # else:
    if len(added_keys) > 0:
        clusters_to_keys = cluster_keys(added_keys)
        print(clusters_to_keys.keys())
        added_text = ""
        for cluster in clusters_to_keys:
            cluster_text = ""
            for key in clusters_to_keys[cluster]:
                cluster_text += _create_collapsible_section(
                    key, _json_code_block(new_file_json[key])
                )
            added_text += _create_collapsible_section(cluster, cluster_text)
        print_string += _create_collapsible_section("ADDED", added_text)

    if len(changed_keys) > 0:
        clusters_to_keys = cluster_keys(changed_keys)
        print(clusters_to_keys.keys())
        changed_text = ""
        for cluster in clusters_to_keys:
            cluster_text = ""
            for key in clusters_to_keys[cluster]:
                key_text = f"\n`-new-`\n"
                key_text += _json_code_block(new_file_json[key])
                key_text += f"\n`-old-`\n"
                key_text += _json_code_block(old_file_json[key])
                cluster_text += _create_collapsible_section(key, key_text)

            changed_text += _create_collapsible_section(cluster, cluster_text)
        print_string += _create_collapsible_section("CHANGED", changed_text)

    return print_string


if __name__ == "__main__":
    compare_file = "mods"

    md_compare = compare(
        f"3.8.0/{compare_file}.json", f"3.7.0/{compare_file}.json", mods=False
    )

    output_file = f"3.7.0_3.8.0_{compare_file}.md"
    with open(output_file, "w") as f:
        f.write(md_compare)

