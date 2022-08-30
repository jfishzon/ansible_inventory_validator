import re
import os
import sys
import argparse
import logging


class Inventory:
    def __init__(self, path):
        self.path = path
        self.parsed_dict = ''
        self.passed = True
        self.error_info = ''
    
    def __str__(self):
        if self.passed:
            return f'Inventory {self.path} passed!'
        else:
            return f'Inventory {self.path} did not pass. {self.error_info}'


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
    try:
        if len(parsed_dict.keys()) == 0:
            raise ValidationException(f'No groups found. Invalid file.')
        for key, val in parsed_dict.items():
            if not val:
                raise ValidationException(f'Group {key} has no children, invalid file.')
    except ValidationException as e:
        inventory.error_info = str(e)
        inventory.passed = False

    return parsed_dict


def check_regex_validity(regex):
    """
    :param regex: String --> Regex to test
    :return: Boolean
    """
    try:
        re.compile(regex)
    except re.error:
        logging.error(f'Regex passed is invalid! {regex} Exiting.')
        raise re.error(f'Regex passed is invalid! {regex}')
    return True


def check_inventory_validity(inventory, regex):
    """
    :param inventory: Inventory Object --> Dictionary representation of an Inventory
    :param regex: String --> A Regex Pattern
    :return: Boolean
    """
    unallowed_symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ';', ':', ',', '?', '/', '\\', '=', '+', '<', '>']
    inventory_file = inventory.parsed_dict
    try:
        r = re.compile(regex)
        values_list = []
        for key, val in inventory_file.items():
            # check if key is not a special key
            if ':children' not in key and ':vars' not in key:
                for value in val:
                    if any([True if symbol in value else False for symbol in unallowed_symbols]):
                        raise ValidationException(f'Un-allowed symbol in "{value}" - {unallowed_symbols}')
                values_list.extend(val)
            # check for broken values such as group:lalala
            elif not any([re.match('.*:children$', key), re.match('.*:vars$', key)]):
                raise ColonValidationException(f'Group {key}, not allowed.')
        # run regex over list and compare list lengths, if there's a difference, raise an error.
        regexed_list = list(filter(r.match, values_list))
        if len(regexed_list) != len(values_list):
            non_regexed = set(values_list) ^ set(regexed_list)
            raise ValidationException(f'Failed verifying the inventory against regex {regex}! Problem with: {non_regexed}')
    except (ValidationException, ColonValidationException) as e:
        inventory.error_info = str(e)
        inventory.passed = False
        return False
    return True


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
    logging.error(f"Path {path} doesn't exist! please enter a valid path.")
    raise FileNotFoundError(f"Path {path} doesn't exist! please enter a valid path.")


def main():
    # initialize logger, argparse, add arguments & parse
    logging.basicConfig(filename='ansible_inventory_validator.log',filemode='w', encoding='utf-8' ,level=logging.DEBUG, format='%(asctime)s %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='path to config file or folder', required=True, type=str)
    parser.add_argument('--regex',type=str,
                        help='Regex to apply on all groups which are not children or vars. By default works by:'
                             '^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$',
                        default='^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$')
    args = parser.parse_args()
    # validate args
    logging.info(f'Received Path: {args.path} Regex: {args.regex}')
    check_regex_validity(args.regex)
    logging.info('Passed regex validity.')
    path_type = check_path(args.path)
    logging.info('passed path check')
    if path_type == 'file':
        # parse inventory
        inventory = Inventory(args.path)
        inventory.parsed_dict = read_inventory(inventory)
        if inventory.passed and check_inventory_validity(inventory, args.regex):
            print(f'Inventory {args.path} passed!')
        else:
            print(f'Inventory {inventory.path} did not pass. {inventory.error_info}')
    else:
        inventory_files = []
        # iterate over files in path and parse them as ansible Inventory files
        for path, dirs, files in os.walk(args.path):
            for file in files:
                file = os.path.join(path,file)
                # parse inventory
                inventory = Inventory(file)
                inventory.parsed_dict = read_inventory(inventory)
                check_inventory_validity(inventory, args.regex)
                inventory_files.append(inventory)
        # print out if inventory passed or not and
        for inv in inventory_files:
            if not inv.passed:
                logging.warning(inv)
            else:
                logging.info(inv)
            print(inv)
    sys.exit(0)


if __name__ == '__main__':
    main()
