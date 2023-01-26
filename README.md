  # Ansible INI Inventory Validator
  ## Prerequisites
  - Python 3.10
  ## Description:
  The Ansible INI Inventory Validator lets you make sure that the inventory is up to standard using your own regex and linting rules.
  You can use the default linting rules, add, or use your own linting rules.
  
  If you don't want to specify your own regex, the default regex of:  
  `^[a-zA-Z]*-[a-zA-Z0-9]*-[\[]?[0-9]{2}[:]?[0-9]{0,2}[\]]?\.[a-zA-Z0-9-]*\.[a-zA-Z]*[\s]*$`  
  will be applied.  
  
  This makes sure your hosts are up to standard in the following format:  
  **EXAMPLE 1**
  ``` bash
  prefix-servername-01.domain.com
  ...
  ...
  prefix-servername-99.domain.com
  ```
  **EXAMPLE 2**
  ```bash
  prefix-servername-[01-99].domain.com
  ```
  
  You can validate a directory with inventories or 1 inventory by itself.
  The program won't pause on each failed file, but instead will tell you the errors found in each file at the end of the process.
  Please note that general-all will only show the first error it found per linting rule.
  Feel free to use the fail inventories under the inventories folder for testing.
  ## Parameters
  **--path** <_path_to_folder/path_to_file_>  
  Description: Specify a path to either a folder (which contains inventories) or an inventory file.  
  Required: True

  **--regex** <_regex to apply_>  
  Description: pass a valid regex to apply on your hostnames.  
  Required: False
  
  **--exclude-invs** <_inventories,comma,seperated_>  
  Description: specify which inventories to exclude  
  Required: False
  
  **--exclude** <_rulenum,comma,separated_>  
  Description: specify which lint rules to exclude by their number (E.G. 400,200, etc..)  
  Required: False
  
  **--no-regex**  
  Description: a flag to specify not to use the default regex for hosts or your own.  
  Required: False
  
  ## Adding custom rules
  The linting rules are based on regex and are separated to 4 different categories:
  - general-line: apply regex to each line in the inventory
  - general-all: apply regex to the entire inventory as 1 big string
  - group: apply regex to each group name in the inventory (not including var groups)
  - host: apply regex to each host in the inventory

  When you're adding custom rules, make sure to test them beforehand and add them to the correct rules folder.
  When naming the rule, please make sure to follow the correct naming scheme:
  - general-line: uses numbers between 100 to 199
  - general-all: uses numbers between 200-299
  - group: uses numbers between 300-399
  - host: uses numbers between 400-499

  As well, specify the correct rule level:
  - ERROR: at the end of the program, will exit with error code.
  - WARN: at the end of the program, will exit normally (code 0)
  Therefore, when creating a new rule, make sure not to use the same rule numbers that already exist, and stay within the correct number category, and rule level (error, warn)
  It's also important that the rule name is descriptive of the issue, and utilizes underscores instead of spaces.
  for example, a new general-line rule file name that should raise an error should look like so:   
  `(102)ERROR_SPECIAL_SYMBOL_IN_LINE`   
  and should be placed under rules/general-line
  
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
  
  
  
