# WordzHunter
A script that finds words from given letter grid. Can be utilised in Wordz/Sanajahti or similar games - but not recommended!

It is only slightly optimized and could possibly be optimized a whole lot more. The script uses a customized of depth-first search method to find the words. The Finnish word list is from [kotus](https://kaino.kotus.fi/sanat/nykysuomi) and contains about Finnish 100 000 words. The `converter.py` script filters out some words that will not appear in the games and the script itself will filter out some 98% of the words based on the current letter grid before running the search.

## Notice
This is just a fun programming project. It is not meant to be used in malicious ways and I discourage you to use this in any actual games. If you do, however, use it, it's all on you.

# Plans
I did this just for fun and I have no specific plans.

Anyway, the script could utilize a very simple computer vision software to automatically recognize the letters from the screen. It could also utilize some other software to automatically pick the words from the screen using the touchscreen/mouse.
