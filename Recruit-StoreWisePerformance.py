
# coding: utf-8

#Kaggle kernel for the Recruit Restaurant Visitor Forecasting. 
# <https://www.kaggle.com/c/recruit-restaurant-visitor-forecasting>


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import folium
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.


# In the earlier kernel, we have seen that there are stores with no customers on a given day. 
# The number of such stores peaks in the latter part of the data set. In this kernel, we will
# identify storewise performance, by looking at number of vistors at each store, during the 
# entire duration.



#read airstore data and read store IDs into a list
airstore = pd.read_csv('../input/air_store_info.csv')
print (airstore.head())
airstorelist = list(airstore['air_store_id'])
print (len(airstorelist))




#read the air visit data and read the date range into a list
airvisit = pd.read_csv('../input/air_visit_data.csv')
airvisit['visit_date'] = pd.to_datetime(airvisit['visit_date']).dt.date
print (airvisit.head())
datelist = list(airvisit['visit_date'].unique())
print (len(datelist))




#test sample values at a random store
parstore = airvisit[airvisit['air_store_id'] == 'air_0f0cdeee6c9bf3d7']
parstore.tail()




#create a new dataframe with store id and date combination
from itertools import product
dailystorevisits = pd.DataFrame(list(product(airstorelist, datelist)), columns=['air_store_id', 'visit_date'])
dailystorevisits['visit_date'] = pd.to_datetime(dailystorevisits['visit_date']).dt.date
print (dailystorevisits.head())




#read the number of visitors to each store, every day, by merging with the airvisit data
dailystorevisits = pd.merge(dailystorevisits, airvisit, how='left', on=['visit_date', 'air_store_id'])
dailystorevisits['visitors'] = dailystorevisits['visitors'].fillna(0)
#print (dailystorevisits.head())
dailystorevisits.describe()


# Since a lot of stores were started after July 2016, all those stores will have 0 visitors before that time. To avoid marking up new stores as underperforming stores, let us do the analysis after August 2016. Filtering the data set to reflect this change.



import datetime as dt
dailystorevisits = dailystorevisits[dailystorevisits['visit_date'] > dt.date(2016, 8, 1)]
dailystorevisits.describe()




sns.distplot(dailystorevisits['visitors'], bins=200)
plt.xlabel('number of visitors per day')
plt.ylabel('normalized count')
plt.show()


# **Number of store days with no customers**
# 
# We will look at the total number of store days with no customers. 



totstoredays = len(dailystorevisits)
print ('total number of store days: ',  totstoredays)

nocuststoredays = len(dailystorevisits[dailystorevisits['visitors'] == 0])
print ('total number of store days with no customers: ',  nocuststoredays)




frac = 1. * nocuststoredays/totstoredays
print ('Percentage of store days with no customers is: ', 100*frac)


# Storewise performance
# 
# Let us look at the performance of each store -  mean, min and maximum number of visitors to each place.



swp = dailystorevisits.groupby(dailystorevisits['air_store_id'], as_index=False).mean()
swp.describe()
#swp.head()


# We see that mean number of vistiors to any store, on a given day is around 18. While the maximum number of mean visitors is 51, a quarter of stores have less than 10 visitors on average. 
# 



plt.hist(swp['visitors'], bins=50, normed=True)
plt.xlabel('average number of visitors per day')
plt.ylabel('normalized count')
plt.show()


# We can see that a significant number of stores have less than 10 customers a day, on average.  The fraction of these stores compared to the total number of stores is
# 



print ('Percentage of stores recieving less than 10 visitors on average are:  ' , 100 * len(swp[swp['visitors'] < 10])/len(swp))


# Let us see if the cuisine has any effect on the number of visitors. Mapping the cusine to restaurant, by merging data frames. 

# **Cuisine and visitors**
# 
# Let us now plot the cuisines of restuarants with lowest number of mean visitors per day



dst = pd.merge(swp, airstore, how='left', on='air_store_id')
plt.hist(dst[dst['visitors'] <  10]['air_genre_name'])
plt.xlabel('average number of visitors per day')
plt.ylabel('normalized count')
plt.xticks(rotation='vertical')
plt.show()


# Fron this plot, we can see that a large number of Bar/Cocktail stores have least visitors.  The next cuisines with least footfalls are Izakaya and Dining bar. 

# **Geographical location of low performing stores**



#Marking high and low performance stores by number of visitors
hpstores = dst[dst['visitors'] > 30]
lpstores = dst[dst['visitors'] < 10]




map_osm = folium.Map(location=[40, 140], zoom_start=5)
for lng, lat, desc in zip(hpstores['longitude'], hpstores['latitude'], hpstores['air_genre_name']):
    folium.Marker([lat, lng], popup=desc, icon = folium.Icon(color='blue')).add_to(map_osm)
    

for lng, lat, desc in zip(lpstores['longitude'], lpstores['latitude'], lpstores['air_genre_name']):
    folium.Marker([lat, lng], popup=desc, icon = folium.Icon(color='red')).add_to(map_osm)
map_osm


# We can see the geographical location of high performance stores, where average number of visitors is more than 30 marked in blue, and low performance stores, where average number of visitors is less than 10 marked in red, on the map.
# 





