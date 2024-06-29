from src.utils.db_utilities import connect
from getpass import getpass
import os
import subprocess


def init_db():
    script_path = os.path.dirname(os.path.realpath(__file__))
    directory = os.fsencode(script_path + "/setup/").decode()
    host = input("Enter DB Hostname: ")
    user = input("Enter DB Administrator Username: ")
    password = getpass("Enter DB Admin Password: ")
    files = os.listdir(directory)
    files.sort()
    for file in files:
        filename = os.fsdecode(file)
        if filename.endswith(".sql"): 
            print(f"Executing {filename}")
            with open(directory + file) as f:
                print([
                        'mysql',
                        '-h', host,
                        '-u', user,
                        f'--password={password}'
                    ])
                x = subprocess.Popen(
                    [
                        'mysql',
                        '-h', host,
                        '-u', user,
                        f'--password={password}'
                    ], stdin=f
                )
                x.communicate()
        else:
            continue

def create_user():
    pass

def main():
    choice = input("Initialize Database [This may wipe all existing data]? "
                   "(y/[n])")
    if choice.lower() == 'y':
        init_db()
    
    choice = input("Create new user? (y/[n])")
    if choice.lower() == 'y':
        create_user()


if __name__ == "__main__":
    main()
