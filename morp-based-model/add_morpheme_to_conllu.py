import sys
import re
import os
import codecs
import fileinput
import argparse
import io
import itertools


def to_conllu(conllu_tokenized, disamb_text, type):
  disamb_text = "\n".join((disamb_text.split("\n")[1:-1]))

  morps = disamb_text.split("\n</S> </S>+ESTag\n<S> <S>+BSTag\n")
  
  out = ""
  i = 0
  j = 0
  with io.StringIO(conllu_tokenized) as fi:
    for line in fi:
      line = line.strip()
      if len(line) == 0:
        i = i + 1
        j = 0

      if len(line) > 0 and not line.startswith('#'):
        cols=line.split("\t")
        # morps[i].split("\n")[j].split(" ")[1]: best parse
        if "[Unknown]" not in morps[i].split("\n")[j].split(" ")[1]:
           morpy = morps[i].split("\n")[j].split(" ")[1]
         
           morpy2 = morpy.replace("-","+")
           morphies = morpy2.split("]+")
           
           morphies.pop(0)
           

           morphies = [x for x in morphies if not x.startswith('[')]
       

           final_morp = "_"
           if len(morphies) > 0:
              final_morp = morphies[len(morphies)-1]
              #final_morp = "-".join(morphies)
              #final_morp = final_morp.replace('[','-')
              #final_morp = final_morp.replace(']','')
         
           if "-" not in cols[0]:
              if type == "full":
                 cols[8] = morpy
              elif type == "last":
                 cols[8] = final_morp
        j = j + 1
        out += str(cols[0]+"\t"+cols[1]+"\t"+cols[2]+"\t"+cols[3]+"\t"+cols[4]+"\t"+cols[5]+"\t"+cols[6]+"\t"+cols[7]+"\t"+cols[8]+"\t"+cols[9]+"\n")
          
      else:
        out += line+"\n"
  return out


if __name__=="__main__":

   f_filename = sys.argv[1]
   f_morp_filename = sys.argv[2]
   f_new_filename = sys.argv[3]
   type = sys.argv[4]
   f=codecs.open(f_filename, encoding='utf-8', errors='ignore')
   f_morp=codecs.open(f_morp_filename, encoding='utf-8', errors='ignore')
   f_new = codecs.open(f_new_filename, "w", "utf-8")

   morps = f_morp.read()

   morps = morps.split("\n</S> </S>+ESTag\n<S> <S>+BSTag\n")
  
   i = 0
   j = 0
   for line in f:
       line = line.strip()
       
       if len(line) == 0:
          i = i + 1
          j = 0
        

       if len(line) > 0 and not line.startswith('#'):
          
          cols=line.split("\t")
          if "[Unknown]" not in morps[i].split("\n")[j].split(" ")[1]:
             morpy = morps[i].split("\n")[j].split(" ")[1]
           
             morpy2 = morpy.replace("-","+")
             morphies = morpy2.split("]+")
             
             morphies.pop(0)
             

             morphies = [x for x in morphies if not x.startswith('[')]
         

             final_morp = "_"
             if len(morphies) > 0:
                final_morp = morphies[len(morphies)-1]
                #final_morp = "-".join(morphies)
                #final_morp = final_morp.replace('[','-')
                #final_morp = final_morp.replace(']','')
           
             if "-" not in cols[0]:
                if type == "full":
                   cols[8] = morpy
                elif type == "last":
                   cols[8] = final_morp
          j = j + 1
          f_new.write(str(cols[0]+"\t"+cols[1]+"\t"+cols[2]+"\t"+cols[3]+"\t"+cols[4]+"\t"+cols[5]+"\t"+cols[6]+"\t"+cols[7]+"\t"+cols[8]+"\t"+cols[9]+"\n"))
          
       else:
          f_new.write(line+"\n")