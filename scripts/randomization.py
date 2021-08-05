import sys
import re
import os
import codecs
import fileinput
import argparse
import random


if __name__=="__main__":

   f_filename1 = sys.argv[1]
   f_filename2 = sys.argv[2]
   f_filename_gold = sys.argv[3]
   repeat_num = sys.argv[4]

   f1=codecs.open(f_filename1, encoding='utf-8', errors='ignore')
   f2=codecs.open(f_filename2, encoding='utf-8', errors='ignore')
   fgold = codecs.open(f_filename_gold,  encoding='utf-8', errors='ignore')

   sents1 = f1.read().split("\n\n")

   sents1 = sents1[:-1]

   sents2 = f2.read().split("\n\n")

   sents2 = sents2[:-1]

   gold_sents = fgold.read().split("\n\n")

   gold_sents = gold_sents[:-1]


   model1_vec_uas = []
   model2_vec_uas = []
   model1_vec_las = []
   model2_vec_las = []

   for sent1,sentg in zip(sents1,gold_sents):

      lines_all1 = sent1.split("\n")
      lines1 = [line for line in lines_all1 if not line.startswith("#")]
      lines_1 = [line for line in lines1 if not "-" in line.split("\t")[0]]

      lines_gold = sentg.split("\n")
      linesgold = [line for line in lines_gold if not line.startswith("#")]
      lines_gold = [line for line in linesgold if not "-" in line.split("\t")[0]]


      for line1, lgold in zip(lines_1, lines_gold):

         #print(line1, lgold)
         cols1 = line1.split("\t")
         cols_gold = lgold.split("\t")
         
         #print(cols1, cols_gold)
         if cols1[6] == cols_gold[6]: #changed this for morp. they were 6 before for dep
            model1_vec_uas.append(1)
            if cols1[7] == cols_gold[7]:
               model1_vec_las.append(1)
    
            else:
               model1_vec_las.append(0)
         else:
            model1_vec_uas.append(0)
            model1_vec_las.append(0)


   for sent2,sentg in zip(sents2,gold_sents):

      lines_all2 = sent2.split("\n")
      lines2 = [line for line in lines_all2 if not line.startswith("#")]
      lines_2 = [line for line in lines2 if not "-" in line.split("\t")[0]]

      lines_gold = sentg.split("\n")
      linesgold = [line for line in lines_gold if not line.startswith("#")]
      lines_gold = [line for line in linesgold if not "-" in line.split("\t")[0]]


      for line2, lgold in zip(lines_2, lines_gold):

         cols2 = line2.split("\t")
         cols_gold = lgold.split("\t")
         
         #print(cols2,"******",cols_gold)
         if cols2[6] == cols_gold[6]: #changed this for morp. they were 6 before for dep
            model2_vec_uas.append(1)
            if cols2[7] == cols_gold[7]:
               model2_vec_las.append(1)
            else:
               model2_vec_las.append(0)
         else:
            model2_vec_uas.append(0)
            model2_vec_las.append(0)

   print("model1: ")
   print("uas: ",sum(model1_vec_uas)/len(model1_vec_uas))
   print("las: ",sum(model1_vec_las)/len(model1_vec_las))
   print("model2: ")
   print("uas: ",sum(model2_vec_uas)/len(model2_vec_uas))
   print("las: ",sum(model2_vec_las)/len(model2_vec_las))


   model1_uas_sum = sum(model1_vec_uas)
   model1_las_sum = sum(model1_vec_las)

   model2_uas_sum = sum(model2_vec_uas)
   model2_las_sum = sum(model2_vec_las)

  # print(len(model1_vec_uas)," ",len(model2_vec_uas))
  # print(model1_uas_sum)
  # print(model2_uas_sum)
  # print(model1_las_sum)
  # print(model2_las_sum)

         
#### for UAS ####

   real_diff_uas = model1_uas_sum - model2_uas_sum

   fake_model1 = model1_vec_uas
   fake_model2 = model2_vec_uas

   diff_count = 0
   for i in range(0,int(repeat_num)):
      for j in range(0,len(model1_vec_uas)):

          flip = random.randint(0, 1)

          if flip == 1:
             temp = fake_model1[j]
             fake_model1[j] = fake_model2[j]
             fake_model2[j] = temp

      new_sum_model1 = sum(fake_model1)
      new_sum_model2 = sum(fake_model2)
      
      if (real_diff_uas > 0 and (new_sum_model1 - new_sum_model2) > real_diff_uas) or (real_diff_uas <= 0 and (new_sum_model2 - new_sum_model1) > -1*real_diff_uas) :
         diff_count = diff_count + 1


  # print(diff_count)
   print("UAS p-val:")
   print((diff_count+1)/(int(repeat_num)+1))
   
#### for LAS ####

   real_diff_las = model1_las_sum - model2_las_sum

   fake_model1 = model1_vec_las
   fake_model2 = model2_vec_las

   diff_count = 0
   for i in range(0,int(repeat_num)):
      for j in range(0,len(model1_vec_las)):

          flip = random.randint(0, 1)

          if flip == 1:
             temp = fake_model1[j]
             fake_model1[j] = fake_model2[j]
             fake_model2[j] = temp

      new_sum_model1 = sum(fake_model1)
      new_sum_model2 = sum(fake_model2)
      
      
      if ( real_diff_las > 0 and (new_sum_model1 - new_sum_model2) > real_diff_las) or  ( real_diff_las <= 0 and (new_sum_model2 - new_sum_model1) > -1*real_diff_las) :
         diff_count = diff_count + 1


   #print(diff_count)
   print("LAS p-val:")
   print((diff_count+1)/(int(repeat_num)+1))
