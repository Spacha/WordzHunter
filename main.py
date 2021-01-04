import time
import argparse
import textwrap
import numpy as np
from os import path

WORD_FILE = 'lists/words_filtered.txt'

# Game settings
MIN_LEN, MAX_LEN = (3,10)
GRID_SIZE = 4

# Timing
matcher_t = 0
reduction_t = 0
testmode = False

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

def get_test_grids(testfile):
	""" . """
	grids = []

	# minimum word length is 3
	with open(testfile, 'r') as f:
		for line in f:
			line = line.lower().strip()
			if len(line) == GRID_SIZE**2:
				grids.append(line)
	return grids

def get_filtered_words(letters):
	"""
	Load the word list from a file and, to speed up the search, reduce the
	word list by filtering out the words that cannot be formed using the
	available letters.
	"""
	global reduction_t

	start_t = time.time()
	words = []

	with open(WORD_FILE, 'r') as f:
		for line in f:
			line = line.lower().strip()
			if len(line) >= MIN_LEN and contains_all(letters, line):
				words.append(line)

	words = np.array(words, dtype=str)
	print("Reduced set: {}".format( len(words) ))
	print("Reduction time: {} s\n".format( time.time() - start_t ))
	if testmode: reduction_t += time.time() - start_t
	return words

grid = None
found = []
words = []
verbose = False
def visit_next(x,y, neighbor):
	global grid, found, words, verbose, matcher_t

	if verbose: print("[Deeper] next neighbor for {}...".format(grid.get_current_word()))

	done_neighbors = []

	while True:
		test_word = grid.get_current_word()
		if verbose: print("{} \t{}".format(test_word, grid.visited))

		# check if the current test word might be an actual word
		if test_word in words:
			if test_word not in found:
				found.append(test_word)
		
		if testmode: start_t = time.time()
		if not start_of_word(test_word, words):
			if verbose: print("Reversing, no words for this combination...")
			return
		if testmode: matcher_t += time.time() - start_t
		
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

#################################################
#                PRINT RESULTS                   
#################################################

def print_test_results(grid_list, found_total, time_total):
	""" Print test results. """
	global matcher_t, reduction_t

	test_runs = len(grid_list)
	avg_search_t = time_total / test_runs
	avg_reduction_t = reduction_t / test_runs
	avg_matcher_t = matcher_t / test_runs
	avg_other_t = (time_total - reduction_t - matcher_t) / test_runs

	def of_total(t):
		return round(t / avg_search_t*100, 1)

	print("\nTotal TEST time: {} s".format(time_total))
	print("\tRan {} searches".format(len(grid_list)))
	print("\tFound {} words".format(found_total))
	print("\tAverage search time: {} s".format(avg_search_t))
	print("\t\tReduction time {} s, {} %".format(avg_reduction_t, of_total(avg_reduction_t)))
	print("\t\tMatcher time {} s, {} %".format(avg_matcher_t, of_total(avg_matcher_t)))
	print("\t\tRest {} s, {} %".format(avg_other_t, of_total(avg_other_t)))


def print_results(results, found_total, sorting, time_total):
	""" Print the results in a helpful form. """
	print("\nTotal time: {} s".format(time_total))
	print("******** FOUND ({}) ********".format(found_total))

	# sort if necessary - the list is already ordered by 'location'
	if sorting == 'alphabetical':
		results.sort(results)
	elif sorting == 'length':
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

#################################################
#                    MAIN                        
#################################################

def main(letters, testfile, sorting):
	global grid, found, words, verbose, testmode

	if testmode:
		grid_list = get_test_grids(testfile)
	else:
		grid_list = [letters]

	# Find results

	start_t = time.time()
	found_total = 0
	for letters in grid_list:
		grid = Grid(letters)

		# optimize by filtering out the words that cannot
		# be formed using the available letters
		words = get_filtered_words(letters)

		found = []
		for y,row in enumerate(grid.grid):
			for x,letter in enumerate(row):
				if verbose: print("New start: {} in ({},{})".format(letter, x, y))
				grid.visited = [grid.coord_to_key(x,y)]
				visit_next(x, y, None)
				grid.clear_visited()

		found_total += len(found)

	# Done!
	time_total = time.time() - start_t
	if testmode:
		print_test_results(grid_list, found_total, time_total)
	else:
		print_results(found, found_total, sorting, time_total)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Win in Sanajahti.")
	parser.add_argument("-i", "--input", default="", type=str, help="the 4x4 grid of the letters as a string, required unless -t is used")
	parser.add_argument("-s", "--sorting", default="location", type=str, help="sorting of the results (alphabetical | length | location (default))")
	parser.add_argument("-v", "--verbose", action="store_true")
	parser.add_argument("-t", "--test", default="", type=str, help="run a list of test grids (file name must be given) and print metrics")

	# Validate arguments
	
	args = parser.parse_args()

	letters 	= ""
	testmode 	= False
	testfile 	= ""
	sorting 	= "location"

	testmode = len(args.test) > 0
	if testmode:
		testfile = args.test
		if not path.isfile(testfile):
			raise ValueError("Testfile '{}' not found!".format(testfile))

	letters = args.input.lower()
	verbose = args.verbose

	if args.sorting == "alphabetical" or args.sorting == "a":
		sorting = "alphabetical"
	elif args.sorting == "length" or args.sorting == "l":
		sorting = "length"

	if not testmode and len(letters) != GRID_SIZE**2:
		raise ValueError("Invalid list dimensions! Make sure to give exactly {} letters.".format(GRID_SIZE**2))

	main( letters, testfile, sorting )
