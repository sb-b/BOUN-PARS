#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os

#SpecAdvList = ["en", "az", "daha", "hep", "biraz", "böyle","çok","þöyle","öyle","adeta","niçin"]
#SpecAdvList = ['þimdi','böyle','kendiliðinden','hemen','sadece','sonra','bazen','esasen','yine','hep','gerçekten','niye','zaten','ne','aslýnda','beraberce','hala','sanki','sonunda','dolayýsýyla','acaba','aynen','iþte','oysa','yeniden','ardýndan','artýk','birlikte','herhalde','yalnýzca','genellikle','onca','bunca']

def find_nearest_verb(uposList):
    if "VERB" in uposList:
      return True
    else:
      return False


def rule_based_parser(sent,uposList, xposList, morpList):

    ruleActions = []
    for i,w in enumerate(sent):
       if uposList[i] == "ADV":
          if i < len(sent) and uposList[i+1] == "ADJ" and xposList[i+1] == "Adj":
             specAdvFile = open('/home/betul/turkunlp/Turku-neural-parser-pipeline/Parser-v2/nparser/scripts/SpecAdvList.txt','r')
             specAdvList = specAdvFile.readlines()
             if w not in specAdvList:
                ruleActions.append("dn")
             
             elif find_nearest_verb(uposList):
                ruleActions.append("dv")
             else:
                ruleActions.append("dr")
          
          elif i < len(sent) and uposList[i+1] == "VERB":
             ss = u"önce"
             print(ss)
             u = ss.decode('utf8')
             print(u)
             if w not in ["bile",u,"sanki"]:
               ruleActions.append("dn")
             else:
               ruleActions.append("dp")

          else:
             ruleActions.append("uk")

       elif uposList[i] == "ADJ" and xposList[i] == "Adj":
          if i < len(sent) and (uposList[i+1] == "NOUN" or (uposList[i+1] == "VERB" and "VerbForm=Vnoun" in morpList[i+1])):
             ruleActions.append("jn")
          else:
             ruleActions.append("uk")


       else:
          ruleActions.append("uk")

    for i,tag in enumerate(uposList):
       uposList[i] = tag + "_" + ruleActions[i]

    return uposList


if __name__=="__main__":


    sent = ["daha","uzun","bir","isim","verseydin"]
    uposList = ["ADV","ADJ","NUM","NOUN","VERB"]
    xposList = ["Adverb","Adj","ANum","Noun","Verb"]
    morpList = ["","","NumType=Card","Case=Nom","Tense=Past"]

    ss = u"\00F6nce"
    print(ss)
    u = ss.decode('utf8')
    print(u)

    newUposList = rule_based_parser(sent,uposList,xposList,morpList)
    s="XPOS=Prop|Case=Gen|Number=Sing|Person=3"
    splits = s.split('|', 1)
    print(splits[0])
    print(newUposList)



             
             
