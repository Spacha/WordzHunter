slen = len('<st><s>')
fres = open('words_max16.txt', 'a')
with open('sanat_xml.txt', 'r') as f:
	for lnum,line in enumerate(f):
		# print(line[slen:line.find('<', slen)])
		parsed_line = line[slen:line.find('<', slen)]
		if len(parsed_line) > 0 and len(parsed_line) <= 16:
			fres.write(parsed_line + '\n')

fres.close()