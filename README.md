# Inverted-Index
A basic search engine has been implemented using SPIMI - single pass in memory indexing. 


## Author
You can get in touch with me on <a class="btn-linkedin" href="https://www.linkedin.com/in/ibrahim-zfr/">LinkedIn</a>!

If you liked my repository, kindly support my work by giving it a ⭐!


## About this Repository
A basic Inverted Index is constructed on a corpus of HTML files. <br>
Corpus may be downloaded from here - https://drive.google.com/open?id=1_qNz0U1D_3pNsHWNpD25tvEwM4yvsGeI
The performance of 4 ranking functions are benchmarked against human expert judgements, using 10 queries. <br>
The ranking functions include:
##### TF-IDF
##### Okapi-TF
##### Okapi-BM25
##### Language Model with Jelinek Mercer smoothing

Later, the ranking done with the 4 ranking functions were compared with judgements given by human experts in the corpus.qrel file. 
The metric for comparison was Graded Average Precision(GAP). 


### Method
The following sequence may be followed for a quick run-through of the whole process(using Command-line): 
1) Tokenize Documents and make forward index. <br>
```
python.py tokenize_documents.py <path_to_corpus> 
```

2) Make inverted index from forward index.<br>
``` 
python.py invert_index.py 
```


3) (Optional) Find any term/document from the index.<br>
* For searching details of a term in a specific document<br>
```python read_index.py --term <term> --doc <doc> ```<br>
* For searching details of a term<br>
```python read_index.py --term <term> ```<br>
* For searching details of a doc<br>
```python read_index.py --doc <doc> ```<br>


4) Now that the inverted index has been made, we may start scoring <br>
``` 
python.py scoring.py --score TF-IDF
python.py scoring.py --score OK-TF
python.py scoring.py --score JM-Smooth
python.py scoring.py --score OK-BM
```
<br>
The scores for the files which had the query terms have been scored. 
You should also include the scores for files that are not related to the query at all, with Step 5. 
<br>

5) Complete the outputfiles. 
``` 
python.py scoring.py --score completeoutput
```
<br>
All outputs are now in the files updatedokbm.txt, updatedjm.txt, updatedoktf.txt and updatedtfidf.txt.
<br>
<br>


6) Compare with Human Expert Judgement, with Graded Average Precision. <br>
```
python gap.py corpus.qrel updatedokbm.txt -v 
python gap.py corpus.qrel updatedoktf.txt -v 
python gap.py corpus.qrel updatedtfidf.txt -v 
python gap.py corpus.qrel updatedjm.txt -v 
```
<br>
 This gives us the comparison of all of the scoring functions, with respect to human graded judgements. 



## Contributions are Welcome!
Feel free to improve/find bugs in the code by generating a pull request!<br>



## License
[MIT License](https://github.com/ibrahimzafar/Inverted-Index/blob/master/LICENSE)



