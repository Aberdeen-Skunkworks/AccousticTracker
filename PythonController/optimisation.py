import math
import scipy

# Mean Square Error
# guess = [x, y, z]
# list of locations = [[x, y, z], [x, y, z].....
# distances_mesured = [d1, d2, d3..... these are the distances from point to location l1, l2 so on in order

def distance_on_sphere(location, point):
    import math
    distance = math.sqrt( (location[0]-point[0])**2 + (location[1]-point[1])**2 + (location[2]-point[2])**2 )
    return distance

def mse(x, locations, distances_mesured): # x = point in 3D space [x, y, z]
    mse = 0.0
    distances = []
    for i in range(len(locations)):
        distances.append(distance_on_sphere(locations[i], x))
        
    for errors in range(len(locations)):
        mse += math.pow(distances_mesured[errors] - distances[errors], 2.0)
    return mse / len(locations)




guess = [0,5,0]
locations = [[0,0,0],[10,0,0],[0,10,0]]
distances_mesured = [7.0710678118654755, 7.0710678118654755,7.0710678118654755]




# initial_location: (x, y, z)

result = scipy.optimize.minimize(
	mse,                         # The error function
	guess,            # The initial guess
	args=(locations, distances_mesured), # Additional parameters for mse
	method='L-BFGS-B',           # The optimisation algorithm
	options={
		'ftol':1e-5,         # Tolerance
		'maxiter': 1e+7      # Maximum iterations
	})
location = result.x

print(location)