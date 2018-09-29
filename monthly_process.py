import pandas as pd
import numpy as np
import os

claim_path = '.\\After_Process\\Claim\\'
personal_path = '.\\After_Process\\personal_process\\'
output_path = '.\\After_Process\\monthly_process\\'

multiply = 1000
'''
Create File
'''
create_path = ''
for i in output_path.split('\\'):
  if i == '.':
    create_path += '.'
  elif i is not '':
    create_path += '\\' + i
    if not os.path.exists(create_path):
      os.mkdir(create_path)


'''
Doing Process
'''
# title = ['投保證號', '地區別','核付年月','行業別細類(業別)','是否為職業工會','職災費率編號','職災費率','行業別費率','實績費率','實績費率增減率','職災當月保費應繳金額', 'avg %d' %multiply]
title = ['投保證號', '核付年月', '給付金額', 'avg %d' %multiply]
# claim_dir_list = os.listdir(claim_path)
claim_dir_list = ['Claim-2008.txt', 'Claim-2011.txt']

for i in claim_dir_list:
  df_claim = pd.read_csv(claim_path + i, sep='\t')
  df_claim = df_claim[['投保證號', '核付年月', '給付金額']]

  # Calculate the total money belongs of that month and insure account
  df_claim = df_claim.groupby(['投保證號', '核付年月']).agg('sum')
  df_claim = df_claim.reset_index()

  year = i.split('-')[1][:-4]
  df_new = pd.DataFrame()
  for j in range(1, 13):
    print(year, j)
    df_monthly = df_claim[df_claim['核付年月'] % 100 == j].sort_values(by='投保證號').reset_index(drop=True)

    df_personal_count = pd.read_csv(personal_path + year + '/%d.txt' %j)
    inter = set(df_monthly['投保證號']).intersection(set(df_personal_count['保險證號']))
    df_personal_count = df_personal_count[df_personal_count['保險證號'].isin(inter)]
    diff = set(df_monthly['投保證號']).difference(set(df_personal_count['保險證號']))
    df_personal_count = df_personal_count.append(pd.DataFrame({'保險證號' : list(diff), 'count': 1})).sort_values(by='保險證號')
    df_personal_count = df_personal_count.reset_index(drop=True)
    l = 0
    for k in range(0, len(df_monthly)):
      if l < len(df_personal_count) - 1:
        if (df_personal_count.loc[l, '保險證號'] == df_monthly.loc[k, '投保證號']):
          df_monthly.loc[k, 'avg %d' % multiply] = df_monthly.loc[k, '給付金額'] * multiply / df_personal_count.loc[l, 'count']
        l+=1
      else:
        break
    df_new = df_new.append(df_monthly)

  df_new.reset_index(drop=True)
  df_new.to_csv(output_path + "%s.txt" %year, index=False)
