#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import codecs
import fileinput

specAdvFile = open('./rule-based-model/QuantityDegreeAdvList.txt','r')
specAdvList = specAdvFile.readlines()
specAdvFile.close()
file = open('./rule-based-model/head_level_compounds.txt','r')
compound_words = file.readlines()
file.close()
file = open('./rule-based-model/reflexives.txt','r')
ref_words = file.readlines()
file.close()
file = open('./rule-based-model/possessive_compounds.txt','r')
nmod_words = file.readlines()
file.close()
file = open('./rule-based-model/compound_verbs_clean.txt','r')
compound_verbs = file.readlines()
file.close()

def isCompoundWord(word1,word2,lem1,lem2):
    global compound_words
    if word1+" "+lem2+"\n" in compound_words or word1+" "+word2+"\n" in compound_words:
       return True
    else:
       return False

def isReflexiveWord(word1,word2):

    global ref_words
    if word1+" "+word2+"\n" in ref_words:
       return True
    else:
       return False

def isNmodWord(word1,word2,lem1,lem2):

    global nmod_words
  
    if word1+" "+lem2+"\n" in nmod_words or word1+" "+word2+"\n" in nmod_words:
       return True
    else:
       return False



def isCompoundVerb(word1,word2,lem1,lem2,lemma):

    global compound_verbs
  
    if word1+" "+lem2+"\n" in compound_verbs or lem1+" "+lem2+"\n" in compound_verbs or word1+" "+word2[:2]+"\n" in compound_verbs or word1+" "+word2[:3]+"\n" in compound_verbs or word1+" "+word2[:4]+"\n" in compound_verbs or word1+" "+lemma+"\n" in compound_verbs:
       return True
    else:
       return False
    
def popWord(sent,lemmaList,uposList,xposList,morpList,i):
    
    sent.pop(i)
    lemmaList.pop(i)
    uposList.pop(i)
    xposList.pop(i)
    morpList.pop(i)

def isConsecutive(num1,num2):

    num1 = int(num1)
    num2 = int(num2)
    if num1+1 == num2:
       return True
    else:
       return False

def isPossessive(morp):
 
    if "[P1sg]" in morp or "[P2sg]" in morp or "[P3sg]" in morp or "[P1pl]" in morp or "[P2pl]" in morp or "[P3pl]" in morp:      
       return True
    else:
       return False
    
def find_adj_compounds(sent,lemmaList,uposList,xposList,morpList):

    tempAdjList = []
    i = 0
    while i < len(sent):
        if i < len(sent)-1 and "[Adj]" in morpList[i] and "Noun" not in morpList[i]:
            if "[Adj]" in morpList[i+1] and "Noun" not in morpList[i+1]:
                tempAdjList.append([sent[i],sent[i+1]])
                popWord(sent,lemmaList,uposList,xposList,morpList,i)
                i = 0

        i = i + 1
    return tempAdjList
          
def find_adv_compounds(sent,lemmaList,uposList,xposList, morpList, ruleActions):

    tempAdvList = []
    i = 0
    while i < len(sent):
        
        w = sent[i].split('#',1)[0].lower()
        ind = sent[i].split('#',1)[1]
        ind = int(ind)
        
        if i < len(sent)-1 and "[Adv]" in morpList[i] and "[Adv]" in morpList[i+1]:

            specAdvFile = open('./rule-based-model/QuantityDegreeAdvList.txt','r')
            specAdvList = specAdvFile.readlines()

            if w+"\n" in specAdvList:
                
                ruleActions[ind] = "adv"
            else: 
                tempAdvList.append([sent[i],sent[i+1]])
                
            popWord(sent,lemmaList,uposList,xposList,morpList,i)
            i = 0
            
        i = i + 1

    return ruleActions, tempAdvList
          
def encoding(diff,letter):

    code = ""
    for j in range(0,diff):
        code =  code + letter

    return code
 
def complexPredicateRule(sent,lemmaList, uposList, xposList, morpList,ruleActions):
    i = 0
    while i < len(sent):

        lemma = morpList[i].split("[")[0]
        if i > 0 and isCompoundVerb(sent[i-1].split('#',1)[0].lower(),sent[i].split('#',1)[0].lower(),lemmaList[i-1],lemmaList[i],lemma):
             
             index = int(sent[i].split('#',1)[1])
             index2 = int(sent[i-1].split('#',1)[1])
             ruleActions[index] = "cmp"
             ruleActions[index2] = "c"
             popWord(sent,lemmaList,uposList,xposList,morpList,i)
             i = 0

        i = i + 1

    return ruleActions

def wordCompoundRule(sent,lemmaList, uposList, xposList, morpList,ruleActions):
    i = 0
    while i < len(sent):

        if i < len(sent)-1 and (isCompoundWord(sent[i].split('#',1)[0].lower(),sent[i+1].split('#',1)[0].lower(),lemmaList[i],lemmaList[i+1]) or isReflexiveWord(sent[i].split('#',1)[0].lower(),sent[i+1].split('#',1)[0].lower())) :

             index = int(sent[i].split('#',1)[1])
             index2 = int(sent[i+1].split('#',1)[1])
             if index + 1 == index2:
                ruleActions[index2] = "fla"
                popWord(sent,lemmaList,uposList,xposList,morpList,i+1)
                i = 0
        elif i < len(sent)-1 and isNmodWord(sent[i].split('#',1)[0].lower(),sent[i+1].split('#',1)[0].lower(),lemmaList[i],lemmaList[i+1]):
             index = int(sent[i].split('#',1)[1])
             index2 = int(sent[i+1].split('#',1)[1])
             if index + 1 == index2:
                ruleActions[index] = "nmo"
                popWord(sent,lemmaList,uposList,xposList,morpList,i)
                i = 0

        i = i + 1

    return ruleActions


def numberRule(sent,lemmaList, uposList, xposList, morpList,ruleActions):

    i = 0
    while i < len(sent)-1:
    
       if uposList[i] == "NUM" and "[Det]" not in morpList[i] and uposList[i+1] == "NUM" and "[Det]" not in morpList[i+1]:
          
          index = int(sent[i+1].split('#',1)[1])
          ruleActions[index] = "fla"
          popWord(sent,lemmaList,uposList,xposList,morpList,i+1)
          i = 0

       i = i + 1
    
    return ruleActions


def properNounRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):

   i = 0
   while i < len(sent)-1:
   
       word1 = lemmaList[i] # sent[i].split('#',1)[0]
       word2 = lemmaList[i+1] # sent[i+1].split('#',1)[0]

       if (i > 0 or (i == 0 and "Prop" in morpList[i])) and word1[0].isupper() and word2[0].isupper() and isConsecutive(sent[i].split('#',1)[1],sent[i+1].split('#',1)[1]):
          tmpind = sent[i+1].split('#',1)[1]
          tmpind = int(tmpind)
             
          ruleActions[tmpind] = "fla"           
              
          if i < len(sent)-2:
             word3 = lemmaList[i+2] # sent[i+2].split('#',1)[0]
             if word3[0].isupper() and isConsecutive(sent[i+1].split('#',1)[1],sent[i+2].split('#',1)[1]):
                tmpind = sent[i+2].split('#',1)[1]
                tmpind = int(tmpind)
                ruleActions[tmpind] = "fla"               
                
                if i < len(sent)-3:
                   word4 = lemmaList[i+3] # sent[i+3].split('#',1)[0]
                   if word4[0].isupper() and isConsecutive(sent[i+2].split('#',1)[1],sent[i+3].split('#',1)[1]):
                      tmpind = sent[i+3].split('#',1)[1]
                      tmpind = int(tmpind)
                      ruleActions[tmpind] = "fla"
                                              
                      if i < len(sent)-4:
                         word5 = lemmaList[i+4] # sent[i+4].split('#',1)[0]
                         if word5[0].isupper() and isConsecutive(sent[i+3].split('#',1)[1],sent[i+4].split('#',1)[1]):
                            tmpind = sent[i+4].split('#',1)[1]
                            tmpind = int(tmpind)
                            ruleActions[tmpind] = "fla"
                            popWord(sent,lemmaList,uposList,xposList,morpList,i+4)

                      popWord(sent,lemmaList,uposList,xposList,morpList,i+3)
                    
                popWord(sent,lemmaList,uposList,xposList,morpList,i+2)

          popWord(sent,lemmaList,uposList,xposList,morpList,i+1)
          i = 0

       i = i + 1 

   return ruleActions   

def adpRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):

   i = 0
   while i < len(sent):
             
      if uposList[i] == "ADP" or uposList[i] == "AUX":
               
         index = int(sent[i].split('#',1)[1])
                     
         ruleActions[index] = "cas"
         popWord(sent,lemmaList,uposList,xposList,morpList,i)
         i = 0
      i = i + 1
   return ruleActions


def accDatLocRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):

    i = 0
    while i < len(sent)-1:

       if ("[Acc]" in morpList[i] or "[Loc]" in morpList[i] or "[Dat]" in morpList[i]) and ("[Verb]" in morpList[i+1] or ruleActions[int(sent[i+1].split('#',1)[1])] == "c"):
          index = int(sent[i].split('#',1)[1])
                        
          if "[Acc]" in morpList[i]:
             ruleActions[index] = "obj"
          else:
             ruleActions[index] = "obl"
          popWord(sent,lemmaList,uposList,xposList,morpList,i)
          i = 0

       i = i + 1
    return ruleActions

def adjNounRule(sent, lemmaList, uposList, xposList, morpList, ruleActions, tempAdjList):

    i = 0
    while i < len(sent) - 1:
    
       if ("[Adj]" in morpList[i] or "Adj+PastPart" in morpList[i] or "Adj+PresPart" in morpList[i] or "Adj+FutPart" in morpList[i]) and "[Noun]" in morpList[i+1]: 
          
          index = int(sent[i].split('#',1)[1])
                       
          ruleActions[index] = "amo"

          for ind,(a,b) in enumerate(tempAdjList):
              if b == sent[i]:
                 
                 comp_ind = a.split('#',1)[1]
                 comp_ind = int(comp_ind)
                 ruleActions[comp_ind] = "amo"
                 tempAdjList.pop(ind)

          popWord(sent,lemmaList,uposList,xposList,morpList,i)
          i = 0

       i = i + 1
    return ruleActions

def detNounRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):

   i = 0
   while i < len(sent) - 1:
             
      if "[Det]" in morpList[i] and "[Noun]" in morpList[i+1]:
               
         index = int(sent[i].split('#',1)[1])
                     
         ruleActions[index] = "det"
         popWord(sent,lemmaList,uposList,xposList,morpList,i)
         i = 0
      i = i + 1
   return ruleActions

def possConstructionRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):
   i = 0
   while i < len(sent) - 1:
     if i == 0 or (i > 0 and "ve[Conj]" not in morpList[i-1]):
       
       if ("Noun" in morpList[i] or "Pron" in morpList[i] or ("Verb" and "Noun" in morpList[i])) and ("Noun" in morpList[i+1] or "Pron" in morpList[i+1] or ("Verb" and "Noun" in morpList[i+1])):
          index = int(sent[i].split('#',1)[1])
         
          
          if "[Gen]" in morpList[i] and isPossessive(morpList[i+1]):

             
             ruleActions[index] = "nmo"
             popWord(sent,lemmaList,uposList,xposList,morpList,i)
             i = 0

          elif i < len(sent)-2 and ruleActions[int(sent[i+1].split('#',1)[1])] == "c":
            
             
             ruleActions[index] = "nmo"
             popWord(sent,lemmaList,uposList,xposList,morpList,i)
             i = 0

          elif "[Nom]" in morpList[i] and isPossessive(morpList[i+1]):
               
           
             ruleActions[index] = "nmo"
             popWord(sent,lemmaList,uposList,xposList,morpList,i)
             i = 0

     i = i + 1
    
         
   return ruleActions



def advAdjRule(sent, lemmaList, uposList, xposList, morpList, ruleActions, tempAdvList):
   global specAdvList
   i = 0
   while i < len(sent) - 1:
      
      word = sent[i].split('#',1)[0]
      word = word.lower()
      index = int(sent[i].split('#',1)[1])

      if "[Adv]" in morpList[i] and "[Adj]" in morpList[i+1] : 
                   
         # specAdvFile = open('./rule-based-model/QuantityDegreeAdvList.txt','r')
         # specAdvList = specAdvFile.readlines()
         if word+"\n" in specAdvList:
           
            ruleActions[index] = "adv"
                
            for ind,(a,b) in enumerate(tempAdvList):
                if b == sent[i]:   
                   comp_ind = a.split('#',1)[1]
                   comp_ind = int(comp_ind)
                   ruleActions[comp_ind] = "adv"
                   tempAdvList.pop(ind)
                                         
            popWord(sent,lemmaList,uposList,xposList,morpList,i)
            i  = 0
                            
      i = i + 1

   return ruleActions

def advVerbRule(sent, lemmaList, uposList, xposList, morpList, ruleActions, tempAdvList):
  
   i = 0
   while i < len(sent) - 1:

      if i > 0 and "[Adv]" in morpList[i] and ("Verb" in morpList[i+1] or ruleActions[int(sent[i+1].split('#',1)[1])] == "c"):
         
         word = sent[i].split('#',1)[0]
         word = word.lower()
         index = int(sent[i].split('#',1)[1])

         w_b = sent[i-1].split('#',1)[0]
                    
         if word not in ["bile","önce","sonra"]:
           
            ruleActions[index] = "adv"
            popWord(sent,lemmaList,uposList,xposList,morpList,i)
            i = 0
               
         elif word in ["bile"] or ( word in ["önce","sonra"] and "[Abl]" in morpList[i-1]):

            ruleActions[index] = "adv"
            popWord(sent,lemmaList,uposList,xposList,morpList,i)
            i = 0

      i = i + 1

   return ruleActions

def adjVerbRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):

   i = 0
   while i < len(sent) - 1:
             
      if "[Adj]" in morpList[i] and ("Verb" in morpList[i+1] or ruleActions[int(sent[i+1].split('#',1)[1])] == "c"):
               
         index = int(sent[i].split('#',1)[1])
           
         ruleActions[index] = "amo"
         popWord(sent,lemmaList,uposList,xposList,morpList,i)
         i = 0
      i = i + 1
   return ruleActions

def nounVerbRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):

   i = 0
   while i < len(sent) - 1:
             
      if ("Noun" in morpList[i] or "Pron" in morpList[i]) and ("Verb" in morpList[i+1] or ruleActions[int(sent[i+1].split('#',1)[1])] == "c"):
               
         index = int(sent[i].split('#',1)[1])
           
         ruleActions[index] = "nsu"
         popWord(sent,lemmaList,uposList,xposList,morpList,i)
         i = 0
      i = i + 1
   return ruleActions


def mweRule(sent, lemmaList, uposList, xposList, morpList, ruleActions):

   i = 0
   while i < len(sent) - 1:
             
      
      if "|" in sent[i].split('#',1)[0]:

         word = sent[i].split('#',1)[0].lower()
         ind = sent[i].split('#',1)[1]
         mwe_word = word.split('|',1)[1]
         word = word.split('|',1)[0]

         if mwe_word == word + sent[i+1].split('#',1)[0].lower():
           # print("first")
            index = int(sent[i+1].split('#',1)[1])            
            ruleActions[index] = "cop"
            popWord(sent,lemmaList,uposList,xposList,morpList,i+1)
            sent[i] = word+'#'+ind
            i = 0
         elif mwe_word == word + sent[i+1].split('#',1)[0].lower() + sent[i+2].split('#',1)[0].lower():
           # print("second")
            index = int(sent[i+1].split('#',1)[1])            
            ruleActions[index] = "cop"
            index2 = int(sent[i+2].split('#',1)[1])            
            ruleActions[index2] = "cop"
            popWord(sent,lemmaList,uposList,xposList,morpList,i+2)
            popWord(sent,lemmaList,uposList,xposList,morpList,i+1)
            sent[i] = word+'#'+ind
            i = 0

      i = i + 1
   return ruleActions


def rule_based_parser(sent,lemmaList, uposList, xposList, morpList):

    realUposList = []
    ruleActions = []
    tempAdjList = []
    tempAdvList = []

    for tag in uposList:
        realUposList.append(tag)
      
    for i in range(0,len(sent)):
        
        ruleActions.append("_")
        sent[i] = sent[i] + "#" + str(i)


    ruleActions = mweRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
    ruleActions = numberRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
        
    ruleActions, tempAdvList = find_adv_compounds(sent,lemmaList,uposList,xposList,morpList,ruleActions)
    tempAdjList = find_adj_compounds(sent,lemmaList,uposList,xposList,morpList)

    ruleActions = complexPredicateRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
    ruleActions = properNounRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
    ruleActions = wordCompoundRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
    ruleActions = detNounRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
    ruleActions = adpRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)

    i = 0
    for i in range(0,len(sent)):
       ruleActions = advAdjRule(sent, lemmaList, uposList, xposList, morpList, ruleActions, tempAdvList)
       ruleActions = adjNounRule(sent, lemmaList, uposList, xposList, morpList, ruleActions, tempAdjList)
       ruleActions = possConstructionRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)     
   #    ruleActions = advVerbRule(sent, lemmaList, uposList, xposList, morpList, ruleActions, tempAdvList)
   #    ruleActions = adjVerbRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
   #    ruleActions = nounVerbRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)
   #    ruleActions = accDatLocRule(sent, lemmaList, uposList, xposList, morpList, ruleActions)

       i = i + 1

    for i,tag in enumerate(realUposList):
        realUposList[i] = ruleActions[i]


    return realUposList


def writeToConllFile(ruleList, filename):

    newFileName = "ruled-"+filename
    f = codecs.open(filename, encoding='utf-8', errors='ignore')
    f_new = codecs.open(newFileName, "w", "utf-8")

    i = 0
    for line in f:
       line = line.strip()

       if line.startswith('#'):
          f_new.write(line+"\n")
       elif len(line) == 0:
          f_new.write(line+"\n")
          
       elif re.match('^[0-9]+[-.][0-9]+\t', line):
          f_new.write(line+"\n")
       else:
          cols=line.split("\t")
          #if cols[9] == "_":
           #  cols[9] = ruleList[i]
          #else:
           #  cols[9] = ruleList[i]+"|"+cols[9]
          cols[9] = ruleList[i]
          i = i + 1
          f_new.write(str(cols[0]+"\t"+cols[1]+"\t"+cols[2]+"\t"+cols[3]+"\t"+cols[4]+"\t"+cols[5]+"\t"+cols[6]+"\t"+cols[7]+"\t"+cols[8]+"\t"+cols[9]+"\n"))


def dontWriteToConllFilePlease(ruleList, text):

    out = ""
    i = 0
    lines = text.split("\n")
    for line in lines:
       line = line.strip()

       if line.startswith('#'):

          out += line+"\n"
       elif len(line) == 0:
          out += line+"\n"
          
       elif re.match('^[0-9]+[-.][0-9]+\t', line):
          out += line+"\n"
       else:
          cols=line.split("\t")
          #if cols[9] == "_":
           #  cols[9] = ruleList[i]
          #else:
           #  cols[9] = ruleList[i]+"|"+cols[9]
          cols[9] = ruleList[i]
          i = i + 1
          out += str(cols[0]+"\t"+cols[1]+"\t"+cols[2]+"\t"+cols[3]+"\t"+cols[4]+"\t"+cols[5]+"\t"+cols[6]+"\t"+cols[7]+"\t"+cols[8]+"\t"+cols[9]+"\n")
    return out

def to_conllu(text):

  wordList = []
  lemmaList = []
  uposList = []
  xposList = []
  morpList = []
 
  allRules = []
  mwe_flag = 0
  lines = text.split("\n")
  for line in lines:
     line = line.strip()
     
     if len(line) == 0:
       ruleList = rule_based_parser(wordList,lemmaList,uposList,xposList,morpList)
       allRules = allRules + ruleList

       wordList = []
       lemmaList = []
       uposList = []
       xposList = []
       morpList = []

     if len(line) > 0 and not line.startswith('#'):
       if re.match('^[0-9]+[-.][0-9]+\t', line):
          mwe_flag = 1
          mwe_word = line.split("\t")[1]

       if not re.match('^[0-9]+[-.][0-9]+\t', line):

         cols=line.split("\t")
         if mwe_flag == 1:
            wordList.append(cols[1]+"|"+mwe_word)
         else:
            wordList.append(cols[1])
         lemmaList.append(cols[2])
         uposList.append(cols[3])
         if "|" in cols[4]:
            xposList.append(cols[4].split('|')[0].split('=')[1])
         else:
            xposList.append(cols[4])
         morpList.append(cols[8])
         
         mwe_flag = 0
           
      
  return dontWriteToConllFilePlease(allRules, text)
     

         
if __name__=="__main__":

    filename = sys.argv[1]
   
    f=codecs.open(filename, encoding='utf-8', errors='ignore')

    wordList = []
    lemmaList = []
    uposList = []
    xposList = []
    morpList = []
   
    allRules = []
    mwe_flag = 0

    for line in f:
       line = line.strip()
       
       if len(line) == 0:
         ruleList = rule_based_parser(wordList,lemmaList,uposList,xposList,morpList)
         allRules = allRules + ruleList

         wordList = []
         lemmaList = []
         uposList = []
         xposList = []
         morpList = []

       if len(line) > 0 and not line.startswith('#'):
         if re.match('^[0-9]+[-.][0-9]+\t', line):
            mwe_flag = 1
            mwe_word = line.split("\t")[1]

         if not re.match('^[0-9]+[-.][0-9]+\t', line):

           cols=line.split("\t")
           if mwe_flag == 1:
              wordList.append(cols[1]+"|"+mwe_word)
           else:
              wordList.append(cols[1])
           lemmaList.append(cols[2])
           uposList.append(cols[3])
           if "|" in cols[4]:
              xposList.append(cols[4].split('|')[0].split('=')[1])
           else:
              xposList.append(cols[4])
           morpList.append(cols[8])
           
           mwe_flag = 0
             
        
    writeToConllFile(allRules, filename)
       
    



             
             
