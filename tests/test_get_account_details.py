####################################################################################################
# This example connects to the LightSolver Cloud using the LaserMind client and retrieves account details.
# The `get_account_details` method fetches information such as username, spin limit, expiration date, and credits.
####################################################################################################

from laser_mind_client import LaserMind

# Enter your TOKEN here
user_token = "<TOKEN>"

# Connect to the LightSolver Cloud
lsClient = LaserMind(user_token=user_token)

res = lsClient.get_account_details()

assert 'username' in res
assert 'dlpu_spin_limit' in res
assert 'expiration_date' in res
assert 'dlpu_credit_seconds' in res

print(f"Test PASSED, response is: \n{res}")