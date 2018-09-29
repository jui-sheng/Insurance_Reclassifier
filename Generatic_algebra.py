import pandas as pd
import glob
import random
import os
from datetime import datetime

from funcLibrary import *

class generatic_Algebra:
  def __init__(self, first, last, cross_rate, mutation_rate, max_mutation_occur, max_mutation, epochs, total_chromosome, total_classification, reproduction_rate, main_path):
    '''
    Generatic Algebra Initialize Function

    :param first: List Type
      Insert first 3 year List
    :param last: List Type
      Insert first 3 year List
    :param cross_rate: Float Type
      0 ~ 1
    :param mutation_rate: Float Type
      0 ~ 1
    :param epochs: Int Type
      1 ~ Any
    :param total_chromosome: Int Type
      Above 4, Even Number
    :param total_classification: Int Type
      Above 30
    '''
    self.first = first
    self.last = last
    self.cross_rate = cross_rate
    self.mutation_rate = mutation_rate
    self.max_mutation_occur = max_mutation_occur
    self.max_mutation = max_mutation
    self.epochs = epochs
    self.total_chromosome = total_chromosome
    self.total_classification = total_classification
    self.max_cross = 10
    self.reproduction_rate = reproduction_rate
    self.main_path = main_path

    '''
    default load path setting
    '''
    self.load_group = []
    self.load_epoch = 0
    self.load_path = ""

    self.__read__()

#  Testing use
#  def __init__(self):
#    print("empty")

  def __read__(self):
    list = glob.glob(".\After_Process\Company\*")
    list2 = glob.glob(".\After_Process\monthly_process\*") # 原本claim_monthly_process -> monthly_process
    first3year_company = [i for i in list for j in self.first if j in i]
    last3year_company = [i for i in list for j in self.last if j in i]

    first3year_claim = [i for i in list2 for j in self.first if j in i]
    last3year_claim = [i for i in list2 for j in self.last if j in i]

    df_first = get3Years(first3year_company, first3year_claim)
    df_last = get3Years(last3year_company, last3year_claim)
    print("intersection")
    self.df_first, self.df_last = getIntersection(df_first.copy(), df_last.copy())
    
    # read the latest industry type
    print("read latest")
    df_latest = pd.read_csv('.\After_Process\Company\Company-2015.txt', sep='\t')
    df_latest = df_latest.drop_duplicates('投保證號').reset_index(drop=True)
    #print('更換行業別細類(業別)以company-2015為主，共有 %s '%len(df_latest['行業別細類(業別)'].unique()))

    print("replace old to latest")
    # replace old industry type to latest
    self.df_first = replaceIndustryType(self.df_first, df_latest)
    self.df_last = replaceIndustryType(self.df_last, df_latest)

    print("create Distance Table")
    self.table = createDistanceTable(self.df_last)
    # print(self.table)

  def start(self):
    epoch = self.load_epoch
    self.validation_list = []
    self.loss_list = []
    self.groupLists = []
    min_dict= {'min':float('Inf'), 'group':newClassification(self.df_first, self.total_classification)}

    # Generate New Chromosome
    if len(self.load_group) == 0:
      groupList = [newClassification(self.df_first, self.total_classification) for i in range(0, self.total_chromosome)]
    else:
        groupList = self.load_group
    self.groupLists.append(groupList.copy())
 #   fp = open('geneRecord.txt', 'w');
    date = datetime.now().__str__().split('.')[0].replace(' ', '-').replace(':', '.')
    # pathdir = './Results/' + date
    if self.load_path != "":
      pathdir = self.load_path
    else:
      pathdir = os.getcwd() + '\\Results\\' + self.main_path + date

    '''
    save arguments
    '''
    arguments_name = ["first", "last", "cross_rate", "mutation_rate", "max_mutation_occur", "max_mutation", "epochs", "total_chromosome", "total_classification", "reproduction_rate", "main_path"]
    arguments = [self.first, self.last, self.cross_rate, self.mutation_rate, self.max_mutation_occur, self.max_mutation, self.epochs, self.total_chromosome, self.total_classification, self.reproduction_rate, self.main_path]
    argument_path = pathdir + '\\argument.txt'

    if not os.path.exists(pathdir):
      os.mkdir(pathdir)

    with open(argument_path, 'w') as fp:
      for name in arguments_name:
        fp.write(name+"\t")
      fp.write("\n")
      for argument in arguments:
        fp.write(str(argument)+"\t")
      fp.write("\n")

    path = pathdir + '\\result.txt'
    path2 = pathdir + '\\min-group.txt'
    path3 = pathdir + '\\records.txt'


    while epoch < self.epochs:
      random.seed(datetime.now())
      loss_list = [getLoss(self.df_first, i, self.table) for i in groupList]
      print('Generatic is running ')
      # record all epoch min-group(add on)
      # path2 = pathdir + '/min-group-%d.txt' %epoch

      # avg_loss = [getLoss_Average(self.df_first, i) for i in groupList]
      self.loss_list.append(loss_list.copy())

      # print(loss_list)
      # print(type(loss_list), type(loss_list[0]))
      # print(min(loss_list))
      temp_min = loss_list.index(min(loss_list))

      if min_dict['min'] > loss_list[temp_min]:
        min_dict['min'] = loss_list[temp_min]
        min_dict['group'] = groupList[temp_min]
        #print(min_dict)

      curr = groupList[loss_list.index(min(loss_list))]
      curr['first_給付金額'] = self.df_first['first_給付金額']
      curr['last_給付金額'] = self.df_first['last_給付金額']
      # curr['diff_給付金額'] = [math.pow(self.df_first.loc[j,'給付金額'] - self.df_last.loc[j,'給付金額'], 2) for j in range(0, len(self.df_first))]
      curr['行業別細類(業別)'] = self.df_first['行業別細類(業別)']

      self.curr = curr[['投保證號', 'group', '行業別細類(業別)', 'first_給付金額', 'last_給付金額']]
      self.sorted_curr = curr.sort_values(['group'])[['投保證號', 'group', '行業別細類(業別)', 'first_給付金額', 'last_給付金額']]

      if not os.path.exists('Results'):
        os.mkdir('Results')

      with open(path, 'a') as fp:
        fp.write("epochs %d : Max Loss : %f Min Loss : %f\n" % (epoch + 1, max(loss_list), min(loss_list)))
        # fp.write("epochs %d : Max Average Loss : %f Min Average Loss : %f\n" % (epoch + 1, max(avg_loss), min(avg_loss)))
        fp.flush()


      # write min result
      with open(path2, 'w') as file:
        file.write("epoch:%d  loss = %d\n" %(epoch, min_dict['min']))
      min_dict['group'].to_csv(path2, mode='a', sep='\t', index=False)

      if os.path.exists(path3):
         os.remove(path3)

      for group_1 in groupList:
        group_1.to_csv(path3, mode='a', sep='\t', index=False)

      groupList = tournament_selection(groupList, loss_list, self.reproduction_rate, min_dict['group'])

      print("epochs %d : Max Loss : %f Min Loss : %f" % (epoch + 1, max(loss_list), min(loss_list)))
      # validation_list = [validation(self.df_first, self.df_last, i) for i in groupList]
      # self.validation_list.append(validation_list.copy())
      # groupList = random_selection(groupList, validation_list)
      print(datetime.now().__str__().split('.')[0].replace(' ', '-'))
      self.groupLists.append(groupList.copy())
      for j in range(0, len(groupList), 2):
        if (random.uniform(0, self.max_cross) <= self.max_cross * self.cross_rate):
          groupList[j], groupList[j+1] = twoPointCross(groupList[j], groupList[j+1])

      for i in range(0, len(groupList), 1):
        if (random.uniform(0, self.max_mutation_occur) <= self.max_mutation_occur * self.mutation_rate):
          # mutation(groupList[i], self.total_classification)
          multi_mutation(groupList[i], self.total_classification, self.max_mutation)
      epoch+=1
#    fp.close()

  def load(self, path, total_chromosome):
    # read epoch file
    last_line = ""
    with open("%s/result.txt" %path) as fp:
      for line in fp:
        last_line = line

    df = pd.read_csv("%s/records.txt" %path, sep='\t')
    total_len = len(df)
    total_len -= total_chromosome - 1
    each_chromosome_len = int(total_len / total_chromosome)
    df_array = []

    for i in range(total_chromosome):
      df_array.append(df[i * each_chromosome_len + i: (i+1) * each_chromosome_len + i].astype(float).reset_index(drop=True))
    self.load_path = path
    self.load_group = df_array
    self.total_chromosome = total_chromosome
    self.load_epoch = int(last_line.split(" ")[1])

# print(datetime.now().__str__().split('.')[0].replace(' ', '-'))
