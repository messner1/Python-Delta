import nltk
import string
import sys
import argparse
import math
import re

import numpy
import matplotlib.pyplot as plt


class fullCorpus:

	def __init__(self, textCollections, numFeatures, cullPercentage):
		self.overallList = nltk.FreqDist()
		self.standardDev = 0
		self.nonPercent = {}
		
		for collection in textCollections:
			for text in collection.collection:
				self.overallList.update(collection.collection[text].freqList) #build an overall list of word frequencies out of the individual text lists contained in the passed textcollections (candidate and target generally)
		
		#cull overrepresented features here (as long as the option has been passed)
		if cullPercentage > 0:
			for feature in self.overallList:
				for collection in textCollections:
					for text in collection.collection:
						if feature in collection.collection[text].freqList: #if the given feature shows up in the text
							if (float(self.overallList[feature]) > 0) and (float(collection.collection[text].freqList[feature])/float(self.overallList[feature]) * 100) >= cullPercentage:
								self.overallList.pop(feature) #if it meets the percentage threshold (IE one text accounts for at least 70 occurences of a feature of the overall corpus) cut it
		
		#cull list down to numfeatures
		tempList = nltk.FreqDist()
		for r in range(0, numFeatures):
			key, value = self.overallList.items()[r]
			tempList.inc(key, value)
		self.overallList = tempList
		
		#get standard deviation of main corpus set
		self.standardDev = numpy.std(self.overallList.values())
		
		self.setPercentageDict() #build a dictionary of the percentage of each word	
			

				
	def getList(self): #returns the dict of token|number of times token occurs
		return self.overallList		
	
	def setPercentageDict(self):
		self.percentageDict = {key: self.overallList.freq(key) for key in self.overallList}
	
	def getPercentageDict(self):
		return self.percentageDict
	
		
	
		
		
class individualText:
	def __init__(self, file): #an individual text is a single freq dist for a single inputted file
		raw = file.read()
		raw = re.sub('\.|,|\(|\)|;|:|!|&|\*|\'','', raw) #remove punctuation
		self.freqList = nltk.FreqDist(word.lower() for word in nltk.word_tokenize(raw)) #tokenize
		self.zDict = {}
		self.setPercentageDict()#build a dictionary of the percentages
	
	def getList(self): #returns the dict of token|number of times token occurs for an individual text
		return self.freqList
					
	def getPercentageDict(self):
		return self.percentageDict
		
	def setPercentageDict(self):
		self.percentageDict = {key: self.freqList.freq(key) for key in self.freqList}
		
	def setZScoreDict(self, fullCorpus):  #take the overall corpus and using its percentage dictionary find the difference between this texts percentage of a feature and the overall, then make that into a dict
		for dist in fullCorpus.percentageDict: 
			if dist in self.percentageDict:
				self.zDict.update({dist : (self.percentageDict[dist] - fullCorpus.percentageDict[dist])/fullCorpus.standardDev})   #go right to an array of difference in percentages divided by standard dev of word (if that's right)
			else: 
				self.zDict.update({dist : (0-fullCorpus.percentageDict[dist])/fullCorpus.standardDev}) #if the token appeared zero times in this text (but enough times to be under the feature limit in main corpus) 
		#outfile.write('\n' + self + " " + self.zDict + '\n')

		
	def compareZScore(self, compareText): # HERE not working it seems, but only at high feature sets. this might be because at like 500 features "lapham" starts showing up as a feature in the main corpus. so culling/text selection (ie make the potential author corpuses like 5 works so that it drowns out common names hopefully)?
		testZMean = 0
		for feature in self.zDict:
			testZMean += abs(self.zDict[feature] - compareText.zDict[feature])
		#this should be the final measure
		#make more intelligible by getting out of sci note!
		return testZMean/len(self.zDict) * 10000000

class textCollection:
		def __init__(self, filelist):
			self.collection = {file.name: individualText(file) for file in filelist} #a textCollection is a dictionary of individual texts
		
		def getList(self): #returns the dict of all the individual texts (key is filename, value is the individualText object)
			return self.collection
			
		def getPercentages(self):
			for text in self.collection:
				print self.collection[text].getPercentageDict()
		
		def getZScoreDicts(self, fullCorpus):
			for text in self.collection:
				self.collection[text].setZScoreDict(fullCorpus)
				
		def compareZScores(self, compareCollection, outfile, plot):
			zScoresList = []
			textList = []
			for text in self.collection:
				outfile.write(text)
				textList.append(text)
				for compareText in compareCollection.collection:
					zScoresList.append(self.collection[text].compareZScore(compareCollection.collection[compareText]))	#compare each zscore in the passed collections
					outfile.write("\n" + str(zScoresList[len(zScoresList)-1]) + "\n")
					
			if plot:
				plt.plot(zScoresList, 'ro')
				plt.title(compareText)
				plt.ylabel('Zscore')
				plt.xlabel('text')
				plt.xticks(numpy.arange(0, len(textList)), textList, size='small')
				plt.show()
def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('infiles', nargs='+', type=argparse.FileType('r'), default=sys.stdin)
	parser.add_argument('-t', '--target', nargs='+', type=argparse.FileType('r'), help = "name of unknown file")
	parser.add_argument("-f", '--features', type=int, default = 500, help="Set amount of features to use")
	parser.add_argument("-c", '--cull', type=int, default = 0, help="Percentage for culling overrepresented words in main corpus")
	parser.add_argument("-o", '--out', type=argparse.FileType('w'), default=sys.stdout, help="Optional file to write program output to. Otherwise writes to stdout")
	parser.add_argument("-p", '--plot', type=bool, default = 0, help="Enable to display a plot of Zscores")

	
	arguments = parser.parse_args()
	

	candidateTexts = textCollection(arguments.infiles)
	targetTexts = textCollection(arguments.target)

	corpus = fullCorpus([candidateTexts,targetTexts], arguments.features, arguments.cull)
	candidateTexts.getZScoreDicts(corpus)
	targetTexts.getZScoreDicts(corpus)
	
	candidateTexts.compareZScores(targetTexts, arguments.out, arguments.plot)

if __name__ == "__main__":
    main()		
		


