import sys

if(len(sys.argv) !=2):
	print("USAGE: csp.py input_file")
	sys.exit()

csp_file = open(sys.argv[1], 'r')
text = []

variables = []
sources = []
grid_width = 0
grid_height = 0
colors = {}

for line in csp_file:
	line_list = list(line)
	if(line_list[-1] == '\n'):
		line_list.pop()
	text.append(line_list)

for line in text:
	for c in line:
		sys.stdout.write(c)
	sys.stdout.write('\n')
