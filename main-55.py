from Generatic_algebra import *

first3year = ['2009', '2010', '2011']
last3year =  ['2013', '2014', '2015']
# old (first, last, cross_rate, mutation_rate, epochs, total_chromosome, total_classification, reproduction):

# (first, last, cross_rate, mutation_rate, max_mutation_occur, max_mutation, epochs, total_chromosome, total_classification, reproduction_rate, main_path)




a = generatic_Algebra(first3year, last3year, 0.8, 0.3, 1000, 1000, 1000, 10, 55, 0.2, 'group55-')
#a.load("Results/group495-2018-09-08-01.07.12", 10)
a.start()

# print(a.load_group[0][0:1]['group'])
#
# print(a.load_group[0][0:1]['group'].astype(float))

# testing
# a = generatic_Algebra()




# print(a.loss_list)

# '''
# Temporary Code
# import pandas as pd
# import glob as glob
# import math
#
# list = glob.glob("./After_Process/Company/*")
# list2 = glob.glob("./After_Process/claim_monthly_process/*")
# first3year_company = [i for i in list for j in first3year if j in i]
# last3year_company = [i for i in list for j in last3year if j in i]
#
# first3year_claim = [i for i in list2 for j in first3year if j in i]
# last3year_claim = [i for i in list2 for j in last3year if j in i]
#
# first_company = get3Years(first3year_company, first3year_claim)
# last_company = get3Years(last3year_company, last3year_claim)
#
# print(len([i for i in first_company['給付金額'] if not math.isnan(i)]))
# print(len([i for i in first_company['給付金額'] if math.isnan(i)]))
#
# print(len([i for i in last_company['給付金額'] if not math.isnan(i)]))
# print(len([i for i in last_company['給付金額'] if math.isnan(i)]))
#
#
# first, last = getIntersection(first_company.copy(), last_company.copy() )
#
# first = first.fillna(0)
#
#
# for i in first:
#   print(i)
#   break
#
# nan_list = [i for i in range(0,len(first)) if math.isnan(first.loc[i,'last_給付金額']) and math.isnan(first.loc[i,'給付金額'])]
# a = pd.DataFrame({'a':[0,1,2,3]})
# b = pd.DataFrame({'a':[4,5,6,7]})
# a = a.append(b)
#
#
# # testing random selection
#
#
# glist = pd.DataFrame({'A':[1,2,3],'B':[1,2,3]})
# list = [glist , glist.loc[:, 'A']*5, glist*8]
# loss = [10,1,1]
# print(random_selection(list, loss))
# total = sum(loss)
# a = [1 / i  for i in loss]
# print(a)
# print(sum(a))

