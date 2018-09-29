import pandas as pd
import glob
from funcLibrary import *
import numpy as np


claim_path = ".\After_Process\monthly_process\*"
company_path = ".\After_Process\Company\*"


list_claim = glob.glob(claim_path)
list_company = glob.glob(company_path)


first_list = ['2009', '2010', '2011']
last_list = ['2013', '2014', '2015']


first_claim_list = sorted([i for i in list_claim for j in first_list if j in i])
last_claim_list = sorted([i for i in list_claim for j in last_list if j in i])


first_company_list = sorted([i for i in list_company for j in first_list if j in i])
last_company_list = sorted([i for i in list_company for j in last_list if j in i])


first_df = get3Years(first_company_list, first_claim_list)
last_df = get3Years(last_company_list, last_claim_list)

first_group = first_df[['投保證號', '行業別細類(業別)']].rename({'行業別細類(業別)':'group'}, axis=1)
last_group = last_df[['投保證號', '行業別細類(業別)']].rename({'行業別細類(業別)':'group'}, axis=1)

# read the latest industry type
df_latest = pd.read_csv('.\After_Process\Company\Company-2015.txt', sep='\t')
df_latest = df_latest.drop_duplicates('投保證號').reset_index(drop=True)

first_group = replaceIndustryType(first_group, df_latest)
last_group = replaceIndustryType(last_group, df_latest)

# 6 years
first, last = getIntersection(first_df.copy(), last_df.copy())

# first = replaceOriginalIndustryType(first.copy(), './行業標準分類第九次修訂(edited).xlsx')

first['group'] = first['行業別細類(業別)']
first['行業別細類(業別)'] = first['group']
# first = first.drop('行業別細類(業別)', axis=1)

table = createDistanceTable(first)


def getLossOriginal(df_first, group, distanceTable):
  """
  Lost Function
  :param df_first: first 3 year claim , last 3 year claim
  :param group: classifier group set
  :return: Loss DataFrame
  """
  groupSet = sorted(set(group['group']))
  lossList = []
  for i in groupSet:
    index = int(i)
    cur = group[group['group'] == index]
    df_first_cur = df_first[df_first['投保證號'].isin(cur['投保證號'])].reset_index(drop=True)
    # print(df_first_cur)
    loss = []

    # Fill Zero
    new_df = fillZero(df_first_cur['行業別細類(業別)'].astype(int).astype(str), 4)

    combi = combinations(new_df.unique(), 2)
    print(combination(len(df_first_cur['行業別細類(業別)'].unique()), 2))
    # Calculate Loss
    for j in range(0, len(df_first_cur)):
      loss.append(df_first_cur.loc[j, 'first_給付金額'] - df_first_cur.loc[j, 'last_給付金額'])
    #lossList.append(math.pow(sum(loss),2) )#測試拔掉distancetable
    #lossList.append(math.pow(sum(loss),2) * sumDistance(new_df, distanceTable) / combination(new_df, 2))
    #lossList.append(math.pow(sum(loss),2) * calcKIndustryType(new_df, distanceTable))
   
    lossList.append(math.pow(sum(loss),2) * calcDefault(new_df, distanceTable))

  fitness_loss = math.fabs(sum(lossList))
  return fitness_loss

loss = getLossOriginal(first.copy(), first.copy(), table)

print('loss= ',loss)
# print('未處理(first)-行業別細類(業別)= ',len(first_df['行業別細類(業別)'].unique()))
# print('未處理(last)-行業別細類(業別)= ',len(last_df['行業別細類(業別)'].unique()))
# print('first.shape= ',first_df.shape)
# print('last.shape= ',last_df.shape)

# print('查看投保證號數量= ',len(first_df['投保證號'].unique()))
# print('查看投保證號數量= ',len(last_df['投保證號'].unique()))

# len(first_df['行業別細類(業別)'].unique())
# ours = 153204534504969404416
# print("Diff with the ours = ", ours - loss)
