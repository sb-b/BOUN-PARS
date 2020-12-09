import sys
import re
import os
import codecs
import fileinput

def to_conllu(text):
  lines = text.split("\n")
  sent = ""
  out = ""
  for line in lines:
    line = line.strip()

    if len(line) == 0:
      sent = sent + "\n"
      out += sent
      sent = ""

    if len(line) > 0 and not line.startswith('#'):
      cols=line.split("\t")
      sent = sent + cols[1]+" "
  return out

             


if __name__=="__main__":

   f_filename = sys.argv[1]
   f_new_filename = sys.argv[2]

   f=codecs.open(f_filename, encoding='utf-8', errors='ignore')
   f_new = codecs.open(f_new_filename, "w", "utf-8")

   sent = ""
   for line in f:
       line = line.strip()
       
       if len(line) == 0:
          sent = sent + "\n"
          f_new.write(sent)
          sent = ""

       if len(line) > 0 and not line.startswith('#'):
        
          cols=line.split("\t")
          sent = sent + cols[1]+" "
             