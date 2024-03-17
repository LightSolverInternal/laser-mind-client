import os
from laser_mind_client import LaserMind

print("This is a Test Environment script for the laser-mind-client")
ls_user = os.getenv('LS_USER')
ls_pass = os.getenv('LS_PASS')
if ls_pass == None or ls_user == None :
    print("Setup Environment incomplete,\n Credentials not defined,\n please deactivate venv and run again setup_env.py ")
    exit(1)
try:
    lsClient = LaserMind(ls_user, ls_pass)
except Exception as ex:
    print("Error logging-in to the LightSolver cloud, could be due to wrong credentials.")
    print("Setup Environment incomplete,\n please deactivate venv and run again setup_env.py ")
    exit(1)

print("Test Environment Complete")