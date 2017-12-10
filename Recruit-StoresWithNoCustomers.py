
# coding: utf-8



# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.




# First analysis of data
av = pd.read_csv('../input/air_visit_data.csv')

#format date and time, include weekday, month and year in the dataframe
av['weekday'] = pd.to_datetime(av['visit_date']).dt.dayofweek
av['month'] = pd.to_datetime(av['visit_date']).dt.month
av['year'] = pd.to_datetime(av['visit_date']).dt.year
av['visit_date'] = pd.to_datetime(av['visit_date']).dt.date
print (av.head())




av1 = av[['visit_date', 'visitors']].groupby(['visit_date'], as_index=False).sum()
plt.plot(av1['visit_date'], av1['visitors'])
plt.xlabel('date')
plt.xticks(rotation='vertical')
plt.ylabel('number of daily visitors')
plt.show()


# The number of visitors to the restaurant chain shows a step change, in July 2016. It might be due to increased number of stores, or increased foot fall. Let us examine the number of stores.



av2 = av.groupby(['visit_date'], as_index=False).count()
plt.plot(av2['visit_date'], av2['air_store_id'])
plt.xlabel('date')
plt.xticks(rotation='vertical')
plt.ylabel('number of stores')
plt.show()


# The reason for increased visitors is due to an increase in number of stores. Around July 2016, the number of stores more than doubled. However, it is surprising to see the number of stores varying over time, on a daily basis. This may be due to holidays where there might be no customers at a restaurant. 
# 
# Let us now examine the above plots on working days, by filtering out holidays. To do this, we will merge the holidays column from date_info file into the air visit file.



holidays = pd.read_csv('../input/date_info.csv')
holidays=holidays.rename(columns={'calendar_date':'visit_date'})
holidays['visit_date'] = pd.to_datetime(holidays['visit_date']).dt.date
holidays.head()




#merge the data frames
av3 = pd.merge(av, holidays, how='left', on='visit_date')
print (len(av3))
#remove holidays
av3 = av3[av3.holiday_flg == 0]
print (len(av3))

av3 = av3.groupby(['visit_date'], as_index=False).count()


# There are 252108 entries for all days, while 239333 entries for working days. To check the number of holidays, let us see the number of entries in both data frames as well as number of holidays in the list. The date ranges for air visit data and date info data are different. Using the common date range, we see that the number of holidays are 31. 



#date range in air visits data
mindate = min(av['visit_date'])
maxdate = max(av['visit_date'])
print (mindate, maxdate)

minholiday = min(holidays['visit_date'])
maxholiday = max(holidays['visit_date'])
print (minholiday, maxholiday)

#number of holidays in air visit date range
nh = sum(holidays[(holidays['visit_date']>= mindate) & (holidays['visit_date'] <= maxdate)]['holiday_flg'])
print (nh)

print (len(av2) - len(av3))




plt.plot(av2['visit_date'], av2['air_store_id'], 'red')
plt.plot(av3['visit_date'], av3['air_store_id'], '.')
plt.xlabel('date')
plt.xticks(rotation='vertical')
plt.ylabel('number of stores')
plt.legend(['all days', 'holidays'])
plt.show()


# The red line shows dates including holidays, while blue circles shows data without holidays. Even when holidays are filtered out, we see that the number of stores varies with time. This means that there are stores with no customers, even on working days. 

# **Stores with no customers**
# 
# To find out the number of stores with no customers on a given a day, we first count the total number of stores active on a given day. Then, we find out the maximum & minimum number of outlets active in a given month.



av4 = av
av4['month_year'] = 100*av4['year'] + av4['month']
#print (av4.head())
av4 = av4.groupby(['month_year','visit_date']).agg({'air_store_id': 'count', 'visitors': 'sum'}).reset_index()
print (av4.head())




av5 = av4
av5['max_stores'] = av5['air_store_id']
av5['min_stores'] = av5['air_store_id']




av5 = av4.groupby(['month_year']).agg({'max_stores': 'max', 'min_stores':'min', 'visitors': 'mean'}).reset_index()
av5['date'] = pd.to_datetime(av5['month_year'], format='%Y%m')




print (av5)




plt.plot(av5['date'], av5['max_stores'], '->')
plt.plot(av5['date'], av5['min_stores'], '-o')
plt.plot(av5['date'], av5['max_stores']-av5['min_stores'], '-D')
plt.xlabel('date - month and year')
plt.xticks(rotation='vertical')
plt.ylabel('number of stores')
plt.legend(['max stores', 'min stores', 'stores with no customers'])
plt.show()


# Maximum number of stores active in a given month remains fairly constant over time. As observed earlier, the number of stores more than doubled in July 2016, that accounts for increased number of customers. 
# 
# Minimum number of stores is the smallest number of active stores in a given month. This means that the remaining stores did not recieve any customers on that given day. 
# 
# Number of stores with no customers peaks in Dec 2016 and remains so till Jan 2017, which may be the effect of holiday season.

# To understand this better, we plot the daily number of stores with no customers, by subtracting the number the stores from maximum for that month. 



av6 = pd.merge(av4, av5, how='left', on='month_year')




plt.plot(av6['visit_date'], av6['max_stores_y'] - av6['air_store_id'], '-')
plt.xlabel('date - month and year')
plt.xticks(rotation='vertical')
plt.ylabel('number of stores with no customers')
plt.show()


# The number of stores with no customers shows a weekly variation. In the next kernel, we will examine this dependence on weekday. 
