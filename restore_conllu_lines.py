import sys
import re
import os
import codecs
import fileinput



if __name__=="__main__":

   pred_filename = sys.argv[1]
   base_filename = sys.argv[2]
 

   pred=codecs.open(pred_filename, encoding='utf-8', errors='ignore')
   base=codecs.open(base_filename, encoding='utf-8', errors='ignore')

   write_file = codecs.open("final_output.conllu", "w", "utf-8")

   pred_sents = pred.read().split("\n\n")
   base_sents = base.read().split("\n\n")

   for psent,bsent in zip(pred_sents,base_sents):
       pwords = psent.split("\n")
       bwords = bsent.split("\n")

       for pword,bword in zip(pwords,bwords):

          if not pword.startswith("#") and not pword == "" :
          
             pcols = pword.split("\t")
             bcols = bword.split("\t")

             
             write_file.write(pcols[0]+"\t"+pcols[1]+"\t"+pcols[2]+"\t"+pcols[3]+"\t"+pcols[4]+"\t"+pcols[5]+"\t"+pcols[6]+"\t"+pcols[7]+"\t"+bcols[8]+"\t"+bcols[9]+"\n")       
          
          else:
          
             write_file.write(pword+"\n") 

       write_file.write("\n")                


               


             