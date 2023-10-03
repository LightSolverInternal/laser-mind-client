import getpass
import subprocess
from laser_mind_client import LaserMind

print("This is a setup script for the laser-mind-client")

ls_user = input("Username:")
ls_pass = getpass.getpass("Password:")

try:
    lsClient = LaserMind(ls_user, ls_pass)
except Exception as ex:
    print("Error logging-in to the LightSolver cloud, could be due to wrong credentials.")
    print("Setup incomplete.")
    exit(1)

print("Setting environment variables")

try:
    subprocess.call(['powershell.exe', '-Command', f'[Environment]::SetEnvironmentVariable("LS_USER", "{ls_user}", "User")'])
    subprocess.call(['powershell.exe', '-Command', f'[Environment]::SetEnvironmentVariable("LS_PASS", "{ls_pass}", "User")'])
except Exception as ex:
    print("Error updating environment variables, please verify that you are running as administrator")
    print("Setup incomplete.")
    exit(1)

print("Setup Complete")