from ansible_inventory_validator import read_inventory,\
    check_path,\
    check_inventory_validity,\
    check_regex_validity,\
    Inventory

def test_valid_read_inventory():
    inventory = Inventory('inventories/test.ini')
    assert read_inventory(inventory) == {'isrl_group_1': ['isrl-servername-01.domain.com', 'isrl-servername-02.domain.com'], 'isrl_group_2': ['isrl-servername-03.domain.com', 'isrl-servername-04.domain.com'], 'isrl:children': ['isrl_group_1', 'isrl_group_2'], 'isrl:vars': ["test={'123'}"]}

def test_valid_check_path():
    assert check_path('inventories/test.ini') == 'file'
    assert check_path('inventories') == 'folder'

def test_valid_check_inventory_validity():
    inventory = Inventory('inventories/test.ini')
    regex = '^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$'
    inventory.parsed_dict = read_inventory(inventory)
    assert check_inventory_validity(inventory,regex)

def test_valid_check_regex_validity():
    assert check_regex_validity('^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$')
    assert check_regex_validity('1234')

def test_error_notfound_read_inventory():
    pass

def test_error_validationerror_read_inventory():
    pass

def test_error_check_path():
    pass

def test_error_validationerror_check_inventory_validity():
    pass

def test_error_colonvalidationerror_check_inventory_validity():
    pass

def test_error_regex_validity():
    pass