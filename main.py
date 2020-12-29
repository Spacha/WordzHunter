import time
import argparse
import textwrap
import numpy as np

WORD_FILE = 'lists/words_max16.txt'
CUSTOM_WORD_FILE = 'lists/custom_words.txt'
GRID_SIZE = 4
#WORD_FILE = 'lists/sanat_small_test.txt'
#GRID_SIZE = 3

class Grid:
	def __init__(self, letters):
		self.visited = []
		letters_list = textwrap.wrap(letters, GRID_SIZE)
		self.grid = np.array(letters_list, dtype=str)

	def get_next_neighbor(self, x, y, exclude=[]):
		for dx in [-1, 0, 1]:
			if not (0 <= (x+dx) <= (GRID_SIZE-1)): continue 		# X outside of grid

			for dy in [-1, 0, 1]:
				if not (0 <= (y+dy) <= (GRID_SIZE-1)): continue 	# Y outside of grid
				if (dx == 0 and dy == 0): continue 					# the value itself
				if self.coord_to_key(x+dx,y+dy) in exclude: continue# excluded (done neighbor)

				# found a valid neighbor!
				if not self.is_visited(x+dx,y+dy): 					# not visited
					self.visit_node(x+dx,y+dy)	 					# mark node as visited
					return (self.grid[y+dy][x+dx], x+dx, y+dy)

		return (None, None, None) 									# all neighbors visited

	def visit_node(self, x, y):
		self.visited.append(self.coord_to_key(x,y))

	def is_visited(self, x, y):
		return self.coord_to_key(x,y) in self.visited
	
	def reverse(self):
		self.visited = self.visited[:-1]

	def clear_visited(self):
		self.visited = []

	def get_current_word(self):
		word = ""
		for c in self.visited:
			x,y = self.key_to_coord(c)
			word += self.grid[y][x]
		return word

	def coord_to_key(self, x, y):
		return y*GRID_SIZE + x
	def key_to_coord(self, k):
		return (k % GRID_SIZE, k // GRID_SIZE)



def contains_all(letters, word):
	""" Check whether sequence @letters contains ALL of the items in @word. """
	return 0 not in [c in letters for c in word]

def start_of_word(word, words):
	""" Check whether sequence @word is a valid start of any item in @words. """
	return 1 in [w.startswith(word) for w in words]

def get_filtered_words(letters):
	start_t = time.time()
	words = []

	# minimum word length is 3
	for fname in [WORD_FILE, CUSTOM_WORD_FILE]:
		with open(fname, 'r') as f:
			for line in f:
				line = line.lower().strip()
				if contains_all(letters, line) and len(line) > 2:
					words.append(line)

	words = np.array(words, dtype=str)
	print("Reduced set: {}".format( len(words) ))
	print("Time: {} s\n".format( time.time() - start_t ))
	return words

grid = None
found = []
words = []
verbose = False
def visit_next(x,y, neighbor):
	global grid, found, words, verbose

	if verbose: print("[Deeper] next neighbor for {}...".format(grid.get_current_word()))

	done_neighbors = []

	while True:
		test_word = grid.get_current_word()
		if verbose: print("{} \t{}".format(test_word, grid.visited))

		# check if the current test word might be an actual word
		if test_word in words:
			if test_word not in found:
				found.append(test_word)
		
		if not start_of_word(test_word, words):
			if verbose: print("Reversing, no words for this combination...")
			return
		
		# get next neighbor
		neighbor, nx, ny = grid.get_next_neighbor(x,y, done_neighbors)

		# keep going deeper unless we are gone through all...
		if len(test_word) > 0 and neighbor != None:
			visit_next(nx,ny, neighbor)
			done_neighbors.append( grid.coord_to_key(nx, ny) )
			grid.reverse()
			if verbose: print("Done: {}".format(done_neighbors))

		if neighbor == None:
			break

	if verbose: print("Reversing, no more neighbors ({})...".format(test_word))

def print_results(results, sort):
	print("******** FOUND ({}) ********".format(len(found)))

	# sort if necessary - the list is already ordered by 'location'
	if sort == 'alphabetical':
		results.sort(results)
	elif sort == 'length':
		results.sort(key=len, reverse=True)

	for word in results:
		prefix = ""
		if len(word) > 8:
			prefix = " . . . . . . . "
		elif len(word) > 5:
			prefix = " . . . . "
		elif len(word) > 3:
			prefix = " . "

		print(prefix + word)


def main(args):
	global grid, found, words, verbose
	letters = args.letters.lower()
	verbose = args.verbose

	# Validate arguments
	
	if args.sort == 'alphabetical' or args.sort == 'a':
		sort = 'alphabetical'
	elif args.sort == 'length' or args.sort == 'l':
		sort = 'length'
	else:
		sort = 'location'

	if len(letters) != GRID_SIZE**2:
		raise Exception("Invalid list dimensions! Make sure to give exactly {} letters.".format(GRID_SIZE**2))

	# Find results
	
	grid = Grid(letters)

	# optimization: filter out the words that cannot be formet using the available letters
	words = get_filtered_words(letters)

	found = []
	for y,row in enumerate(grid.grid):
		for x,letter in enumerate(row):
			if verbose: print("New start: {} in ({},{})".format(letter, x, y))
			grid.visited = [grid.coord_to_key(x,y)]
			visit_next(x, y, None)
			grid.clear_visited()

	# Done!
	print_results(found, sort)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Win in Sanajahti.')
	parser.add_argument('letters', type=str, help='the 4x4 grid of the letters as a string')
	parser.add_argument('-s', '--sort', default='location', type=str, help='sorting of the results (alphabetical | length | location (default))')
	parser.add_argument("-v", "--verbose", action="store_true")
	main( parser.parse_args() )