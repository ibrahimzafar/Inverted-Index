import os
from bs4 import BeautifulSoup
import re
import nltk
#nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk import *
import operator
import sys


class InvertedIndex:
	path_to_corpus=sys.argv[1]
	corpus_folder = os.path.join(os.getcwd(), path_to_corpus)
	stemmer = PorterStemmer()
	stoplist = []
	unique_word_pool = set()
	wordlist = []		
	termID = 1
	def __init__(self):
		self.stoplist = self.get_stoplist("stoplist.txt")
		open("docids.txt",'w'), open("termids.txt",'w'), open("doc_index.txt",'w')
	def get_stoplist(self, path_to_stoplist):
		stoplist = []
		with open (path_to_stoplist) as stopfile:
			for word in stopfile:
				stoplist.append(word.strip())
		stopfile.close()
		return stoplist
	def writeFileToForwardIndex(self, file_number, file_dictionary):
		with open("doc_index.txt",'a', encoding='utf-8', errors='ignore') as docindex:
			if file_dictionary is not None:
				for words in self.wordlist:
					if file_dictionary.get(words[0]) is not None:
						docindex.write(str(file_number)+"\t"+str(words[1]))					
						for pos in file_dictionary.get(words[0]):
							docindex.write("\t"+str(pos))
						docindex.write("\n")
	def parseFile(self, filename, position_index):
		file_dictionary = {}
		with open (os.path.join(self.corpus_folder, filename), encoding='utf-8', errors='ignore') as readfile:
			page_soup = BeautifulSoup(readfile, "html.parser")
		for script in page_soup(["script", "style"]):
			script.decompose()
#		print(filename)	
		contents = page_soup.head
		try:
			contents.append(page_soup.body)
		except AttributeError:
			contents = page_soup.body
		except ValueError:
			pass
		if (contents is not None):
			text = contents.get_text().split()
			for tex in text:
				token = self.stemmer.stem((''.join(e for e in tex if e.isalpha())).lower())
				if len(token)>0 and token not in self.stoplist:
						if token not in self.unique_word_pool:
							file_dictionary[token]=[]
							file_dictionary[token].append(position_index)
							self.wordlist.append([token, self.termID])
							self.unique_word_pool.add(token)
							with open("termids.txt",'a', encoding='utf-8', errors='ignore') as termfile:
								termfile.write(str(self.termID)+"\t"+token+"\n")							
							self.termID = self.termID + 1
						elif token in self.unique_word_pool:
							if token not in file_dictionary:
								file_dictionary[token]=[]
							file_dictionary[token].append(position_index)
						position_index = position_index+1
			return file_dictionary
	def makeIndex(self):
		file_number = 0
		position_index=1
		progress = 0.00
		for filename in os.listdir(self.corpus_folder):
#			print(os.listdir(self.corpus_folder))
			if os.path.isfile(os.path.join(self.corpus_folder, filename)):
				file_number=file_number+1
				with open("docids.txt",'a') as docfile:
					docfile.write(str(file_number)+"\t"+filename+"\n")
				file_dictionary = self.parseFile(filename, position_index)
				self.writeFileToForwardIndex(file_number, file_dictionary)
				if file_dictionary is not None:
					file_dictionary.clear()
			progress = (file_number/len(os.listdir(self.corpus_folder)))*100		
			print("%.2f" % round(progress,2),"% " , file_number, " -> ", filename)
if __name__=="__main__":	
	index = InvertedIndex()
	index.makeIndex()
