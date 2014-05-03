Some quick and dirty code for calculating Burrows's Delta measure of textual difference. Solutions like  https://files.nyu.edu/dh3/public/TheDeltaSpreadsheets.html and https://sites.google.com/site/computationalstylistics/
already exist but I did not find any Python code.

Needs NLTK, matplotlib, numpy

Run on command line with "python delta.py [author corpuses] -t target text"
Additional optional switches include 
-c to set culling of words from main corpus (70, for example, would cull if 70 of a specific word is in the total corpus by virtue of its abundance in a single author corpus)
-f to set number of features to use (default is 500)
-p [true/false] will plot the final Z scores if true
-o [filename] will print output to a file (otherwise printed to stdout)

