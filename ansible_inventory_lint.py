import os
import re
import sys
import argparse
#TODO rules, rules exclusions, etc..


class LintRule:
    def __init__(self, impacts, level, name, num, regex):
        self.impacts = impacts
        self.level = level
        self.name = name
        self.num = num
        self.regex = regex

    def __str__(self):
        return f'{self.num}_{self.level}_{self.name}'

def populate_rules():
    rules_dict = {
            'host': [],
            'group': [],
            'general': []
            }
    for path, folders, files in os.walk('rules'):
        if path != 'rules':
            for file in files:
                with open(os.path.join(path, file), 'r') as f:
                    rule_impacts = os.path.basename(path)
                    rule_level = re.search('(?<=\))[A-Z]*(?=_)', file).group()
                    rule_name = re.search('(?<=_).*$', file).group()
                    rule_num = re.search('(?<=\()[0-9]{3}(?=\))', file).group()
                    rule_regex = f.readline().strip()
                    rules_dict[rule_impacts].append(LintRule(
                                                impacts=rule_impacts,
                                                level=rule_level,
                                                name=rule_name,
                                                num=rule_num,
                                                regex=rule_regex
                                                ))

    return rules_dict


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--path', help='path to config file or folder', required=True, type=str)
    arg_parser.add_argument('--regex', type=str,
                            help='Regex to apply on all hosts which are not children or vars. By default uses:'
                                '^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$',
                            default='^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$'
                            )
    args = arg_parser.parse_args()
    path_type = check_path(args.path)
    if path_type == 'file':
        rules = populate_rules()
        for key,val in rules.items():
            print(key,[str(rule) for rule in val])



def read_inventory_file(file):
    with open(file, 'r') as f:
        line_num = 1
        for line in f:
            print(f'{line_num} {line}')
            line_num += 1


def check_path(path):
    """
    :param path: String --> The path to validate
    :return: String --> 'file' or 'folder'
    """
    # check if exists and return if file or folder
    if os.path.exists(path):
        if os.path.isfile(path):
            return 'file'
        else:
            return 'folder'
    # if neither of the above
    raise FileNotFoundError(f"Path {path} doesn't exist! please enter a valid path.")


if __name__ == '__main__':
    main()