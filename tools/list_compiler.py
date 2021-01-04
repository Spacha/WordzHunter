MIN_LEN, MAX_LEN = ( 3,10 )
VALID_CHARACTERS = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","å","ä","ö"]

words_fname = '../lists_testing/kotus/kotus-sanalista_v1.xml'
bl_fname = '../lists/blacklist.txt'
wl_fname = '../lists/whitelist.txt'
target_fname = '../lists/words_filtered.txt'
slen = len('<st><s>') # length of the opening tag in every line

removed_len = 0 	# number of words removed due to invalid length
removed_inv = 0 	# number of words removed due to it containing an invalid character
removed_bl = 0 		# number of words removed due to it being blacklisted

def valid_word(word):
	""" Validates a word according to a strict rules. """
	global removed_len, removed_inv, removed_bl

	# check if the word is too short or too long
	if len(word) < MIN_LEN or len(word) > MAX_LEN:
		removed_len += 1
		return False

	# check if the word is blacklisted
	if word in blacklist:
		removed_bl += 1
		return False

	# check if there are invalid characters (only scandinavian alphabets)
	for c in word:
		if c not in VALID_CHARACTERS:
			removed_inv += 1
			return False

	# the word is valid!
	return True

def remove_duplicates(words):
	""" Remove duplicate words - does not preserve order! """
	return list(set(words))


################################################################################

blacklist = []
words = []
# get blacklisted words
with open(bl_fname, 'r') as f:
	for lnum,line in enumerate(f):
		blacklist.append(line.strip().rstrip("\n"))

# add whitelisted words
with open(wl_fname, 'r') as f:
	for lnum,line in enumerate(f):
		words.append(line.strip().rstrip("\n"))

# add all normal words that are not blacklisted and are valid
with open(words_fname, 'r') as f:
	for lnum,line in enumerate(f):
		parsed_line = line[slen:line.find('<', slen)]
		if valid_word(parsed_line):
			words.append(parsed_line)

# sort the words alphabetically (TODO: sort by 'commonness')
words = remove_duplicates(words)
words.sort()

# write the results to the target file
with open(target_fname, 'w') as f:
	for word in words:
		f.write(word + '\n')

print("Compilation resulted in {} words.".format(len(words)))
print("\tWords removed due to invalid length: {}".format(removed_len))
print("\tWords removed due to invalid characters: {}".format(removed_inv))
print("\tWords removed due to it being blacklisted: {}".format(removed_bl))