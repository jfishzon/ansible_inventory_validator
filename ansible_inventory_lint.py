import os
import re
import sys
import argparse


# colors for printing
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# LintInventory object to hold data on each inventory
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
        """
        parse inventory from self.file and populate self.file_dict, seilf.file_str, self.groups, self.hosts
        """
        try:
            with open(self.file, 'r') as f:
                # count lines
                line_num = 1
                for line in f:
                    # populate everything in self.file_dict
                    self.file_dict[line_num] = line
                    # check for groups or hosts
                    if line.startswith('[') or line.endswith(']'):
                        self.groups[line_num] = line
                    elif line.strip() != '' and '#' not in line and '=' not in line:
                        self.hosts[line_num] = line
                    line_num += 1
            # convert to a string to regex on later
            self.file_str = "".join(self.file_dict.values())
            # get values which are also group names in inventory and remove them from self.hosts dictionary.
            to_delete = set([line_num for line_num, host in self.hosts.items() for group in self.groups.values() if host.strip() in group])
            for key in to_delete: del self.hosts[key]
        except FileNotFoundError:
            raise FileNotFoundError(f'No such file as {self.file}')


# LintRule object to hold data over each rule
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
        :return: String --> Regex that was tested
        """
        try:
            regex = re.compile(regex)
        except re.error:
            raise re.error(f'Regex passed is invalid! "{regex}" for rule {self}')
        return regex

    @property
    def color(self):
        if self.level == 'WARN':
            return '\033[93m'
        elif self.level == 'ERROR':
            return '\033[91m'


def populate_rules(user_rule, to_exclude):
    """
    Reads all rules from rules folders and insert them into rules list
    :param user_rule: LintRule --> LintRule Object of regex passed from the user/default
    :param to_exclude: List --> list of rule numbers to exclude
    :return: List --> rules list
    """
    rules = [user_rule]
    for path, folders, files in os.walk('rules'):
        if path != 'rules':
            for file in files:
                with open(os.path.join(path, file), 'r') as f:
                    # Get data from files and create LinRule object
                    rule_impacts = os.path.basename(path)
                    rule_level = re.search('(?<=\))[A-Z]*(?=_)', file).group()
                    rule_name = re.search('(?<=_).*$', file).group()
                    rule_num = re.search('(?<=\()[0-9]{3}(?=\))', file).group()
                    rule_regex = f.readline().strip()
                    if rule_num not in to_exclude:
                        rules.append(LintRule(
                                            impacts=rule_impacts,
                                            level=rule_level,
                                            name=rule_name,
                                            num=rule_num,
                                            regex=rule_regex
                                            ))
    return rules


def test_lint_rules(inventory, lint_rules):
    """
    check which rules catch on inventory, populate inventory.caught_rules with every rule caught
    :param inventory: LintInventory --> a populated LintInventory Object
    :param lint_rules: List --> list of LintRule objects
    :return Boolean --> True or False if any rules that were caught were errors
    """
    for rule in lint_rules:
        error_exists = False
        if rule.impacts == "general-line":
            caught = list(filter(rule.regex.match, inventory.file_dict.values()))
        elif rule.impacts == "general-all":
            caught = rule.regex.search(inventory.file_str)
        elif rule.impacts == "host":
            caught = list(filter(rule.regex.match, inventory.hosts.values()))
            if rule.num == '000':
                caught = set(inventory.hosts.values()) ^ set(caught)
        elif rule.impacts == "group":
            caught = list(filter(rule.regex.match, inventory.groups.values()))
        if caught:
            if rule.level == 'ERROR':
                error_exists = True
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
    return error_exists


def main():
    # initialize static vars & args
    inventories = []
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--path', help='path to config file or folder', required=True, type=str)
    arg_parser.add_argument('--exclude', help='rules to exclude from validation. comma separated', required=False, type=str, default='')
    arg_parser.add_argument('--regex', type=str,
                            help='Regex to apply on all hosts which are not children or vars. By default uses:'
                                '^[a-zA-Z]*-[a-zA-Z0-9]*-[\[]?[0-9]{2}[:]?[0-9]{0,2}[\]]?\.[a-zA-Z0-9-]*\.[a-zA-Z]*[\s]*$',
                            default='^[a-zA-Z]*-[a-zA-Z0-9]*-[\[]?[0-9]{2}[:]?[0-9]{0,2}[\]]?\.[a-zA-Z0-9-]*\.[a-zA-Z]*[\s]*$'
                            )
    args = arg_parser.parse_args()
    args.exclude = [rule_num for rule_num in args.exclude.split(',')]
    # check path validity and user Regex Validity
    path_type = check_path(args.path)
    user_lint_rule = LintRule(
                        impacts='host',
                        level='ERROR',
                        name='USER DEFINED REGEX',
                        num='000',
                        regex=args.regex
                        )
    # populate all lint rules including user lint rule
    lint_rules = populate_rules(user_lint_rule, args.exclude)
    # add LintInventory objects to inventories list
    if path_type == 'file':
        inventory = LintInventory(args.path)
        error_exists = test_lint_rules(inventory, lint_rules)
        inventories.append(inventory)
    else:
        for path, folders, files in os.walk(args.path):
            if 'group_vars' not in path:
                for file in files:
                    inventory = LintInventory(os.path.join(path, file))
                    error_exists = test_lint_rules(inventory, lint_rules)
                    inventories.append(inventory)
    # iterate over inventories list and print errors
    for inv in inventories:
        print(f'\n{bcolors.BOLD}{inv.file}{bcolors.ENDC}')
        if inv.caught_rules:
            if any([True for rule in inv.caught_rules.keys() if rule.level == 'ERROR']):
                error_exists = True
            for rule_caught, lines in inv.caught_rules.items():
                for line_num, line in lines.items():
                    print(f'{rule_caught.color}{rule_caught}, for line {line_num}:"{line}"{bcolors.ENDC}')
        else:
            print(f'{bcolors.OKGREEN}passed!{bcolors.ENDC}')
    # exit with error
    if error_exists:
        sys.exit(1)


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
