
import pandas as pd
import numpy as np
import math
import random
from itertools import  *

#**
#

money = 'avg 1000'

'''
company_list put 3 years company and use it to get '投保證號','實績費率','職災費率'
claim_list put 3 years claim list and use it to sum the company claim
'''
def get3Years(company_list, claim_list) :

  # get the 3 years company and Process
  df_company_list = []
  df_company_list.append(pd.read_csv(company_list[0], encoding="utf-8", sep='\t', low_memory=False))
  df_company_set = set(df_company_list[0]['投保證號'])

  for i in range(1,3):
    df_company_list.append(pd.read_csv(company_list[i], encoding="utf-8", sep='\t', low_memory=False))
    df_company_set = df_company_set.intersection(set(df_company_list[i]['投保證號']))

  print('input total Company df Length = %d' %len(df_company_set)) #三年期間公司['投保證號']數量(交集後)

  df_company = df_company_list[0][df_company_list[0]['投保證號'].isin(df_company_set)]
  for i in range(1,3):
    df_company = df_company.append(df_company_list[i][df_company_list[i]['投保證號'].isin(df_company_set)])

  df_company = df_company[['投保證號','實績費率','職災費率', '行業別細類(業別)']]
  df_company = df_company.drop_duplicates(['投保證號'])

  print(claim_list)
  # get the 3 years claim and Process
  df_claim = pd.read_csv(claim_list[0], encoding="utf-8", sep=',', low_memory=False)

  for i in range(1, 3):
    df_claim.append(pd.read_csv(claim_list[i], encoding="utf-8", sep=',', low_memory=False))

  # df_claim = df_claim_list[0][df_claim_list[0]['投保證號'].isin(df_claim_set)]
  # for i in range(1, 3):
  #   df_claim = df_claim.append(df_claim_list[i][df_claim_list[i]['投保證號'].isin(df_claim_set)])
  
  df_claim = df_claim[['投保證號', money]]
  print('input total Claim df Length = %d' %len(set(df_claim['投保證號']).intersection(df_company_set)))#三年期間理賠['投保證號']數量(交集後)


  df_claim = df_claim.groupby("投保證號").sum()

  df_company = df_company.join(df_claim, how='left', on='投保證號').reset_index(drop=True)
  df_company.reset_index(drop=True)
  print('output dataframe length = %d' %len(df_company))
  return df_company

def newClassification(df, classification_count):
  classlist = [random.randint(0, classification_count - 1) for i in range(0, len(df))]
  temp = pd.DataFrame({'投保證號':df['投保證號'], 'group': classlist})
  return temp

'''
df_first : first 3 year dataset
df_last : last 3 year dataset
Get those Dataframe Intersection
return (df_first, df_last)
'''
def getIntersection(df_first, df_last):
  first_set = set(df_first['投保證號'])
  last_set = set(df_last['投保證號'])
  inter_set = first_set.intersection(last_set)
  # print(inter_set)
  # print(first_set)
  # print(last_set)
  last = df_last[df_last.iloc[:]['投保證號'].isin(inter_set)].reset_index(drop=True)
  first = df_first[df_first.iloc[:]['投保證號'].isin(inter_set)].reset_index(drop=True)
  first = first.rename(columns={money: 'first_給付金額'})
  first['last_給付金額'] = last[money]
  first = first.fillna(0)
  print('first確認交集後投保證號= %d' %len(first['投保證號'].unique()))
  print('last確認交集後投保證號= %d' %len(last['投保證號'].unique()))
  return first, last


def getLoss_Average(df_first, group):
  """
  Lost Function
  :param df_first: first 3 year data
  :param df_last: last 3 year data
  :param group: classifier group set
  :return: Loss DataFrame
  """
  groupSet = sorted(set(group['group']))
  lossList = []
  for i in groupSet:
    index = int(i)
    cur = group[group['group'] == index]
    df_first_cur = df_first[df_first['投保證號'].isin(cur['投保證號'])].reset_index(drop=True)
    loss = []
    for j in range(0, len(df_first_cur)):
      loss.append(math.pow(df_first_cur.loc[j, 'first_給付金額'] - df_first_cur.loc[j, 'last_給付金額'], 2))
    avg_loss = sum(loss) / len(df_first_cur)

    lossList.append(sum([ avg_loss - i for i in loss]))


    # loss = sum(df_first_cur['給付金額']) - sum(df_last_cur['給付金額'])
    # loss = math.pow(loss, 2)
    # df_loss = df_loss.append({'group':index, '給付金額' : loss}, ignore_index=True)
  fitness_loss = math.fabs(sum(lossList))
  return fitness_loss

def getLoss(df_first, group, distanceTable):
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



    # combi = combinations(new_df.unique(), 2)

    # Calculate Loss
    for j in range(0, len(df_first_cur)):
      loss.append(df_first_cur.loc[j, 'first_給付金額'] - df_first_cur.loc[j, 'last_給付金額'])




    # lossList.append(math.pow(sum(loss),2) * sumDistance(combi, distanceTable) / combination(len(df_first_cur['行業別細類(業別)'].unique()), 2))
    # lossList.append(math.pow(sum(loss),2) * calcKIndustryType(new_df, distanceTable))
    lossList.append(math.pow(sum(loss),2) * calcKWithBatch(new_df, distanceTable, 50))


  fitness_loss = math.fabs(sum(lossList))
  return fitness_loss

def calcDiffer(x):
  loss = []

  x = x.reset_index(drop=True)
  for i in range(len(x)):
    loss.append(x.loc[i, 'first_給付金額'] - x.loc[i, 'last_給付金額'])
  return sum(loss)

def calcDefault(new_df, distanceTable):
  if(len(new_df) == 1) :
    return 1

  combi = combinations(new_df, 2)
  total_distance = sumDistance(combi, distanceTable)
  combination_count = combination(len(new_df), 2)
  return total_distance / combination_count

def calcKIndustryType(new_df, distanceTable):
  combi = combinations(new_df.unique(), 2)
  total_distance = sumDistance(combi, distanceTable)
  combination_count = combination(len(new_df.unique()), 2)
  return total_distance / combination_count

def calcKWithBatch(new_df, distanceTable, batch_size):
  avg_distance = 0
  batch_count = int(len(new_df) / batch_size)
  for i in range(batch_count):
    curr_df = new_df[i * batch_size: (i + 1) * batch_size]
    combi = combinations(curr_df, 2)
    total_distance = sumDistance(combi, distanceTable)
    combination_count = combination(len(new_df.unique()), 2)
    avg_distance += total_distance / combination_count
  return avg_distance / batch_count

def Optimize(df_first, df_last, group):
  """
  Recalculate Insure Fare Rate
  :param df_first: first 3 year data
  :param df_last: last 3 year data
  :param group: classifier group set
  :return: update group rate
  """
  optimizeList = []
  claim_first = df_first
  claim_last = df_last


def calculateRate(rate, first_loss, last_loss):
  return last_loss * rate / first_loss

def validation(df_first, df_last, group):
  '''
  Validation or Fitness Function
  :param df_first:
  :param df_last:
  :param group:
  :return:
  '''
  groupSet = sorted(set(group['group']))
  lossList = []
  for i in groupSet:
    index = int(i)
    cur = group[group['group'] == index]
    # df_first_cur = df_first[df_first['投保證號'].isin(cur['投保證號'])]
    df_last_cur = df_last[df_last['投保證號'].isin(cur['投保證號'])]
    avg_last_claim = sum(df_last_cur['給付金額']) / len(df_last_cur)
    loss = sum([i - avg_last_claim for i in df_last_cur['給付金額']])
    lossList.append(loss)
  validation_loss = sum(lossList)
  return validation_loss



def adaptation_function(validation_list):
  sum_validation = sum(validation_list)
  list = [1 - i / sum_validation for i in validation_list]
  sum_list = sum(list)
  return [i / sum_list for i in list]


def random_selection(group_list, validation_list):
  '''
  Random Select good chromosome
  :param group_list: old group_list
  :param validation_list: loss_list
  :return: new group list
  '''
  # print(len(group_list))
  # sum_validation = sum(validation_list)
  # list = [1 -  i / sum_validation for i in validation_list]
  # sum_list = sum(list)
  # list = [i / sum_list for i in list]
  list = adaptation_function(validation_list)

  random_max = 10 * len(group_list)
  range_list = [0]
  for i in range(0, len(list)-1):
    range_list.append(range_list[i] + random_max * list[i])

  range_list.append(random_max + 1)

  new_group_list = []
  for i in range(0, len(group_list)):
    ran = random.uniform(0, random_max)
    for j in range(0, len(range_list) - 1):
      if(ran >= range_list[j] and ran < range_list[j+1]):
        new_group_list.append(group_list[j])
        break;
  return new_group_list


def twoPointCross(group, group2):
  temp = group.copy()
  temp2 = group2.copy()
  ran1 = random.randint(0, len(group) - 1)
  ran2 = random.randint(0, len(group) - 1)
  if ran1 > ran2:
    ran1, ran2 = ran2, ran1
  # print(ran1, ran2)
  for i in range(ran1, ran2):
    temp.loc[i, 'group'], temp2.loc[i, 'group'] = temp2.loc[i, 'group'], temp.loc[i, 'group']
  return temp, temp2

def mutation(group, classification_count):
  ranG = random.randint(0, len(group) - 1)
  # print(ran)
  group.loc[ranG,'group'] = random.randint(0, classification_count - 1)

def multi_mutation(group, classification_count, max_mutation):
  ran = random.randint(max_mutation / 2, max_mutation)
  # print(ran)
  for i in range(0, ran):
    ranG = random.randint(0, len(group) - 1)
    group.loc[ranG,'group'] = random.randint(0, classification_count - 1)

def cross(d1, d2):
  '''
  Testing Function
  :param d1:
  :param d2:
  :return:
  '''
  data = d1.copy()
  data2 = d2.copy()
  ran1 = random.randint(0, len(data))
  ran2 = random.randint(0, len(data))
  if ran1 > ran2:
    ran1 ,ran2 = ran2, ran1

  for i in range(ran1, ran2):
    data.iloc[i]['a'] = data2.iloc[i]['a']
  # print(data)
  return data

def tournament_selection(group_list, validation_list, reproduction_rate, min_group):
  list = adaptation_function(validation_list)
  random_max = 10 * len(group_list)
  range_list = [0]
  max_reproduction_rate = 100
  # min_group = validation_list.index(min(validation_list))
  for i in range(0, len(list)-1):
    range_list.append(range_list[i] + random_max * list[i])

  range_list.append(random_max + 1)
  best = 0
  new_group_list = []
  # print(list)

  lowest = random.randint(0, len(group_list) - 1)

  for i in range(0, len(group_list)):
    for l in range(0, random.randint(3,6)):
      temp_group = pd.DataFrame(columns=['index', 'adaptation'])
      ran = random.randint(0, random_max)
      # doing the tournament selection and get the most high adaptation

    # if random.randint(0, max_reproduction_rate) <= max_reproduction_rate * reproduction_rate :
    #   new_group_list.append(min_group)
    # else:
    #   new_group_list.append(group_list[best])

    # if random.randint(0, max_reproduction_rate) <= max_reproduction_rate * reproduction_rate :
    #   new_group_list.append(min_group)

    if i == lowest:
      new_group_list.append(min_group)
    elif random.randint(0, max_reproduction_rate) <= max_reproduction_rate * reproduction_rate :
        new_group_list.append(min_group)
    else:
      for j in range(0, len(range_list) - 1):
        if (ran >= range_list[j] and ran < range_list[j + 1]):
          temp_group = temp_group.append(pd.DataFrame([{'index': j, 'adaptation': list[j]}]))
          break;

      # The Best (Highest)
      best = int(temp_group[temp_group['adaptation'] == temp_group['adaptation'].max()]['index'])
      new_group_list.append(group_list[best])

  return new_group_list

# a = [0,1,2,3,4,5]
#
# a[int(temp_group[temp_group['adaptation'] == temp_group['adaptation'].max()]['index'])]
#
# temp_group = temp_group.append(pd.DataFrame({'index': 1, 'adaptation': [1]}))
#
# temp_group.dtypes
#
# temp = pd.DataFrame([{'a':2,'b':1}])
#
# temp = temp.append( pd.DataFrame([{'a':0,'b':4}]))
#
# print(int(temp[temp['a'] == temp['a'].max()]['a']))

def replaceIndustryType(a, df_latest):
  # df = pd.read_csv('./After_Process/Company/Company-%d.txt' % latest_year, sep='\t')
  # df = df.drop_duplicates('投保證號').reset_index(drop=True)
  inter = set(a['投保證號']).intersection(set(df_latest['投保證號']))
  df = df_latest[df_latest['投保證號'].isin(inter)].reset_index(drop=True)
  k = 0;
  for i in range(len(a)):
    if k == len(df):
      break
    if(a.loc[i,'投保證號'] == df.loc[k,'投保證號']):
      a.loc[i,'行業別細類(業別)'] = df.loc[k,'行業別細類(業別)']
      k+=1;
  return a

def calcDistance(a, b):
  # num1 is large , num2 is small
  if countNumber(a) > countNumber(b):
    num1 = a
    num2 = b
  else:
    num1 = b
    num2 = a
  distance = 0
  if num2 == num1:
    return distance + 1
  elif num2 == num1/10:
    # return distance + len(num1) - len(num2)
    return distance + 1
  else:
    distance += calcDistance(int(num1/10), num2) + 1
  return distance


def calcDistanceByString(a, b):
  # num1 is large , num2 is small
  if len(a) > len(b):
    num1 = a
    num2 = b
  else:
    num1 = b
    num2 = a
  distance = 0
  if(num2 == num1):
    return distance + 1
  if num2 == num1[: -1]:
    # return distance + len(num1) - len(num2)
    return distance + 1
  else:
    distance += calcDistanceByString(num1[:-1], num2) + 1
  # print('distance', distance)
  return distance

def sumDistance(a, distanceTable):

  sumDistance = 0


  # print('calculate totle Distance')
  for (idx, i) in enumerate(a):
    sumDistance += distanceTable[i[0]][i[1]]

  return sumDistance


def sumDistance2(a, distanceTable):
  sumDistance = 0
  # print('calculate totle Distance')
  for (idx, i) in enumerate(a):
    sumDistance += distanceTable[i[0]][i[1]]

  return sumDistance

def combination(a, b):
  result = 1
  if(a < b):
    return False
  if(a-b > b):
    diff = a-b
    num = b
  else:
    diff = b
    num = a-b
  if(a != b):
    for i in range(diff + 1, a + 1):
      result *= i
  for j in range(1,num + 1):
    result /= j
  return  result

def countNumber(a):
  number = 0;
  while a > 0:
    number += 1
    a = int(a / 10)
  return number

def createDistanceTable(a):

  unique_industry_type = a['行業別細類(業別)'].unique().astype(int).astype(str)

  # print(unique_industry_type)

  unique_industry_type = fillZero(unique_industry_type, 4)

  # Create Zero Distance Table
  table = pd.DataFrame({i: {j: 0 for j in unique_industry_type} for i in unique_industry_type})
  for i in unique_industry_type:
    for j in unique_industry_type:
      table[i][j] = calcDistanceByString(i, j)
  print('table created')
  return table

def fillZero(a , b):
  # Fill zero to get length 4
  for idx, i in enumerate(a):
    if len(i) < b:
      for j in range(b - len(i)):
        a[idx] = '0' + i

  return a



def replaceOriginalIndustryType(a, replaceVersion):
  l = []
  for i in range(len(a)):
    l.append('0')
  a['大類'] = l
  df_type = pd.read_excel(replaceVersion).astype('str');
  for i in range(len(a)):
    curr = (df_type[df_type['細類'] == str(int(a.loc[i,'行業別細類(業別)']))]['大類'])
    if (curr.iloc[0] != None):
      a.loc[i, '大類'] = curr.iloc[0]

  return a

#
# # df = pd.read_csv('After_Process/Company/Company-2014.txt', sep='\t')
# df2 = pd.read_csv('After_Process/Company/Company-2015.txt', sep='\t')
#
# df = df2.copy()
#
# replaceOriginalIndustryType(df.copy(), 0)
#
# replaceOriginalIndustryType(df2.copy(), 0)
#
# df['group'] = df['行業別細類(業別)']
# df.drop('行業別細類(業別)', axis=1)

# #
# not_duplicate = set(df['投保證號']).intersection(set(df2['投保證號']))
# len(df)
# df = df[df['投保證號'].isin(not_duplicate)]
# df = df.reset_index(drop=True)
# # len(df)
# replaceIndustryType(df, df2)
#
# countNumber(1000)
#
# calcDistance(100, 100)
#
# calcDistanceByString('1000', '1')
# temp[111][111] = 100
# type(df['行業別細類(業別)'].unique()[0])
# unique_industry_type = df['行業別細類(業別)'].unique().astype(int).astype(str)
# for idx,i in enumerate(unique_industry_type):
#   if len(i) < 4:
#     for j in range(4-len(i)):
#       unique_industry_type[idx] = '0' + i
# unique_industry_type[0]
# df2
# table = distanceTable(df2)
