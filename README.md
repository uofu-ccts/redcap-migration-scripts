## Scripts for migrating files/records between redcap instances

It's highly recommended that these scripts be run from inside your VPN/Protected Environment,
on a host that has both Python(3+) and Pip installed, and in a session that won't be closed automatically by the host 

Before running:
1. create a virtual environment 
2. `pip install -r requirements.txt`
3. (optional) Use nohop to redirect progress messages to a file `nohup python move_records.py &`

Note: If only Python v2 is available, remove/refactor the fstrings (or comment out the print commands altogether) from move_records.py