from collections import Counter
import xml.etree.ElementTree as ET
import math
import sys
from nltk import *
import os

#initializes the Porter Stemmer 
stemmer=PorterStemmer()
		
class Scoring:
	#initializes important variables
	def __init__(self):
		self.average_query_length, self.queries_list = self.read_query_len_file()
		self.tfquery_list = self.tf_query()
		self.docnames=self.doc_names()
		self.average_doc_length, self.doc_length = self.read_doc_len_file()
		self.termIDs, self.doc_offset = get_misc_info()

	#computes the occurences of terms in a query
	def tf_query(self):
		tfquery={}
		for query in self.queries_list:
			query_counts = [tokenize(term) for term in query[1]]
			tf = Counter(query_counts)
			tfquery[query[0]] = tf
		return tfquery

	#Parses the file topics.xml and gets the queries with their ids
	def read_query_len_file(self):
		print('Loading queries..')
		tree = ET.parse('topics.xml')
		root = tree.getroot()
		queries_list=[]
		summation=0
		total_number=0
		for child in root:
			query_id = int(child.get('number'))
			for attribute in child:
				if attribute.tag == 'query':
					query_text = attribute.text.split()
					queries_list.append([query_id, query_text])
					total_number = total_number + 1
					summation = summation + len(query_text)
		average_query_length = summation/total_number
		return average_query_length, queries_list

	#loads all names of documents of a corpus in memory
	def doc_names(self):
		docnames={}
		print('Loading document names..')
		with open('docids.txt', 'r') as docfile:
			while (True):
				line=docfile.readline().split()
				if (len(line)<1):
					break
				docnames[int(line[0])]=line[1]
		return docnames

	#loads the lengths of all corpus documents in memory
	def read_doc_len_file(self):
		print('Loading document lengths..')
		summation=0
		doc_length = {}
		with open("doc_index.txt", "r") as doc_index_file:
			while(True):
				line = doc_index_file.readline().split()
				if (len(line)<1):
					break
				doc_length[int(line[0])]=int(line[1])
				summation=summation+int(line[1])
		average_doc_length = summation / (len(doc_length))
		return average_doc_length, doc_length

	#returns okapi-tf scores for each term of a document in a dictionary
	def whole_doc_okapi(self, docID):
		doc_okapi = {}
		if docID != 0:
			try:
				doc_length = self.doc_length[docID]
			except:
				doc_length = 0
			if doc_length > 0:
				reached = False
				with open("doc_index.txt",'r') as doc_index_file:
					offset_in_docindex = self.doc_offset[docID]
					doc_index_file.seek(offset_in_docindex)					
					while (True):
						doc = doc_index_file.readline().split()
						if (len(doc) < 1):
							break
						if (int(doc[0]) != docID and reached):
							break
						if int(doc[0])==docID:
							reached=True
							doc_tf=len(doc[2:])
							doc_okapi[int(doc[1])] = float(doc_tf) / (float(doc_tf) + 0.5 + 1.5*(float(doc_length) / float(self.average_doc_length)))
		return doc_okapi

	#returns okapi-tf scores for each term of a query in a dictionary
	def whole_query_okapi(self, ids_of_query_terms, tfquery):
		query_okapi = {}
		if len(ids_of_query_terms) > 1 :
			query_length = sum(tfquery.values())
			for term, freq in tfquery.items():
				term = tokenize(term)
				if (len(term))>1 and term in ids_of_query_terms.keys():
					termfrequency = freq
					a = termfrequency / (termfrequency + 0.5 + 1.5 * (query_length/ self.average_query_length))
					query_okapi[ids_of_query_terms[term]]=a
		return query_okapi

	#this function takes a single query and computes scores for all 
	#relevant documents using the scoring function okapi-tf
	def okapi_TF_all(self, query):
		queryID = query[0]
		tfquery = self.tfquery_list[queryID]
		ids_of_query_terms = get_IDs_of_query_terms(query, self.termIDs)
		query_okapi = self.whole_query_okapi(ids_of_query_terms,tfquery)
		query_norm = sum(square([i for i in query_okapi.values()]))
		term_docs, relevant_doc_list = query_relevant_docs(ids_of_query_terms)
		for docID in relevant_doc_list:
			score = 0.0
			doc_okapi = self.whole_doc_okapi(docID)
			doc_norm=sum(square([i for i in doc_okapi.values()]))
			for qtid, qtoka in query_okapi.items():
				try:
					dtoka = doc_okapi[int(qtid)]
				except KeyError:
					dtoka = 0.0
				score = score + ((qtoka * dtoka))
			score = score / (doc_norm * query_norm)
			with open('oktf.txt', 'a') as oktffile:
				oktffile.write(str(queryID) + '\t0\t' + self.docnames[docID] + '\t' + str(docID) + '\t' + str(score) + ' run1' + '\n')
			print(queryID, ' 0 ', self.docnames[docID] ,'', docID, '', score, ' run1')
	#this function takes a single query and computes scores for all 
	#relevant documents using the scoring function tf-idf
	def TF_IDF_all(self, query):
		print("TF-IDF is now running")
		queryID = query[0]
		query_text = query[1]
		print('query_text:',query_text)
		tfquery = self.tfquery_list[queryID]
		ids_of_query_terms = get_IDs_of_query_terms(query, self.termIDs)
		query_okapi = self.whole_query_okapi(ids_of_query_terms, tfquery)
		all_dfs={}
		D = len(self.doc_length)
		
		term_docs, relevant_doc_list = query_relevant_docs(ids_of_query_terms)

		query_okapi.pop(0, None)					#remove key that doesn't exist in the corpus
		for qtID, qok in query_okapi.items():
			df = len(term_docs[qtID])
			query_okapi[qtID] = qok * (math.log(D/df))
		query_norm = sum(square([i for i in query_okapi.values()]))
		for docID in relevant_doc_list:
			score = 0.0
			doc_okapi = self.whole_doc_okapi(docID)
			dot_product = 0.0
			tempd = []
			for qtID, qok in query_okapi.items():
				df = len(term_docs[qtID])
				try:
					dok = doc_okapi[int(qtID)]
				except:
					dok = 0.0
				d = dok * (math.log(D/df))
				dot_product = dot_product + (qok * d)
				tempd.append(d)
			doc_norm=sum(square([i for i in tempd]))
			score = dot_product / (query_norm * doc_norm)
			with open('tfidf.txt', 'a') as tfidffile:
				tfidffile.write(str(queryID) + '\t0\t' + self.docnames[docID] + '\t' + str(docID) + '\t' + str(score) + ' run1' + '\n')
			print(queryID, ' 0 ', self.docnames[docID] ,'', docID, '', score, ' run1')


	#this function takes a single query and computes scores for a single 
	#document using the language model with jelinek mercer smoothing
	def jelinek_mercer_doc(self, docID):
		lmbda = 0.6
		all_terms=all_terms_in_doc(docID, self.doc_offset) # 	{termID: tf}
		try:
			length_doc = doc_length[docID]
		except KeyError:
			total_prob = 0.0
		else:
			doc_term_stats = corpus_stats(all_terms.keys())	#	{termID : {tftotal, total_occur} }
			corpus_length = sum(self.doc_length.values())
			total_prob = 1
			for termID, tf in all_terms.items():
				term_prob=0.0
				tftotal = doc_term_stats[termID][0]
				total_occurences = doc_term_stats[termID][1]
				term_prob = lmbda * (tf/length_doc) + (1 - lmbda) * (total_occurences/corpus_length)
				total_prob = total_prob * term_prob
		print(queryID, ' 0 ', self.docnames[docID] ,'', docID, '', total_prob, ' run1')
		return total_prob

	#this function takes a single query and computes scores for all 
	#relevant documents using the language model with jelinek mercer smoothing
	def jelinek_mercer_all(self, query):
		queryID = query[0]
		tfquery = self.tfquery_list[queryID]
		ids_of_query_terms = get_IDs_of_query_terms(query, self.termIDs)
		query_stats = corpus_stats(ids_of_query_terms.values())
		corpus_length = sum(self.doc_length.values())
		term_docs, relevant_doc_list = query_relevant_docs(ids_of_query_terms)
		lmbda = 0.6
		for docID in relevant_doc_list:
			total_prob = 1
			score = 0.0
			length_doc = self.doc_length[docID]
			for termID in ids_of_query_terms.values():
				tf = tf_doc(docID, termID, self.doc_offset)
				try:
					total_occur = query_stats[termID][1]
				except KeyError:
					total_occur = 0
				term_prob = lmbda * (tf/length_doc) + (1- lmbda) * (total_occur/corpus_length)
				total_prob = total_prob * term_prob
			score = total_prob
			with open('jm.txt', 'a') as jmfile:
				jmfile.write(str(queryID) + '\t0\t' + self.docnames[docID] + '\t' + str(docID) + '\t' + str(score) + ' run1' + '\n')
			print(queryID, ' 0 ', self.docnames[docID] ,'', docID, '', score, ' run1')

	#this function takes a single query and computes scores for a single 
	#document using the Okapi-BM25 scoring function
	def okapi_BM25(self, docID, query):
		queryID = query[0]
		tfquery = self.tfquery_list[queryID]
		tfdoc = all_terms_in_doc(docID, self.doc_offset)
		query_terms_IDs = get_IDs_of_query_terms(query, self.termIDs)
		score = 0.0
		D = len(self.doc_length)
		k1=1.2
		b=0.75
		k2=500
		try:
			length_doc = self.doc_length[docID]
		except:
			length_doc = 0.0
		K = k1 * ((1-b) + (b * (length_doc / self.average_doc_length)))
		for term in tfquery.keys():
			try:
				termID = int(query_terms_IDs[term])
			except:
				termID = -1
			try:
				tfd = tfdoc[termID]
			except KeyError:
				tfd = 0.0
			tfq = tfquery[term]
			df = len(all_docs_containing_term(termID))
			logvalue = math.log((D + 0.5)/(df + 0.5))
			middleterm = ((1 + k1) * tfd) / (K + tfd)
			rightterm = ((1 + k2) * tfq) / (k2 + tfq)
			whole_term = logvalue * middleterm * rightterm
			score = score + whole_term
		with open('okbm.txt', 'a') as okbmfile:
			okbmfile.write(str(queryID) + '\t0\t' + self.docnames[docID] + '\t' + str(docID) + '\t' + str(score) + ' run1' + '\n')
		print(queryID, ' 0 ', self.docnames[docID] ,'', docID, '', score, ' run1')
		return score
	#this function takes a single query and computes scores for all 
	#relevant documents using the scoring function okapi-bm25
	def okapi_BM25_all(self, query):
		queryID = query[0]
		query_text = query[1]
		tfquery = self.tfquery_list[queryID]
		score = 0
		D = len(self.doc_length)
		k1=1.2
		b=0.75
		k2=500
		ids_of_query_terms = get_IDs_of_query_terms(query, self.termIDs)
		term_docs, relevant_doc_list = query_relevant_docs(ids_of_query_terms)
		print('query:',query)
		print('ids_of_query_terms:', ids_of_query_terms)
		print('relevant_doc_list:', relevant_doc_list)
		query_okapi = self.whole_query_okapi(ids_of_query_terms, tfquery)
		for docID in relevant_doc_list:
			score = 0.0
			length_doc = self.doc_length[docID]
			K = k1 * ((1-b) + (b * (length_doc / self.average_doc_length)))
			all_term_freq = all_terms_in_doc(docID, self.doc_offset)
			for term, count in tfquery.items():
				try:
					termID = self.termIDs[term]
				except KeyError:
					termID = 0
				try:
					tfd = all_term_freq[int(termID)]
				except KeyError:
					tfd = 0.0
				tfq = count
				try:
					df = len(term_docs[termID])
				except KeyError:
					df = 0.0
				logvalue = math.log((D+0.5)/(df+0.5))
				middleterm = ((1+k1) * tfd) / (K + tfd)
				rightterm = ((1+k2) * tfq) / (k2 + tfq)
				whole_term = logvalue * middleterm * rightterm
				score = score + whole_term
			print(queryID, ' 0 ', self.docnames[docID] ,'', docID, '', score, ' run1')
			with open('okbm.txt', 'a') as okbmfile:
				okbmfile.write(str(queryID) + '\t0\t' + self.docnames[docID] + '\t' + str(docID) + '\t' + str(score) + ' run1' + '\n')

#returns 1 dictionary, 1 list 
#term_docs - {termID: all docs that contain this term}
#all_docs - [all docs that contain this term]
def query_relevant_docs(ids_of_query_terms):
	term_docs={}
	all_docs=[]
	for termID in ids_of_query_terms.values():
		relevant_docs = all_docs_containing_term(termID)
		term_docs[termID] = relevant_docs
		all_docs.extend(relevant_docs)
	return term_docs, sorted(list(set(all_docs)))
	

#returns a list of all documents that contain a term
def all_docs_containing_term(termID):				
	newdoc = 0
	doclist=[]
	with open('term_info.txt', 'r', encoding='utf-8', errors='ignore') as term_info_file:
		while (True):
			line = term_info_file.readline().split()
			if len(line) < 1:
				break
			if termID == int(line[0]):
				offset_in_termindex = int(line[1])
				break
	with open("term_index.txt", 'r') as termindex_file:
		try:
			termindex_file.seek(offset_in_termindex)
		except:
			print('termID:',termID)
		while (True):
			line = termindex_file.readline().split()
			try:
				if (int(line[0]) == termID):
					postings_list = line[1:]
					for posting in postings_list:
						doc = posting.split(":")
						if (int(doc[0]) != 0):
							newdoc = newdoc + int(doc[0])
							doclist.append(newdoc)
					break
			except:
				break
	return doclist

#returns termID for each query term 
def get_IDs_of_query_terms(query, termIDs):
	tokenized_terms = [tokenize(term) for term in query[1]]
	tokenized_terms = [term for term in tokenized_terms if len(term) > 1]	
	term_ids = {}
	for term in tokenized_terms:
		try:
			term_ids[term] = termIDs[term]
		except KeyError:
			term_ids[term] = 0
	term_ids = OrderedDict(sorted(term_ids.items(), key=lambda t: t[1]))
	return term_ids


#function name explains what it does
def get_IDs_of_all_query_terms(queries, termIDs):
	tokenized_terms = [tokenize(term) for term in query for query in queries]
	term_ids = {term:termIDs[term] for term in tokenized_terms}
	return term_ids

#returns the term frequency of term with termID in doc with docID
def tf_doc(docID, termID, doc_starts_at):				
	termfrequency=0
	if termID!=0 and docID!=0:
		with open("doc_index.txt",'r+') as doc_index_file:
			offset_in_docindex = doc_starts_at[docID]
			doc_index_file.seek(offset_in_docindex)
			while (True):
				line = doc_index_file.readline().split()
				if len(line)<1:
					break
				if (docID<int(line[0])):
					break
				if int(line[0])==docID and int(line[1])==termID:
					termfrequency=len(line[2:])
					break
	return termfrequency			

#returns a dictionary of the form 
#{termID: [#documents in which term exists, total occurence of term in whole corpus]}
def corpus_stats(term_ids):							
	stats={}
	with open('term_info.txt') as termfile:
		for termID in term_ids:
			tfd = 0
			overall_occurences=0
			while (True):
				line = termfile.readline().split()
				if (len(line)<1):
					break
				if termID==int(line[0]):
					overall_occurences=int(line[2])
					tfd=int(line[3])
					stats[termID]=[tfd, overall_occurences]
					break
	return stats

#removes punctuation and numbers, tokenizes strings 
def tokenize(term):
	term = ''.join(e for e in term if e.isalpha())		#clean punctuation
	term = stemmer.stem(term.lower())
	return term					
def square(list):
    return map(lambda x: x ** 2, list)

#returns a dictionary of a single document with words, 
#and the total number of times the words occured in that document
def all_terms_in_doc(docID, doc_starts_at):
	terms_len=OrderedDict()
	done=False
	with open ('doc_index.txt') as doc_index_file:
		offset_in_docindex = doc_starts_at[docID]
		doc_index_file.seek(offset_in_docindex)
		while(done==False):
			termID=0
			tf=0
			line = doc_index_file.readline().split()
			if len(line)<1:
				break
			if docID == int(line[0]):
				termID = int(line[1])
				tf = len(line[2:])
				terms_len[termID] = tf
			if (docID < int(line[0])):
				done = True
	return terms_len

#returns dictionary of the format {termID: [all documents that have this term]}
def all_docs_containing_query_terms(ids_of_query_terms):
	term_files={}
	for termID in ids_of_query_terms:
		term_files[termID] = all_docs_containing_term(termID)
	return term_files

#returns common elements of 2 lists
def common_elements(list1, list2):
	return list(set(list1) & set(list2))


#create a helper file, doc_index_details.txt - for offsets to locations in the doc_index.txt file 
#where the details of a document are located
def generate_docindex_details():
	open('doc_index_details.txt', 'w', encoding='utf-8', errors='ignore')
	seenID=0
	with open('doc_index.txt', 'r', encoding='utf-8', errors='ignore') as doc_index_file, open('doc_index_details.txt', 'r+', encoding='utf-8', errors='ignore') as details_file:
		while(True):
			line_start_offset = doc_index_file.tell()
			line = doc_index_file.readline().split()
			if len(line)<1:
				break
			docID = int(line[0])
			if seenID != docID:
				details_file.write(str(docID) +'\t'+ str(line_start_offset)+'\n')
				seenID = docID

#retrieves the offsets of all documents
def get_docindex_details():
	doc_starts_at = {}
	with open('doc_index_details.txt', 'r+', encoding='utf-8', errors='ignore') as details_file:
		while(True):
			line = details_file.readline().split()
			if len(line) < 1:
				break
			doc_starts_at[int(line[0])] = int(line[1])
	return doc_starts_at			

#loads the IDs of all terms in memory
def get_term_IDs():
	termIDs={}
	with open('termids.txt', 'r', encoding='utf-8', errors='ignore') as termidfile:
		while(True):
			line = termidfile.readline().split()
			if len(line) < 1:
				break
			termIDs[line[1]]=int(line[0])
	return termIDs

#helper function that loads miscelaneous information 
def get_misc_info():
	print('Loading Document Index details..')
	if not os.path.isfile('doc_index_details.txt'):
		generate_docindex_details()
	offsets = get_docindex_details()
	print('Loading term IDs..')
	termIDs = get_term_IDs()
	return termIDs, offsets

#all the scoring functions rank the documents that are relevant to the query
#output files have only scores of relevant documents. This function completes the 
#output files with scores of all files. 
def complete_output(docnames, filename):
	open('updated'+filename, 'w')
	docID = 1
	with open(filename, 'r', encoding='utf-8', errors='ignore') as file_to_fix, open('updated'+filename, 'a', encoding='utf-8', errors='ignore') as updated_file:
		while(True):
			line = file_to_fix.readline().split()
			if len(line) < 1:
				break
			lastdocID = docID
			queryID = line[0]
			docname = line[2]
			docID = int(line[3])
			score = line[4]
			if (lastdocID < docID - 1 ):
				for i in range(lastdocID, docID):
					updated_file.write(str(queryID) + '\t0\t' + docnames[i] + '\t' + str(i) + '\t' + str(0.0) + ' run1' + '\n')
			elif (lastdocID > docID and lastdocID < len(docnames)):
				for i in range(lastdocID, len(docnames)):
					updated_file.write(str(queryID) + '\t0\t' + docnames[i] + '\t' + str(i) + '\t' + str(0.0) + ' run1' + '\n')				
			else:
				updated_file.write(str(queryID) + '\t0\t' + docname + '\t' + str(docID) + '\t' + str(score) + ' run1' + '\n')



if __name__ == '__main__':
	if (len(sys.argv) > 2):

		if (sys.argv[1]=='--score'):
			sc = Scoring()
			#done			
			if (sys.argv[2]=='TF-IDF'):
				open('tfidf.txt', 'w')
				for query in sc.queries_list:
					sc.TF_IDF_all(query)
			#done
			elif (sys.argv[2]=='OK-TF'):
				open('oktf.txt', 'w')
				for query in sc.queries_list:
					sc.okapi_TF_all(query)
			#done
			elif (sys.argv[2]=='OK-BM'):
				open('okbm.txt', 'w')
				for query in sc.queries_list:
					sc.okapi_BM25_all(query)
			#done
			elif (sys.argv[2]=='JM-Smooth'):
				open('jm.txt', 'w')
				for query in sc.queries_list:
					sc.jelinek_mercer_all(query)

			elif (sys.argv[2]=='completeoutput'):
				complete_output(sc.docnames, 'oktf.txt')
				complete_output(sc.docnames, 'okbm.txt')
				complete_output(sc.docnames, 'tfidf.txt')
				complete_output(sc.docnames, 'jm.txt')


			else:
				print('Invalid scoring function.')
				print('Scoring functions are:\n 1. TF-IDF\n 2. OK-TF\n 3. OK-BM\n 4. JM-Smooth')
				exit()				
		else:
			print('Usage is as follows\n "python query.py --score <scoringfunction>"')
			print('Scoring functions are:\n 1. TF-IDF\n 2. OK-TF\n 3. OK-BM\n 4. JM-Smooth')
			exit()
	else:
		exit()

