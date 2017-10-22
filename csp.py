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

# Directions of neighboring spaces
	neighbor_dir = [(0,1),(0,-1),(1,0),(-1,0)]

# Defines the state representation
class State:
	def __init__(self, variables, domains):
		self.variables = variables
		self.domains = domains
		self.calculateUnassigned()

	def calculateUnassigned():
		self.unassignedVars = []
		for y in range(grid_height):
			for x in range(grid_width):
				if(self.variables[y][x] is None):
					self.unassignedVars.append((x,y))

	def isComplete(self):
		return not self.unassignedVars

	def getNextVariable(self):
		return self.unassignedVars(randint(0, len(self.unassignedVars)-1))

	def areConstraintsViolated(x, y):
		# Check bounds
		if(x < 0 or y < 0 or x >= grid_width or y >= grid_height):
			return False
		
		value = self.variables[y][x]

		# Check for unassigned varaible
		if(value is None):
			return False

		# Records number of different and same colors nearby
		num_diff = 0
		num_same = 0

		# Cycle through neighbors
		for i, j in neighbor_dir:
			n_x = x+i
			n_y = y+j

			# Check bounds
			if(n_x >= 0 and n_y >= 0 and n_x < grid_width and n_y < grid_height):
				neighbor_value = self.variables[n_y][n_x]

				if(neighbor_value is not None):
					if(neighbor_value != value):
						num_diff = num_diff + 1
					else:
						num_same = num_same + 1

		if(sources[y][x]):
			if(num_diff > 3 or num_same > 1):
				return True
		elif(num_diff > 2 or num_same > 2):
			return True

		return False

	def adjustDomains(domains, x, y):
		# Check bounds
		if(x < 0 or y < 0 or x >= grid_width or y >= grid_height):
			return

		

	def assignValue(x, y, value):
		if(self.variables[y][x] is not None):
			print("Variable at position " + str(x) + ", " + str(y) + " already asigned.")
			return None

		self.variables[y][x] = value

		for i, j in neighbor_dir:
			n_x = x + i
			n_y = y + j

			if(self.areConstraintsViolated(n_x, n_y)):
				self.variables[y][x] = None
				return None

		new_variables = copy.deepcopy(self.variables)
		new_domains = copy.deepcopy(self.domains)

		self.variables[y][x] = None

		new_domains[y][x] = None

		for i, j in neighbor_dir:
			n_x = x + i
			n_y = y + j			

			self.adjustDomains(new_domains, n_x, n_y)

		return State(new_variables, new_domains)


# Initialize stack
stack = [State(variables, domains)]
solution = None

# Begin the search
while stack:
	# Pop next assignment from stack
	current_state = stack.pop()
	variables = current_state.variables
	domains = current_state.domains

	# Check if assignment is complete
	if(current_state.isComplete()):
		solution = variables
		break

	# Get the next variable to be assigned
	next_x, next_y = current_state.getNextVariable()

	successor_list = []

	# Cycle through possible values
	for value in domains[next_y][next_x]:
		successor = current_state.assignValue(x, y, value)

		if(successor is not None):
			successor_list.append(successor)

	# Add successor states to stack
	stack.extend(successor_list)


'''
for line in sources:
	for b in line:
		if(b):
			sys.stdout.write('T')
		else:
			sys.stdout.write('F')
	sys.stdout.write('\n')
'''

