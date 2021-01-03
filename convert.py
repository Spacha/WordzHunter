MIN_LEN, MAX_LEN = ( 3,10 )

slen = len('<st><s>')
fres = open('lists/words_min3_max10.txt', 'a')
with open('lists_testing/words_xml.txt', 'r') as f:
	for lnum,line in enumerate(f):
		# print(line[slen:line.find('<', slen)])
		parsed_line = line[slen:line.find('<', slen)]
		if len(parsed_line) >= MIN_LEN and len(parsed_line) <= MAX_LEN:
			fres.write(parsed_line + '\n')

fres.close()