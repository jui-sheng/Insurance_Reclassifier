import pandas as pd
import glob

title = ['大類','中類','小類','細類']

df = pd.read_excel('.\行業標準分類第九次修訂.xls', names=title)

##  Begin Job Process

# clean the nan row
df = df.dropna(how='all')

# record the data
big = 0
mid = 0
small = 0

# fill the nan as the actual value
for i in range(0, len(df)):
  if pd.isna(df.iloc[i, 0]):
    df.iloc[i, 0] = big
  else:
    big = df.iloc[i, 0]

  if pd.isna(df.iloc[i, 1]):
    df.iloc[i, 1] = mid
  else:
    mid = df.iloc[i, 1]

  if pd.isna(df.iloc[i, 2]):
    df.iloc[i, 2] = small
  else:
    small = df.iloc[i, 2]


df.to_csv('.\行業標準分類第九次修訂(edited).xls', sep='\t', encoding='utf-8',header=title, index=False)
df[df.iloc[:, 3] == 111].iloc[:, 3][0]

df[df.iloc[:, 3] == 2420]
# change those 細類 Table to 大類 Table
replace_col = 0;


list = glob.glob('.\After_Process\Company\*')
list = [i for i in list if i[32:36] > '2012']

from funcLibrary import *

df_main = pd.read_csv(list[0], sep='\t')
#
# for i in list:
#   df_main = pd.read_csv(i, sep='\t')
#   for j in range(0, len(df_main)):
#     # print(df_main.loc[j, '行業別細類(業別)'])
#     df_main.loc[j, '行業別細類(業別)'] = df[(df.iloc[:, 2]/10).astype(int) == int(df_main.loc[j, '行業別細類(業別)']/ 100)].iloc[0, replace_col][0]
#
#   df_main.to_csv('./After_Process/Big_Company/' + i.split('/')[3])
df_main
title = df_main['行業別細類(業別)']

for (i, j) in iter(title):
  print(i, j)
title

from itertools import  *
a = combinations(title, 2)
for i in a:
  print(i)

print(df_main['行業別細類(業別)'].shape[0])

sumDistance(a) / combination(df_main['行業別細類(業別)'].shape[0], 2)