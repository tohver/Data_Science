
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    dane=open('university_towns.txt', 'r')
    #ss=State
    ss=[]
    row=[]
    #rn=RegionName
    rn=[]
    for i in dane:
        if '[edit]' in i:
            s=i[:i.index('[')].strip()
            #continue, inaczej wrzuca nowy stan i poprzednie miasto
            continue
        elif '(' in i:
            rn=i[:i.index('(')].strip()
        else:
            rn=i
        row.append([s,rn])
    df=pd.DataFrame(row, columns=['State', 'RegionName'])
    return df
get_list_of_university_towns()


# In[4]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdp=pd.read_excel('gdplev.xls', skiprows=7)
    gdp=gdp[['Unnamed: 4', 'Unnamed: 6']]
    #lub: c=gdp.loc[:,['Unnamed: 4', 'Unnamed: 6']]
    gdp.columns=['Quarter', 'GDP']  
    gdp=gdp[gdp['Quarter']>'2000']
    # tutaj musi być '2' w: range (2,len(gdp)) bo: porownujemy z 2 poprzednimi. Inaczej: error
    for i in range (2, len(gdp)):
        if (gdp.iloc[i,1]<gdp.iloc[i-1,1]) and (gdp.iloc[i-1,1]<gdp.iloc[i-2,1]):
            # -1, bo chodzi o 1 kwartal kiedy PKB spadlo, nie -2: kiedy bylo max
            rec_start=gdp.iloc[i-1][0]
            return rec_start
get_recession_start()


# In[5]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''        
    gdp=pd.read_excel('gdplev.xls', skiprows=7)
    gdp=gdp[['Unnamed: 4', 'Unnamed: 6']]
    #lub: c=gdp.loc[:,['Unnamed: 4', 'Unnamed: 6']]
    gdp.columns=['Quarter', 'GDP']
    gdp=gdp[gdp['Quarter']>get_recession_start()]
    
    for i in range (2, len(gdp)):
        if (gdp.iloc[i,1]>gdp.iloc[i-1,1]) and (gdp.iloc[i-1,1]>gdp.iloc[i-2,1]):
            rec_end=gdp.iloc[i,0]
            return rec_end   
get_recession_end()


# In[6]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''    
    gdp=pd.read_excel('gdplev.xls', skiprows=7)
    gdp=gdp[['Unnamed: 4', 'Unnamed: 6']]
    gdp.columns=['Quarter', 'GDP']
    a=gdp[gdp['Quarter']>=get_recession_start()] 
    b=a[a['Quarter']<=get_recession_end()]
    bottom=b[b['GDP']==b['GDP'].min()].values[0,0]
    
    return bottom
get_recession_bottom()


# In[7]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    #new columns
    a = list(range(2000,2017))
    b = ['q1','q2','q3','q4']
    output = []
    for i in a:
        for j in b:
            output.append((str(i)+j))
    new_col=output[:67]

    df=pd.DataFrame()

    path='City_Zhvi_AllHomes.csv'
    hs=pd.read_csv(path)
    hs['State']=hs['State'].map(states)
    hs.set_index(['State', 'RegionName'], inplace=True)
    hs.drop(hs.loc[:,:'1999-12'].columns, axis=1, inplace=True)
    a=[list(hs.columns)[i:i+3] for i in range (0, hs.shape[1],3)]
    build=list(zip(new_col,a))
    for i,j in build:
        df[i]=hs[j].mean(axis=1)
    return df
convert_housing_data_to_quarters()
    


# In[20]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    import scipy as sp
    #porownanie czyli run_ttest()
    #h - house prices; st - start of recession, bt - bottom of recession, ut - university towns
    h=convert_housing_data_to_quarters() # dataframe
    st=get_recession_start() # a string
    bt=get_recession_bottom()  # a string
    ut=get_list_of_university_towns().set_index(['State', 'RegionName'])

    # price of houses in this 2 years
    prices=h[[st, bt]]    
    prices['ratio']=prices.iloc[:,0]/prices.iloc[:,1]

    # Two datasets to compare (univ. towns vs. other cities)
    # uni towns -> merging
    uni_ratio=pd.merge(ut, prices, how='inner', left_index=True, right_index=True)['ratio'].dropna()
    
    # 
    not_uni_index=set(prices.index)-set(ut.index)
    not_uni_ratio=prices.loc[list(not_uni_index),:]['ratio'].dropna()

    
    better=''
    if uni_ratio.mean()<not_uni_ratio.mean():
        better='university town'
    else: 
        better='non-university town'
    
    test=sp.stats.ttest_ind(uni_ratio, not_uni_ratio)
    p_value=test[1]
    if float(list(test)[1])<0.01: different=True
    else: different=False
    a=(different, p_value, better)
    return a
run_ttest()


# In[ ]:



