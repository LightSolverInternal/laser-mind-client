from laser_mind_client import LaserMind

# Create a mock QUBO problem
quboListData = [
    [1,1,5],
    [1,2,-6],
    [2,2,3],
    [2,3,-1],
    [3,10,1]]

# Connect to the LightSolver Cloud
lsClient = LaserMind()

res = lsClient.solve_qubo(edgeList=quboListData, timeout=1)

print(res)