  # Ansible INI Inventory Validator
  ### Prerequisites
  - Python 3.10
  #### Video Demo:  [https://youtu.be/qM3X74onAuQ](https://youtu.be/qM3X74onAuQ)
  #### Description:
  The Ansible INI Inventory Validator lets you make sure that the inventory is up to standard using your own regex.
  If you don't want to specify your own regex, the default regex of ^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$ will be applied.
  This makes sure your hosts are up to standard in the following format:
  - prefix-servername-01.domain.com
  - ...
  - ...
  - prefix-servername-99.domain.com
  
  You can validate a directory with inventories or 1 inventory by itself.
  The program won't pause on each failed file, but instead will tell you the first error found in each file at the end of the process.
  Feel free to use the fail inventories under the inventories folder for testing.
  ##### Parameters
  * --path <path_to_folder/path_to_file>
  Description: Specify a path to either a folder (which contains inventories) or an inventory file.
  Required: True

  * --regex <Regex to apply>
  Description: pass a valid regex to apply on your hostnames.
  Default: ^[a-zA-Z]*-[a-zA-Z]*-[0-9]{2}\.[a-zA-Z]*\.[a-zA-Z]*$
  Required: False

  ##### Examples:
  - ansible_inventory_validator.py --path /etc/ansible/inventory/all_servers.ini --regex [0-9]{2}-[a-zA-Z]*\.com
  - ansible_inventory_validator.py --path /etc/ansible/inventory/ --regex [0-9]{2}-[a-zA-Z]*\.com
  - ansible_inventory_validator.py --path /etc/ansible/inventory/
