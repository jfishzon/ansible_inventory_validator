from pytest import raises
import re
from ansible_inventory_validator import read_inventory,\
    check_path,\
    check_inventory_validity,\
    check_regex_validity,\
    Inventory

def test_valid_read_inventory():
    inventory = Inventory('inventories/valid.ini')
    assert read_inventory(inventory) == {'isrl_group_1': ['isrl-servername-01.domain.com', 'isrl-servername-02.domain.com'], 'isrl_group_2': ['isrl-servername-03.domain.com', 'isrl-servername-04.domain.com'], 'isrl:children': ['isrl_group_1', 'isrl_group_2'], 'isrl:vars': ["test={'123'}"]}

def test_valid_check_path():
    assert check_path('inventories/valid.ini') == 'file'
    assert check_path('inventories') == 'folder'

def test_valid_check_inventory_validity():
    inventory = Inventory('inventories/valid.ini')
    regex = '^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$'
    inventory.parsed_dict = read_inventory(inventory)
    assert check_inventory_validity(inventory,regex)


def test_valid_check_regex_validity():
    assert check_regex_validity('^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$')
    assert check_regex_validity('1234')


def test_error_check_path():
    with raises(FileNotFoundError):
        check_path('inventories/test.yaml')


def test_error_regex_validity():
    with raises(re.error):
        check_regex_validity("\\1")
