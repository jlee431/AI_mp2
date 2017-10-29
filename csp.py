import sys
import random
import timeit
import math
from imageio import *
import numpy as np

# Print USAGE information
if(len(sys.argv) !=2):
	print("USAGE: csp.py input_file")
	sys.exit()

# Record start time
start_time = timeit.default_timer()

# Seed random number generator
random.seed(start_time)

# Open input file
csp_file = open(sys.argv[1], 'r')
text = []

# Parse text file
for line in csp_file:
	line_list = list(line)
	if(line_list[-1] == '\n'):
		line_list.pop()
	text.append(line_list)

# Set grid dimensions
grid_height = len(text)
grid_width = len(text[0])

# Initialize 2D arrays (Row major order)
variables = [None]*grid_height    # 2D list of variable assignments
sources = [None]*grid_height      # 2D list indicating source locations
for y in range(grid_height):
	variables[y] = [None]*grid_width
	sources[y] = [False]*grid_width

colors = {}    # Dictionary of colors in input file

for y in range(grid_height):
	for x in range(grid_width):
		char = text[y][x]
		if(char != '_'):
			variables[y][x] = char
			sources[y][x] = True
			colors[char] = 0

color_list = colors.keys()    # All colors in list form

# Returns True if the (x, y) pair is in bounds
def inBounds(x, y):
	return (x >= 0 and y >= 0 and x < grid_width and y < grid_height)

# Initializes the domains for each unassigned variable
def initDomains():
	domains = [None]*grid_height

	# Default domain for each variable is dictionary of each color
	for y in range(grid_height):
		domains[y] = [None]*grid_width
		for x in range(grid_width):
			if(not sources[y][x]):
				domains[y][x] = dict(colors)

	# Assign the weights to the colors in the domain of each variable
	for y in range(grid_height):
		for x in range(grid_width):
			if(sources[y][x]):
				value = variables[y][x]

				# Check neighbors for any sources
				for i, j in neighbor_dir:
					n_x = x + i
					n_y = y + j

					# Neighboring sources add 2 to the weight of the source's color
					if(inBounds(n_x,n_y) and domains[n_y][n_x] is not None):
						domains[n_y][n_x][value] = domains[n_y][n_x][value] + 2

	return domains

# Checks if the assignment is complete
def isComplete(variables):
	for y in range(grid_height):
		for x in range(grid_width):
			if(variables[y][x] is None):
				return False
	return True

# Calculates the weight of variable at (x, y) based on its possible values 
def calcVariableWeight(variables, domains, x, y):
	# Variable weight equal to number of possible assignments
	return len(domains[y][x])

# Creates the initial variable order
def getVariableOrder(variables, domains):
	
	# Initialize unassigned variable list
	var_order = []
	for y in range(grid_height):
		for x in range(grid_width):
			if(variables[y][x] is None):

				if(isSmart):
					# Smart solver uses wieghts to sort variables
					weight = calcVariableWeight(variables, domains, x, y)
					var_order.append((weight, (x,y)))
				else:
					var_order.append((x, y))
	
	# Sort variable order. No effect on dumb solver
	var_order.sort()

	return var_order

# Returns list of values for variable at (x, y) sorted by their priority
def calcValueWeight(variables, domains, x, y):

	# Lists for computation
	weights = []
	w = []

	# Sort domain by wieghts
	for key, value in domains[y][x].items():
		weights.append((value, key))
	weights.sort()

	# Create create list of colors (keys) sorted by weight
	for value, key in weights:
		w.insert(0, key)

	return w

# Update the domains of varaibles around variable at (x, y)
def updateDomainRanking(variables, domains, x, y):
	# Get color of variable at (x, y)
	value = variables[y][x]

	# Cycle through neighbors
	for i, j in neighbor_dir:
		n_x = x + i 
		n_y = y + j

		if(inBounds(n_x, n_y)):
			# Get neighbor value
			n_value = variables[n_y][n_x]

			# if neighbor is unassigned
			if(n_value is None):
				# Update the weight of color at (x, y) in neighbor's domain
				if(value in domains[n_y][n_x]):
					domains[n_y][n_x][value] = domains[n_y][n_x][value] + 1
			
# Returns list of colors sorted by priority
def getValuesByPriority(variables, domains, x, y):
	
	if(isSmart):
		# Smart solver returns sorted list
		priorities = calcValueWeight(variables, domains, x, y)
	else:
		# Dumb solver uses random order
		priorities = list(color_list)
		random.shuffle(priorities)

	return priorities

# Removes color of variable at (x, y) from neighboring domains
def adjustNearbyDomains(variables, domains, x, y):

	value = variables[y][x]

	# Remove value each neighbor's domain
	for i, j in neighbor_dir:
		n_x = x + i
		n_y = y + j

		# Check if neighbor is unassigned
		if(inBounds(n_x, n_y) and variables[n_y][n_x] is None):
			# Remove color if it is in this neighbor's domain
			try:
				del domains[n_y][n_x][value]
			except(KeyError):
				pass

			# Check if a domain was emptied
			if(not domains[n_y][n_x]):
				# True value indicates assignment is invalid
				return True

	# Assignment is still valid 
	return False

# Check if the constraints are violated for variable (x, y)
def constraintsAreViolated(variables, domains, x, y):
	# Check bounds
	if(not inBounds(x, y)):
		return False
	
	# Get value of variable (x, y)
	value = variables[y][x]

	# Check if unassigned
	if(value is None):
		# Dictionary of neighboring colors
		neighbor_colors = {}

		# Check if surrounding colors are all different
		for i, j in neighbor_dir:
			n_x = x+i
			n_y = y+j

			# Check bounds
			if(inBounds(n_x, n_y)):
				color = variables[n_y][n_x]

				# If neighbor unassigned, a solution is still possible
				if(color is None):
					return False

				# If two neighbors have same color, a solution is still possible
				if(color in neighbor_colors):
					return False

				# Add this color to the dictionary
				else:
					neighbor_colors[color] = True

		# At this point, all neighbors have different colors
		# The constraints have been violated, no assignment exists for (x, y)
		return True

	# The variable has a color
	# Clear domain for this variable
	domains[y][x] = None

	num_diff = 0    # Number of different neighboring colors 
	num_same = 0    # Number of matching neighboring colors

	# Cycle through neighbors
	for i, j in neighbor_dir:
		n_x = x+i
		n_y = y+j

		# Check bounds
		if(inBounds(n_x, n_y)):
			neighbor_value = variables[n_y][n_x]

			# Check if neighbor has color
			if(neighbor_value is not None):
				# increment appropriate counter
				if(neighbor_value != value):
					num_diff = num_diff + 1
				else:
					num_same = num_same + 1
		else:
			# Spaces out of bounds counted as different colors
			num_diff = num_diff + 1

	# Check if variable (x, y) is a source
	if(sources[y][x]):
		# Check if constraints are violated
		if(num_diff > 3 or num_same > 1):
			return True
		elif(num_same == 1):
			# If this variable has its constraints satisfied, adjust neighboring domains
			return adjustNearbyDomains(variables, domains, x, y)
	# For non-sources, check constraints
	elif(num_diff > 2 or num_same > 2):
		return True
	elif(num_same == 2):
		# If this variable has its constraints satisfied, adjust neighboring domains
		return adjustNearbyDomains(variables, domains, x, y)

	return False

# Checks if assignment to variable at (x, y) is valid
def validAssignment(variables, domains, x, y):
	# Check assigned variable's constraints
	if(constraintsAreViolated(variables, domains, x, y)):
		return False

	# Check neighbors' constraints
	for i, j in neighbor_dir:
		if(constraintsAreViolated(variables, domains, x+i, y+j)):
			return False

	return True

# Update the order of remaining unassigned variables after assignment to variable at (x, y)
def updateVariableOrder(variables, domains, var_order, x, y):

	# Cycle through neighbors
	for i, j in neighbor_dir:
		n_x = x + i
		n_y = y + j

		if(inBounds(n_x, n_y)):
			# Check if neighbor is unassigned
			if(variables[n_y][n_x] is None):

				index = 0
				
				# Find index of neighbor in variable order
				while index < len(var_order) and var_order[index][1] != (n_x,n_y):
					index = index + 1
				
				if(index < len(var_order)):
					# Assign new weight to neighbor
					var_order[index] = (len(domains[n_y][n_x]), (n_x,n_y))

	# Sort variables by new weights
	var_order.sort()

# Search function
def backtrackingSearch(variables, domains, attempts, var_order = None):

	# Check if assignment is complete
	if(isComplete(variables)):
		return True

	# Check if an order for variables exists
	if(var_order is None):
		# Initialize order
		var_order = getVariableOrder(variables, domains)

	# Get the next variable to be assigned
	if(isSmart):
		# Order is sorted already
		x, y = var_order.pop(0)[1]
	else:
		# Dumb solver choses random variable
		index = random.randint(0, len(var_order)-1)
		x, y = var_order.pop(index)
	
	# Get values by priority
	value_list = getValuesByPriority(variables, domains, x, y)

	# Prepare for assignment by updating varible order
	updateVariableOrder(variables, domains, var_order, x, y)

	# Cycle through possible values
	for value in value_list:
		# Test value assignment
		variables[y][x] = value

		# Create copy of domains for next level
		new_domains = [None]*grid_height
		for j in range(grid_height):
			new_domains[j] = [None]*grid_width
			for i in range(grid_width):
				if(domains[j][i] is not None):
					new_domains[j][i] = dict(domains[j][i])

		# Check if assignment is valid
		if(validAssignment(variables, new_domains, x, y)):
			# Commit to assignment
			attempts[0] = attempts[0] + 1

			# Update order of colors in domains
			updateDomainRanking(variables, new_domains, x, y)

			# Recurse
			if(backtrackingSearch(variables, new_domains, attempts, list(var_order))):
				# Solution found, return True
				return True

	# No valid assignment found, undo assignment
	variables[y][x] = None

	# Return that search failed 
	return False

# Color references for solution image creation
color_references = [[255,0,0], [0,255,0], [0,0,255], [255,255,0], [255,0,255],
					[0,255,255], [255,102,102], [153,255,153], [153,255,255],
					[255,153,255], [102,0,51], [255,128,0], [0,153,153],
					[102,51,0], [102,0,102], [128,128,128], [255,255,255]]

# Draws image of soultion and saves to filename
def drawSolution(filename, solution):
	square_size = 64      # Length in pixels of the side of one grid square
	source_radius = 28    # Radius of source nodes
	pipe_width = 28       # Width of pipes

	# 3D array representing image
	# Two dimensions for position, one for RGB value
	image = np.zeros((grid_height*square_size, grid_width*square_size, 3), dtype=np.uint8)

	next_ref = 0      # Index of next color in color_reference
	color_map = {}    # Maps character to index in color_reference

	# Fill in sources and rounded corners
	for y in range(grid_height):
		for x in range(grid_width):
			# Get value of square
			value = solution[y][x]

			# Check if value has color assignment
			if(value not in color_map):
				# Use next index
				color_map[value] = next_ref
				next_ref = next_ref + 1

			# Lookup RGB value
			color =  color_references[color_map[value]] 

			# Set radius based on sources
			if(sources[y][x]):
				radius = source_radius
			else:
				radius = pipe_width//2

			# Set center position
			center = square_size//2

			# Cycle through pixels in current square
			for i in range(square_size):
				for j in range(square_size):
						# Compute distance from center of square
						i_dist = abs(i - center)
						j_dist = abs(j - center)
						dist = math.sqrt(i_dist ** 2 + j_dist ** 2)

						# Fill in circle
						if(dist < radius):
							image[square_size*y+i][square_size*x+j] = color

	# Fill in pipes
	for y in range(grid_height):
		for x in range(grid_width):
			# Get value of square
			value = solution[y][x]

			# Get color assignment
			color =  color_references[color_map[value]] 

			# Check if neighbor below has matching value
			if(inBounds(x, y+1) and value == solution[y+1][x]):
				# Set starting positions for pipe drawing
				start_x = square_size*x + square_size//2 - pipe_width//2
				start_y = square_size*y + square_size//2

				# Draw pipe from current square to neighbor
				for i in range(square_size):
					for j in range(pipe_width):
						image[start_y + i][start_x + j] = color

			# Check if right neighbor has matching value
			if(inBounds(x+1, y) and value == solution[y][x+1]):
				# Set starting positions for pipe drawing
				start_x = square_size*x + square_size//2
				start_y = square_size*y + square_size//2 - pipe_width//2

				# Draw pipe from current square to neighbor
				for i in range(pipe_width):
					for j in range(square_size):
						image[start_y + i][start_x + j] = color

	# Write image to file
	imwrite(filename, image)


# Directions of neighboring spaces
neighbor_dir = [(0,1),(0,-1),(1,0),(-1,0)]

# Initialize attempts to zero
# Length 1 array so value can be passed as parameter
attempts = [0]

# Initialize domains
domains = initDomains()

# Set whether to use smart or dumb solver
isSmart = False

# Set whether the soultuion should be output
shouldOutput = False

# Perform search
try:
	shouldOutput = backtrackingSearch(variables, domains, attempts)
except KeyboardInterrupt:
	print("Search Interrupted, printing progress at time of interrupt")

# Record time of execution
total_time = timeit.default_timer() - start_time

# Print execution time and number of assignments
print("Time: " + str(total_time) + " seconds")
print("Attempted Assignments: " + str(attempts[0]))

# Print text-based solution
for line in variables:
	for c in line:
		if(c is not None):
			sys.stdout.write(c)
		else:
			sys.stdout.write('_')
	sys.stdout.write('\n')

if(shouldOutput):
	# Initialize filename based on filename of input
	image_filename = "images\soln_" + sys.argv[1][:-4] + ".jpg"

	# Draw the solution
	drawSolution(image_filename, variables)
else:
	print("-No solution found-")
