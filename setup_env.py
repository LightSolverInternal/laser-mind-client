import getpass
import platform
import subprocess
import os
from laser_mind_client import LaserMind

print("This is a setup script for the laser-mind-client")

ls_user = input("Email: ")
ls_pass = getpass.getpass("Password: ")

try:
    lsClient = LaserMind(ls_user, ls_pass)
except Exception as ex:
    print("Error logging-in to the LightSolver cloud, could be due to wrong credentials.")
    print("Setup incomplete.")
    exit(1)

print("Setting environment variables")

try:
    # Change temporarily so user doens't have to respawn the terminal
    os.environ["LS_USER"] = ls_user
    os.environ["LS_PASS"] = ls_pass

    # Permanently set for future terminal sessions, per platform
    if platform.system() == "Windows":
        subprocess.call(['powershell.exe', '-Command', f'[Environment]::SetEnvironmentVariable("LS_USER", "{ls_user}", "User")'])
        subprocess.call(['powershell.exe', '-Command', f'[Environment]::SetEnvironmentVariable("LS_PASS", "{ls_pass}", "User")'])
    else:
        profile_path = os.path.expanduser("~/.bash_profile")
        with open(profile_path, 'a') as profile_file:
            profile_file.write(f'\nexport LS_USER="{ls_user}"\n')
            profile_file.write(f'export LS_PASS="{ls_pass}"\n')

except Exception as ex:
    print("Error updating environment variables, please verify that you are running as administrator")
    print("Setup incomplete.")
    exit(1)

print("Setup Complete")