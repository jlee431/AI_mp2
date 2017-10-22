import sys
import random
import copy

if(len(sys.argv) !=2):
	print("USAGE: csp.py input_file")
	sys.exit()

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

# Initialize variables
variables = [None]*grid_height
sources = [None]*grid_height
domains = [None]*grid_height
for y in range(grid_height):
	variables[y] = [None]*grid_width
	sources[y] = [False]*grid_width
	domains[y] = [None]*grid_width

colors = {}

for y in range(grid_height):
	for x in range(grid_width):
		char = text[y][x]
		if(char != '_'):
			variables[y][x] = char
			sources[y][x] = True
			colors[char] = True

color_list = colors.keys()

for y in range(grid_height):
	domains[y] = [None]*grid_width
	for x in range(grid_width):
		if(not sources[y][x]):
			domains[y][x] = list(color_list)

def isComplete(variables):
	for y in range(grid_height):
		for x in range(grid_width):
			if(variables[y][x] is None):
				return False
	return True

def getNextVariable(variables):
	var_list = getNextVariable.var_list
	
	# Initialize unassigned variable list
	if(var_list is None):
		var_list = []
		for y in range(grid_height):
			for x in range(grid_width):
				if(variables[y][x] is None):
					var_list.append((x, y))

	# Return next unassigned variable
	index = random.randint(0, len(var_list)-1)
	return var_list.pop(index)
getNextVariable.var_list = None

def getValuesByPriority(variables, x, y):
	priorities = getValuesByPriority.priorities
	if(priorities is None):
		priorities = list(color_list)
		random.shuffle(priorities)
	return priorities
getValuesByPriority.priorities = None

def constraintsAreViolated(variables, x, y):
	# Check bounds
	if(x < 0 or y < 0 or x >= grid_width or y >= grid_height):
		return False
		
	value = variables[y][x]

	# Check for unassigned variable
	if(value is None):
		return False
		neighbor_colors = {}

		# Check if surrounding colors are all different
		for i, j in neighbor_dir:
			n_x = x+i
			n_y = y+j

			# Check bounds
			if(n_x >= 0 and n_y >= 0 and n_x < grid_width and n_y < grid_height):
				color = variables[n_y][n_x]
				if(color is None):
					return False
				if(color in neighbor_colors):
					return False
				else:
					neighbor_colors[color] = True

		return True

	# Records number of different and same colors nearby
	num_diff = 0
	num_same = 0

	# Cycle through neighbors
	for i, j in neighbor_dir:
		n_x = x+i
		n_y = y+j

		# Check bounds
		if(n_x >= 0 and n_y >= 0 and n_x < grid_width and n_y < grid_height):
			neighbor_value = variables[n_y][n_x]

			if(neighbor_value is not None):
				if(neighbor_value != value):
					num_diff = num_diff + 1
				else:
					num_same = num_same + 1
		else:
			num_diff = num_diff + 1

	if(sources[y][x]):
		if(num_diff > 3 or num_same > 1):
			return True
	elif(num_diff > 2 or num_same > 2):
		return True

	return False

def validAssignment(variables, x, y):
	# Check assigned variable's constraints
	if(constraintsAreViolated(variables, x, y)):
		return False

	# Check neighbors' constraints
	for i, j in neighbor_dir:
		if(constraintsAreViolated(variables, x+i, y+j)):
			return False

	return True

# Search function
def backtrackingSearch(variables):

	# Check if assignment is complete
	if(isComplete(variables)):
		return True

	# Get the next variable to be assigned
	next_x, next_y = getNextVariable(variables)

	# Get values by priority
	value_list = getValuesByPriority(variables, x, y)

	# Cycle through values
	for value in value_list:
		# Assign value
		variables[next_y][next_x] = value

		# Check if assignment is valid
		if(validAssignment(variables, next_x, next_y)):
			# Recurse
			if(backtrackingSearch(variables)):
				return True

	# Undo assignment
	variables[next_y][next_x] = None
	return False


# Directions of neighboring spaces
neighbor_dir = [(0,1),(0,-1),(1,0),(-1,0)]

backtrackingSearch(variables)


for line in variables:
	for c in line:
		if(c is not None):
			sys.stdout.write(c)
		else:
			sys.stdout.write(' ')
	sys.stdout.write('\n')


