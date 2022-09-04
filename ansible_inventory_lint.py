import os
import re
import sys
import mmap
import argparse
#TODO rules, rules exclusions, etc..


class LintInventory:
    def __init__(self, file):
        self.file = file
        self.file_dict = {}
        self.file_str = ''
        self.groups = {}
        self.hosts = {}
        self.parse_inventory()
        self.caught_rules = {}

    def parse_inventory(self):
        try:
            with open(self.file, 'r') as f:
                line_num = 1
                for line in f:
                    self.file_dict[line_num] = line
                    if re.match('\[.*\]', line):
                        self.groups[line_num] = line
                    elif line.strip() != '' and '#' not in line and '=' not in line:
                        self.hosts[line_num] = line
                    line_num += 1
            self.file_str = "".join(self.file_dict.values())
            # get values which are also group names in inventory and remove them from self.hosts dictionary.
            to_delete = [line_num for line_num, host in self.hosts.items() if f'[{host.strip()}]\n' in self.groups.values()]
            for key in to_delete: del self.hosts[key]

        except FileNotFoundError:
            raise FileNotFoundError(f'No such file as {self.file}')


class LintRule:
    def __init__(self, impacts, level, name, num, regex):
        self.impacts = impacts
        self.level = level
        self.name = name
        self.num = num
        self.regex = self.check_regex_validity(regex)

    def __str__(self):
        return f'{self.num}_{self.level}_{self.name}'

    def check_regex_validity(self,regex):
        """
        :param regex: String --> Regex to test
        :return: Boolean
        """
        try:
            regex = re.compile(regex)
        except re.error:
            raise re.error(f'Regex passed is invalid! "{regex}" for rule {self}')
        return regex


def populate_rules():
    rules = []
    for path, folders, files in os.walk('rules'):
        if path != 'rules':
            for file in files:
                with open(os.path.join(path, file), 'r') as f:
                    rule_impacts = os.path.basename(path)
                    rule_level = re.search('(?<=\))[A-Z]*(?=_)', file).group()
                    rule_name = re.search('(?<=_).*$', file).group()
                    rule_num = re.search('(?<=\()[0-9]{3}(?=\))', file).group()
                    rule_regex = f.readline().strip()
                    rules.append(LintRule(
                                        impacts=rule_impacts,
                                        level=rule_level,
                                        name=rule_name,
                                        num=rule_num,
                                        regex=rule_regex
                                        ))
    return rules


def test_lint_rules(inventory, lint_rules):
    for rule in lint_rules:
        if rule.impacts == "host":
            caught = list(filter(rule.regex.match, inventory.hosts.values()))
        elif rule.impacts == "group":
            caught = list(filter(rule.regex.match, inventory.groups.values()))
        elif rule.impacts == "general-line":
            caught = list(filter(rule.regex.match, inventory.file_dict.values()))
        elif rule.impacts == "general-all":
            caught = rule.regex.search(inventory.file_str)
        if caught:
            caught_lines = {}
            if rule.impacts in ['host', 'group', 'general-line']:
                for item in caught:
                    for line_num, line in inventory.file_dict.items():
                        if line == item and line_num not in caught_lines.keys():
                            caught_lines[line_num] = line.strip('\n')
            else:
                # count characters
                char_count = -1
                for line_num, line in inventory.file_dict.items():
                    char_count += len(line)
                    if caught.span()[0] < char_count <= caught.span()[1]:
                        caught_lines[line_num] = line.strip('\n')
                        break
            # add everything caught to the inventory
            inventory.caught_rules[rule] = caught_lines
    # for caught_rule, lines in inventory.caught_rules.items():
    #     print(caught_rule, lines)


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
    user_lint_rule = LintRule(
                        impacts='host',
                        level='ERROR',
                        name='USER DEFINED REGEX',
                        num='000',
                        regex=args.regex
                        )
    lint_rules = populate_rules()
    if path_type == 'file':
        inventory = LintInventory(args.path)
        test_lint_rules(inventory, lint_rules)

    if inventory.caught_rules:
        for rule_caught, lines in inventory.caught_rules.items():
            for line_num, line in lines.items():
                print(f'{rule_caught}, for line {line_num}:"{line}"')


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
