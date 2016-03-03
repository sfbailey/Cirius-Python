from Bio import SeqIO
UPLOAD_DIR = "/pythonScripts/upload/"
def write_tofasta(fn1="2800M-20160215_1403.fasta",fn2="2800M-20160215_1403B.fasta"):
    h1 = UPLOAD_DIR + fn1
    h2 = UPLOAD_DIR + fn2

    handle=open(h1,"rU")
    file=open(h2,'w')
    #dictionary to store key = record ID and value = sequence length
    dictSeqLen = {}
    #dictionary to store key = record ID and value = sequence
    dictSeq = {}

    print "Process fasta file ...\n"
    #store sequence info before sort into dictionary
    for record in SeqIO.parse(handle,"fasta"):
	   dictSeq[record.id, record.seq] = [str(record.id),str(record.seq)]
	   #dictSeqLen[record.id] = len(record.seq)

    #sort and store the key order in a list
    sortedRecIDList = []
    #sortedRecIDList = sorted(dictSeqLen,key=dictSeqLen.get,reverse=False)
    sortedRecIDList = sorted(dictSeq, key=lambda seq: record.seq)
    #write the ordered record ID list into file
    for record in sortedRecIDList:
	#print ">" + record + "\t" + "length=" + str(dictSeqLen[record]) + "\n"
	   file.write(">" + record + "\t" + "l=" + str(dictSeqLen[record]) + "\n")


    #close
    print "Done!\n"
    handle.close()
    file.close()