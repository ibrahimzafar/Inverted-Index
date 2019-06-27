import os


open("term_index.txt",'w+')
open("term_info.txt",'w+')

def changeparams(termpos, docpos):
	global last_position, last_docid
	last_position = termpos
	last_docid = docpos


fileindex=1
wordlist = []
word_pool_set=set()
a = True
lineno=1
with open("doc_index.txt",'r') as doc_index_file:
	#while (a):
	while(True):
		line = doc_index_file.readline()
		if (line==""):
			break
		else:	
			#print(line)
			#print(line[2])
			line = line.split()
			#print(line[1])
			termID = int(line[1])
			docID = int(line[0])
			if termID not in word_pool_set:
				word_pool_set.add(termID)
				wordlist.append({termID:[]})				#		wordlist.append({termID:[]})	
				wordlist[termID-1][termID].append({docID:[]})	#		wordlist[termID][termID].append({docID:[]})

			else:
				wordlist[termID-1][termID].append({docID:[]})
			#print (wordlist[termID-1][termID][])
			print('docID=',docID, " -> termID=", termID)
			for i in range (2,len(line)):								# positions start at index 2
				#print ('wordlist[',termID-1,']=',wordlist[termID-1])
				#print ('wordlist[',termID-1,'][',termID,']=',wordlist[termID-1][termID])
				#print(type(wordlist[termID-1][termID]))
				length = len(wordlist[termID-1][termID]) 
				#print('length= ',length)
				#print ('wordlist[',termID-1,'][',termID,'][',docID-1,']=',wordlist[termID-1][termID][length-1])
				
				wordlist[termID-1][termID][length-1][docID].append(int(line[i]))	#adding positions
			lineno = lineno+1

with open("term_index.txt",'r+') as term_index_file, open("term_info.txt", 'r+') as term_info_file:	
	#for shiz in wordlist:
	#	print(shiz)
	changeparams(0, 0)					
	for ith_word in range(0,len(wordlist)):
		#print(wordlist[ith_word])
		location_of_ith_index = term_index_file.tell()
		for wordid, all_docs_places in wordlist[ith_word].items():
			#print(wordid, " ", all_docs_places)
			changeparams(last_position, 0)
			total_occurences_in_all_docs = 0
			term_info_file.write(str(wordid)+"\t")
			term_index_file.write(str(wordid)+"\t")
			total_docs_with_term = len(all_docs_places)
			for j in range(0, total_docs_with_term):
				#print(all_docs_places[j])
				for one_doc_id, one_doc_places in all_docs_places[j].items():
					#print("termID:",wordid,"->", "docID",one_doc_id, "->", one_doc_places)
					in_one_doc = len(one_doc_places)
					total_occurences_in_all_docs = total_occurences_in_all_docs + in_one_doc
#					last_position=0
					changeparams(0, last_docid)
					for i in range(0,in_one_doc):
						print("TermID in process: ", termID)
#						print("termID: "wordid,", docID: ",one_doc_id,":","positions located at: ", one_doc_places[i])

						term_index_file.write(str(abs(one_doc_id-last_docid))+":"+str(abs(one_doc_places[i]-last_position)))

#						last_position=one_doc_places[i]
						changeparams(one_doc_places[i], one_doc_id)
						if (i!=in_one_doc-1):
							term_index_file.write("\t")
#					last_docid=one_doc_id
					changeparams(last_position, one_doc_id)
				if (j!=total_docs_with_term-1):
					term_index_file.write("\t")					
			
			term_info_file.write(str(location_of_ith_index)+"\t"+str(total_occurences_in_all_docs)+"\t"+str(total_docs_with_term)+"\n")
		term_index_file.write("\n")
	#one character takes one byte of memory. Calling .tell() on a file object tells 
	#how much memory it has occupied, which is equal to total characters in the file
	total_characters = term_index_file.tell()				

print(len(wordlist))
print('total_characters=',total_characters)

