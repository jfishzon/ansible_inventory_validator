import re
import os
import sys
import argparse


class Inventory:
    def __init__(self, path):
        self.path = path
        self.parsed_dict = ''


class ValidationException(Exception):
    pass


class ColonValidationException(Exception):
    pass


def read_inventory(inventory):
    """
    :param inventory: Inventory Object --> Path of file to read
    :return: Dict --> Dictionary representation of an Inventory
    """
    parsed_dict = {}
    try:
        with open(inventory.path, 'r') as config:
            lines = config.readlines()
            for line in lines:
                line = line.strip()
                # ignore empty lines and comments
                if line != '' and '#' not in line:
                    if re.match('^\[[-_a-zA-Z0-9:]*\]$', line):
                        key = line.replace('[','').replace(']','')
                        parsed_dict[key] = []
                    else:
                        parsed_dict[key].append(line)
    except FileNotFoundError:
        print(f'{inventory.path} failed.')
        print("Inventory wasn't found! Please enter a valid path.")
        sys.exit(1)

    try:
        if len(parsed_dict.keys()) == 0:
            raise ValidationException
        for key, val in parsed_dict.items():
            if val == []:
                raise ValidationException
    except ValidationException:
        print(f'{inventory.path} failed.')
        print('Invalid ansible inventory file.')
        sys.exit(1)

    return parsed_dict


def check_regex_validity(regex):
    """
    :param regex: String --> Regex to test
    :return: Boolean
    """
    try:
        re.compile(regex)
    except re.error:
        print(f'Regex passed is invalid! {regex}')
        sys.exit(1)

    return True


def check_inventory_validity(inventory, regex):
    """
    :param inventory: Inventory Object --> Dictionary representation of an Inventory
    :param regex: String --> A Regex Pattern
    :return: Boolean
    """
    inventory_file = inventory.parsed_dict
    try:
        r = re.compile(regex)
        values_list = []
        for key, val in inventory_file.items():
            # check if key is not a special key
            if ':children' not in key and ':vars' not in key:
                values_list.extend(val)
            # check for broken values such as group:lalala
            elif not any([re.match('.*:children$', key), re.match('.*:vars$', key)]):
                raise ColonValidationException
        # run regex over list and compare list lengths, if there's a difference, raise an error.
        regexed_list = list(filter(r.match, values_list))
        if len(regexed_list) != len(values_list):
            raise ValidationException
    except ValidationException:
        non_regexed = set(values_list) ^ set(regexed_list)
        print(f'{inventory.path} failed.')
        print(f'Failed verifying the inventory! Problem with: {non_regexed}')
        sys.exit(1)
    except ColonValidationException:
        print(f'{inventory.path} failed.')
        print(f'Key {key}, not allowed.')
        sys.exit(1)

    return True


def check_path(path):
    """
    :param path: String --> The path to validate
    :return: String --> 'file' or 'folder'
    """
    try:
        # check if exists and return if file or folder
        if os.path.exists(path):
            if os.path.isfile(path):
                return 'file'
            else:
                return 'folder'
        raise ValidationException
    except ValidationException:
        print(f"Path {path} doesn't exist! please enter a valid path.")
        sys.exit(1)


def main():
    # initialize argparse, add arguments & parse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='path to config file or folder', required=True, type=str)
    parser.add_argument('--regex',type=str,
                        help='Regex to apply on all groups which are not children or vars. By default works by:'
                             '^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$',
                        default='^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$')
    args = parser.parse_args()
    # validate args
    check_regex_validity(args.regex)
    path_type = check_path(args.path)
    if path_type == 'file':
        # parse inventory
        inventory = Inventory(args.path)
        inventory.parsed_dict = read_inventory(inventory)
        print(inventory.parsed_dict)
        check_inventory_validity(inventory, args.regex)
        print(f'Inventory {args.path} passed!')
        sys.exit(0)
    else:
        # iterate over files in path and parse them as ansible Inventory files
        for path, dirs, files in os.walk(args.path):
            for file in files:
                file = os.path.join(path,file)
                # parse inventory
                inventory = Inventory(file)
                inventory.parsed_dict = read_inventory(inventory)
                check_inventory_validity(inventory, args.regex)
                print(f'Inventory {file} passed!')
        sys.exit(0)


if __name__ == '__main__':
    main()
