import sys
import random
import copy
import timeit
import heapq

if(len(sys.argv) !=2):
	print("USAGE: csp.py input_file")
	sys.exit()

start_time = timeit.default_timer()

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
for y in range(grid_height):
	variables[y] = [None]*grid_width
	sources[y] = [False]*grid_width

colors = {}

for y in range(grid_height):
	for x in range(grid_width):
		char = text[y][x]
		if(char != '_'):
			variables[y][x] = char
			sources[y][x] = True
			colors[char] = 0

color_list = colors.keys()
'''
for y in range(grid_height):
	domains[y] = [None]*grid_width
	for x in range(grid_width):
		if(not sources[y][x]):
			domains[y][x] = dict(colors)

for y in range(grid_height):
	for x in range(grid_width):
		if(sources[y][x]):
			value = variables[y][x]
			for i, j in neighbor_dir:
				n_x = x + i
				n_y = y + j
				if(inBounds(n_x,n_y)):
					domains[n_y][n_x][value] = domains[n_y][n_x][value] + 2'''

def inBounds(x, y):
	if(x >= 0 and y >= 0 and x < grid_width and y < grid_height):
		return True
	else:
		return False

def initDomains():
	domains = [None]*grid_height

	for y in range(grid_height):
		domains[y] = [None]*grid_width
		for x in range(grid_width):
			if(not sources[y][x]):
				domains[y][x] = dict(colors)

	for y in range(grid_height):
		for x in range(grid_width):
			if(sources[y][x]):
				value = variables[y][x]
				for i, j in neighbor_dir:
					n_x = x + i
					n_y = y + j
					if(inBounds(n_x,n_y) and domains[n_y][n_x] is not None):
						domains[n_y][n_x][value] = domains[n_y][n_x][value] + 2

	return domains


def isComplete(variables):
	for y in range(grid_height):
		for x in range(grid_width):
			if(variables[y][x] is None):
				return False
	return True

def calcVariableWeight(variables, x, y):
	weight = 0
	for i, j in neighbor_dir:
		n_x = x + i
		n_y = y + j
		if(inBounds(n_x, n_y) and variables[n_y][n_x] is not None):
			if(sources[n_y][n_x]):
				weight = weight + 2
			else:
				weight = weight + 1
	return weight

def getVariableOrder(variables):
	
	# Initialize unassigned variable list
	var_order = []
	for y in range(grid_height):
		for x in range(grid_width):
			if(variables[y][x] is None):
				if(isSmart):
					weight = calcVariableWeight(variables, x, y)
					var_order.append((weight, (x,y)))
				else:
					var_order.append((x, y))
	var_order.sort()

	return var_order

def calcValueWeight(variables, domains, x, y):
	c = dict(colors)

	'''for i, j in neighbor_dir:
		n_x = x + i 
		n_y = y + j

		if(inBounds(n_x, n_y)):
			n_color = variables[n_y][n_x]
			if(n_color is not None):
				if(sources[n_y][n_x]):
					c[n_color] = c[n_color] + 2
				else:
					c[n_color] = c[n_color] + 1
'''
	weights = []
	w = []
	for key, value in domains[y][x].items():
		weights.append((value, key))
	weights.sort()
	for value, key in weights:
		w.insert(0, key)

	return w

def updateDomainRanking(variables, domains, x, y):
	value = variables[y][x]
	for i, j in neighbor_dir:
		n_x = x + i 
		n_y = y + j

		if(inBounds(n_x, n_y)):
			n_value = variables[n_y][n_x]
			if(n_value is None):
				if(value in domains[n_y][n_x]):
					domains[n_y][n_x][value] = domains[n_y][n_x][value] + 1
			

def getValuesByPriority(variables, domains, x, y):
	
	if(isSmart):
		priorities = calcValueWeight(variables, domains, x, y)
	else:
		priorities = list(color_list)
		random.shuffle(priorities)
	return priorities

def adjustNearbyDomains(variables, domains, x, y):

	value = variables[y][x]

	# Remove value from neighboring domains
	for i, j in neighbor_dir:
		n_x = x + i
		n_y = y + j

		if(inBounds(n_x, n_y) and variables[n_y][n_x] is None):
			try:
				del domains[n_y][n_x][value]
			except(KeyError):
				pass
			# Check if a domain was emptied
			if(not domains[n_y][n_x]):
				return True

def constraintsAreViolated(variables, domains, x, y):
	# Check bounds
	if(not inBounds(x, y)):
		return False
		
	value = variables[y][x]

	# Check for unassigned variable
	if(value is None):
		neighbor_colors = {}

		# Check if surrounding colors are all different
		for i, j in neighbor_dir:
			n_x = x+i
			n_y = y+j

			# Check bounds
			if(inBounds(n_x, n_y)):
				color = variables[n_y][n_x]
				if(color is None):
					return False
				if(color in neighbor_colors):
					return False
				else:
					neighbor_colors[color] = True

		return True

	# Clear domain for this variable
	domains[y][x] = None

	# Records number of different and same colors nearby
	num_diff = 0
	num_same = 0

	# Cycle through neighbors
	for i, j in neighbor_dir:
		n_x = x+i
		n_y = y+j

		# Check bounds
		if(inBounds(n_x, n_y)):
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
		elif(num_same == 1):
			return adjustNearbyDomains(variables, domains, x, y)
	elif(num_diff > 2 or num_same > 2):
		return True
	elif(num_same == 2):
		return adjustNearbyDomains(variables, domains, x, y)

	return False

def validAssignment(variables, domains, x, y):
	# Check assigned variable's constraints
	if(constraintsAreViolated(variables, domains, x, y)):
		return False

	# Check neighbors' constraints
	for i, j in neighbor_dir:
		if(constraintsAreViolated(variables, domains, x+i, y+j)):
			return False

	return True

def updateVariableOrder(variables, var_order, x, y):

	for i, j in neighbor_dir:
		n_x = x + i
		n_y = y + j

		#print("Nx: "+str(n_x)+" Ny: "+str(n_y))
		if(inBounds(n_x, n_y)):
			if(variables[n_y][n_x] is None):
				index = 0
				#print(str(var_order))
				while index < len(var_order) and var_order[index][1] != (n_x,n_y):
					#print("Ix: "+str(n_x)+" Iy: "+str(n_y))
					index = index + 1
				if(index < len(var_order)):
					weight = var_order[index][0]
					var_order[index] = (weight+1, (n_x,n_y))

	var_order.sort()

# Search function
def backtrackingSearch(variables, domains, attempts, var_order = None):

	# Check if assignment is complete
	if(isComplete(variables)):
		return True

	if(var_order is None):
		var_order = getVariableOrder(variables)
		#print(str(var_order))

	# Get the next variable to be assigned
	if(isSmart):
		x, y = var_order.pop()[1]
	else:
		index = random.randint(0, len(var_order)-1)
		x, y = var_order.pop(index)
	
	# Get values by priority
	value_list = getValuesByPriority(variables, domains, x, y)

	# Prepare for assignment
	updateVariableOrder(variables, var_order, x, y)
#	updateDomainRanking(variables, domains, x, y)

	# Cycle through values
	for value in value_list:
		# Assign value
		variables[y][x] = value

		new_domains = [None]*grid_height
		for j in range(grid_height):
			new_domains[j] = [None]*grid_width
			for i in range(grid_width):
				if(domains[j][i] is not None):
					new_domains[j][i] = dict(domains[j][i])

		# Check if assignment is valid
		if(validAssignment(variables, new_domains, x, y)):
			attempts[0] = attempts[0] + 1
			updateDomainRanking(variables, new_domains, x, y)

			'''print("Attempted Assignments: " + str(attempts[0]))

			for line in variables:
				for c in line:
					if(c is not None):
						sys.stdout.write(c)
					else:
						sys.stdout.write(' ')
				sys.stdout.write('\n')
			input()'''

			# Recurse
			if(backtrackingSearch(variables, new_domains, attempts, list(var_order))):
				return True

	# Undo assignment
	variables[y][x] = None
	return False


# Directions of neighboring spaces
neighbor_dir = [(0,1),(0,-1),(1,0),(-1,0)]
attempts = [0]

domains = initDomains()

isSmart = True
backtrackingSearch(variables, domains, attempts)

endtime = timeit.default_timer() - start_time

print("Time: " + str(endtime) + " seconds")
print("Attempted Assignments: " + str(attempts[0]))

for line in variables:
	for c in line:
		if(c is not None):
			sys.stdout.write(c)
		else:
			sys.stdout.write(' ')
	sys.stdout.write('\n')
