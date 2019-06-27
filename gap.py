from __future__ import division
import sys
import argparse

class qrel:
    """a class for parsing trec qrels"""

    def __init__(self, path, maxgrade=1):
        """constructor. Takes a path to a qrel file 
        and optionally the theoretically max grade, 
        which defaults to binary. Converts all neg. 
        grades to 0"""

        #store the maxgrade
        self.maxgrade = maxgrade

        #compute the score associated w/ each grade
        self.scores=[(2**x - 1)/(2**maxgrade) for x in range(maxgrade+1)]

        #the actual qrel dict of dicts
        #_qrel[query][doc] = grade
        self._qrel = dict()

        #the documents at each grade
        #dict of dicts of lists
        #R[query][grade] = count
        self.R = dict()

        #read the qrel one line at a time
        IN = open(path)
        for line in IN:
            row = line.strip().split()
            
            #cast stuff to ints
            query = row[0]
            doc = row[-2]
            grade = int(row[-1])
            
            #init dicts for that query
            if query not in self.R:
                self.R[query] = [0]*maxgrade
                self._qrel[query] = dict()

            #make sure grade is non-neg
            if grade < 0:
                grade = 0
            #if its rel add it to R
            if grade > 0:
                self.R[query][grade-1] += 1
            #add it to the qrel
            self._qrel[query][doc] = grade
        IN.close()

    def getR(self, query):
        """returns that queries dict of the docs at each grade"""
        return self.R[query]

    def getQueries(self):
        """returns the set of queries"""
        return self.R.keys()

    def judge(self, query, doc):
        """returns the grade of the doc for that query."""
        try:
            return self._qrel[query][doc]
        except KeyError:
            return 0

    def getScore(self, grade):
        """returns the score associated w/ a rel grade"""
        return self.scores[grade]

    def getMaxgrade(self):
        """returns the maxgrade in the qrel"""
        return self.maxgrade

def parserun(runpath, maxrank=20):
        """constructs a run from a trec run"""

        #initialize 
        #ranked lists go in a dict of lists
        #rl[query]=[doc1,doc2,...]
        rl = dict()

        name = None

        #read the ranked list into a dict of dicts
        #rawlist[query][doc]=score
        rawlist = dict()
        #open the run
        IN = open(runpath)
        #and read it line by line
        for line in IN.readlines():
            #chomp it and split it by white space
            row = line.strip().split()

            #make sure the row wasn't empty
            if len(row)==0:
                continue

            if name == None:
                name = row[-1]

            #read the query, doc, score, etc
            query = row[0]
            
            if row[-2] == 'NaN':
                score = 0.0
            else:
                score = float(row[-2])

            #make sure the query is in the dict
            if not query in rawlist:
                rawlist[query]=dict()

            #store the doc in the presorted list
            #if the doc shows up more than once in a query, 
            #that's not my problem

            doc = row[2]
            rawlist[query][doc] = score
        IN.close()

        #for each query 
        for query in sorted(rawlist):

            #sort the list by score and then by name
            rl[query] = sorted(rawlist[query],key=lambda x: (rawlist[query][x],x),reverse=True)[:maxrank]

        return name, rl

def gap(query,run,qrel):
    """gap of a run on a query given a qrel"""
    totalp=0
    for n in range(len(run[query])):
        docn = run[query][n]
        grade = qrel.judge(query,docn)
        if grade > 0:
            p = 0
            for m in range(n+1):
                i = min(grade,qrel.judge(query,run[query][m]))
                for j in range(1,i+1):
                    p += qrel.getScore(j)
            totalp += p / (n+1)
    denom = 0
    for i in range(1,qrel.getMaxgrade()+1):
        rel=0
        for j in range(1, i+1):
            rel += qrel.getScore(j) 
        denom += rel*qrel.R[query][i-1]
    return totalp/denom

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('qrel_path', help='path to qrel file')
    parser.add_argument('run_path', help='path to run file')
    parser.add_argument('-v', '--verbose', help='display score for each query', action='store_true')
    parser.add_argument('-r', '--rank', type=int, help='evaluation rank. Defaults to 1000')
    parser.add_argument('-m', '--maxgrade', type=int, help='specify maxgrade. Defaults to 4')
    args = parser.parse_args()

    #get the maxgrade
    MAXGRADE = 4
    if args.maxgrade != None:
        MAXGRADE = args.maxgrade
    #so we can make the qrel
    theqrel = qrel(args.qrel_path, MAXGRADE)

    #now get the rank
    RANK = 1000
    if args.rank != None:
        RANK = args.rank
    runname, therun = parserun(args.run_path, RANK)

    #finally, do the evaluation
    mgap = 0
    for query in sorted(theqrel.getQueries()):
        qgap = gap(query, therun, theqrel)
        if args.verbose:
            print ("\t".join([runname, query, str(qgap)]))
        mgap += qgap
    mgap /= len(theqrel.getQueries())
    print ("\t".join([runname,'avg',str(mgap)]))
