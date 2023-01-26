  # Ansible INI Inventory Validator
  ## Prerequisites
  - Python 3.10
  ## Description:
  The Ansible INI Inventory Validator lets you make sure that the inventory is up to standard using your own regex and linting rules.
  You can use the default linting rules, add, or use your own linting rules. The linting rules are based on regex and are separated to 4 different categories:
  - general-all: apply regex to the entire inventory as 1 big string
  - general-line: apply regex to each line in the inventory
  - group: apply regex to each group name in the inventory (not including var groups)
  - host: apply regex to each host in the inventory
  
  If you don't want to specify your own regex, the default regex of ^[a-zA-Z]*-[a-zA-Z0-9]*-[\[]?[0-9]{2}[:]?[0-9]{0,2}[\]]?\.[a-zA-Z0-9-]*\.[a-zA-Z]*[\s]*$ will be applied.
  This makes sure your hosts are up to standard in the following format:
  #### EXAMPLE 1:
  - prefix-servername-01.domain.com
  - ...
  - ...
  - prefix-servername-99.domain.com
  
  #### EXAMPLE 2:
  - prefix-servername-[01-99].domain.com
  
  
  You can validate a directory with inventories or 1 inventory by itself.
  The program won't pause on each failed file, but instead will tell you the errors found in each file at the end of the process.
  Please note that general-all will only show the first error it found per linting rule.
  Feel free to use the fail inventories under the inventories folder for testing.
  ## Parameters
  * **--path** <path_to_folder/path_to_file>  
  Description: Specify a path to either a folder (which contains inventories) or an inventory file.  
  Required: True

  * **--regex** <regex to apply>  
  Description: pass a valid regex to apply on your hostnames.
  Required: False
  
  * **--exclude-invs** <inventories,comma,seperated>  
  Description: specify which inventories to exclude  
  Required: False
  
  * **--exclude** <rulenum,comma,separated>  
  Description: specify which lint rules to exclude by their number (E.G. 400,200, etc..)  
  Required: False
  
  * **--no-regex**  
  Description: a flag to specify not to use the default regex for hosts or your own.  
  Required: False
  

  ## Examples:
  
  Folder structure:
  ``` bash
  └── etc
      └── ansible
          └── inventory
              ├── all_servers.ini
              ├── database_servers.ini
              └── web_servers.ini
  ```
  
  `basic usage on folder / specific inventory`:
  - ansible_inventory_validator.py --path /etc/ansible/inventory/
  - ansible_inventory_validator.py --path /etc/ansible/inventory/all_servers.ini
  
  `validate a specific inventory / folder with inventories with your own regex`
  - ansible_inventory_validator.py --path /etc/ansible/inventory/ --regex [0-9]{2}-[a-zA-Z]*\.com
  - ansible_inventory_validator.py --path /etc/ansible/inventory/all_servers.ini --regex [0-9]{2}-[a-zA-Z]*\.com
  
  `disable default/user regex linting`
  - ansible_inventory_validator.py --path /etc/ansible/inventory/ --no-regex
  
  `pass inventories to exclude`
  - ansible_inventory_validator.py --path /etc/ansible/inventory/ --exclude-invs databse_servers.ini,web_servers.ini
  
  `pass lint rules to exclude`
  - ansible_inventory_validator.py --path /etc/ansible/inventory/ --exclude 200,201,400
  
  
  
