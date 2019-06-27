import os
import sys
import nltk
#nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk import *


stemmer = PorterStemmer()

def __termID(a):
	global termID	
	termID = a
def __docID(a):
	global docID
	docID=a
def __offset(a):
	global offset
	offset=a
def __termfrequency(a):
	global term_frequency
	term_frequency=a
def __numberofdocuments(a):
	global no_of_docs
	no_of_docs=a
def __distinct(a):
	global distinct
	distinct=a
def __positions(a):
	global positions
	positions=a
def initialize_parameters(a):
	__offset(a)
	__termfrequency(a)
	__numberofdocuments(a)
	__termID(a)
	__docID(a)
	__distinct(a)


def doc_details(docname):
	initialize_parameters(0)
	if docname is not None:
		with open("doc_index.txt",'r+', encoding='utf-8') as docindex, open("docids.txt",'r', encoding='utf-8') as docfile:
			all_doc = docfile.read().split()
			for i in range(0,len(all_doc)):
				if docname==all_doc[i]:
					__docID(all_doc[i-1])
					break
			if docID==0:
				print('File not in directory')
			else:
				while(True):
					line = docindex.readline()
					if line !="":
						line = line.split()
						if (line[0]==docID):
							__distinct(distinct+1)
							__termfrequency(term_frequency+len(line)-2)
							
					else:
						break
				print("Listing for document:", docname)
				print("Doc ID:", docID)
				print("Distinct terms:",distinct)
				print("Total terms:", term_frequency)
def term_details(term):
	initialize_parameters(0)
	if term is not None:
		with open("term_info.txt", 'r', encoding='utf-8') as term_info_file, open("termids.txt",'r+', encoding='utf-8') as termfile:
			print(term)
			term = ''.join(e for e in term if e.isalpha())		#clean punctuation
			token = stemmer.stem(term.lower())
			doc = termfile.read().split()
			for i in range(0, len(doc)):
				if (doc[i]==token):
					__termID(doc[i-1]) 
					break
			if (termID==0):
				print("Word not in corpus")
			else:
				while(True):
					doc = term_info_file.readline().split()
					if len(doc) > 0:
						if (termID==doc[0]):
							__offset(doc[1])
							__termfrequency(doc[2])
							__numberofdocuments(doc[3])
							break	
					else:
						break
				print("Listing for term:", token)
				print("Term ID:", termID)
				print("Number of documents containing term:", no_of_docs)
				print("Term frequency in corpus:", term_frequency)
				print("Inverted list offset:", offset)
def term_doc_details(term, docname):
	initialize_parameters(0)
	if term is not None and docname is not None:
		with open("doc_index.txt",'r+', encoding='utf-8') as docindex, open("docids.txt",'r', encoding='utf-8') as docidfile, open("termids.txt",'r+', encoding='utf-8') as termfile:
			term = ''.join(e for e in term if e.isalpha())		#clean punctuation
			doc = termfile.read().split()
			term = stemmer.stem(term.lower())
			__termID('N/A')
			__docID('N/A')
			__positions(0)
			for i in range(0, len(doc)):
				if (doc[i]==term):
					__termID(doc[i-1])
					break
			if termID!='N/A':
				doc = docidfile.read().split()		
				for i in range(0, len(doc)):
					if (doc[i]==docname):
						__docID(doc[i-1])
						break
				if (docID!='N/A'):
					while (True):
						doc = docindex.readline().split()
						if len(doc)>0:
							if doc[0]==docID and doc[1]==termID:
								print('docID=',docID)
								print('termID=',termID)
								a = doc[2:]
								__positions(doc[2:])
								__termfrequency(len(positions))
								break
								
						else:
							__termfrequency('N/A')
							__positions('N/A')
							break
			else:
				print("Invalid token")
		
			print('Inverted list for term: ', term)
			print('In document: ', docname)
			print('TERMID:', termID)
			print('DOCID:', docID)
			print('Term frequency in document:', term_frequency)
			if type(positions)==list:
				print('Positions:', (', '.join(positions)))
			else:
				print('Positions:', (positions))

if __name__ == '__main__':
	if len(sys.argv) > 1:
		if sys.argv[1]=='--term' and sys.argv[3]=='--doc':
			term_doc_details(sys.argv[2], sys.argv[4])

	elif sys.argv[1]=='--term':
		term_details(sys.argv[2])	

	elif sys.argv[1]=='--doc':
		doc_details(sys.argv[2])
	else:
		print('Usage details as follows')
		print('1. For searching details of a term in a specific document\t"python read_index.py --term <term> --doc <doc>", or')
		print('2. For searching details of a term\t"python read_index.py --term <term>", or')
		print('3. For searching details of a doc\t"python read_index.py --doc <doc>"')
