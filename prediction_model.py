# -*- coding: utf-8 -*-
"""Final Arima.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17Nf2lzo4DNPL2sSEgEW_I3yGNDVOFv6G

**ARIMA** **MODEL**

**What is SARIMA?**\
Seasonal Autoregressive Integrated Moving Average, **SARIMA** or **Seasonal ARIMA**, is an extension of ARIMA that explicitly supports univariate time series data with a **seasonal component**.

**Modules required to implement SARIMA?**
>pip3 install numpy scipy patsy pandas<br>
>pip3 install statsmodels<br>
>pip install seaborn<br>
>pip install matplotlib<br>
"""

import numpy as np #This is used to import numpy library
import pandas as pd #This is used to import pandas library

data_path = "/content/drive/MyDrive/Adrima Pred/AIML_CASE.xlsx" #Path for the file

#Use This Code if the file is CSV type
#df=pd.read_csv(data_path,parse_dates=True) 

#This is used to read EXCEL file
df=pd.read_excel(data_path,parse_dates=True)

from matplotlib import style
import matplotlib.pyplot as plt
import seaborn as sns
import pprint
 
fig = plt.figure()
ax1 = plt.subplot2grid((1,1), (0,0))
 
style.use('ggplot')
 
#ploting graph of Date vs Data
sns.lineplot(x=df["DATE"], y=df["DATA"], data=df)
sns.set(rc={'figure.figsize':(15,6)})
 
plt.title("CPU comsuption")
plt.xlabel("Date")
plt.ylabel("comsuption")
plt.grid(True)
plt.legend()
 
for label in ax1.xaxis.get_ticklabels():
    label.set_rotation(90)
 
 
plt.title("Energy Consumption According to Date")

"""**Data Imputation**"""

df.isna().sum() #This code return you the number of nan (null) values in the respective column

df.dropna() #To Remove the nan(null) values in each columns row

print('Shape of data',df.shape,"no. of (row,column)") # To get the no. of rows and columns (row,column)

df.head() #This display the first 5 rows of the dataframe

"""Since the time is in **12 hours** format<br>
***timeConversion*** function convert the **12hours** time into **24 hours** time by cheacking the **AM/PM** columns **data**
"""

mod_df = df.copy() #copy the dataframe
cols_to_merge = mod_df.columns[:-1]

print("Merging columns:", cols_to_merge)
mod_df['DateAndTime'] = mod_df[cols_to_merge].apply(
    lambda x: pd.to_datetime(" ".join(x.astype(str))), axis=1
)


keep = ["DateAndTime", "DATA"]
to_remove_cols = [i for i in mod_df.columns if i not in keep]

print("\nRemoving columns", to_remove_cols, "\n")

mod_df.drop([*to_remove_cols], inplace=True, axis=1)

#mod_df.set_index("DateAndTime", inplace=True)  # converting datetimes to dataframe index

display(mod_df.head())  # display sameple of the modified data

#mod_df["DateAndTime"] = mod_df["DateAndTime"].dt.strftime('%H:%M:%s')

mod_df

'''
!pip3 uninstall statsmodels
!pip3 install numpy scipy patsy pandas
!pip3 install statsmodels
'''

#ignore harmless warnings
import warnings
warnings.filterwarnings("ignore")

# This Code generate next month date with time (15 min diff)
nextMonth = []
st = pd.Timedelta(minutes=0)
m = mod_df["DateAndTime"].iloc[-1]
for i in range (2976):
     st = m +pd.Timedelta(minutes=15)
     m = st
     nextMonth.append(st)

nextDf = pd.DataFrame(nextMonth,columns=["DateAndTime"])
nextMonthForcast = nextDf.copy()
nextMonthForcast["DATA"] = 0

nextMonthForcast

conDf = pd.concat([mod_df,nextMonthForcast]) # join main dataframe with next month dataframe
trainEndDf = conDf["DATA"].iloc[:len(df)]
nextMonthForcast = nextDf.set_index("DateAndTime")
mod_df = mod_df.set_index("DateAndTime")

conDf = conDf.reset_index()
conDf.drop('index', inplace=True, axis=1)

conDf

#Ho: It is non stationary
#H1: It is stationary
from statsmodels.tsa.stattools import adfuller

#P-value determain wheather the data is stationary or not
def adfuller_test(sales):
    result=adfuller(sales)
    labels = ['ADF Test Statistic','p-value','#Lags Used','Number of Observations Used']
    for value,label in zip(result,labels):
        print(label+' : '+str(value) )
    if result[1] <= 0.05:
        print("strong evidence against the null hypothesis(Ho), reject the null hypothesis. Data has no unit root and is stationary")
    else:
        print("weak evidence against null hypothesis, time series has a unit root, indicating it is non-stationary ")

adfuller_test(mod_df["DATA"])

"""Here P-value is 0.01 which is less than 0.05, which means data is not accepting the null hypothesis, which means data is stationary."""

fig = plt.figure()
ax1 = plt.subplot2grid((1,1), (0,0))
 
style.use('ggplot')
 
#Graph of DateAndTime vs Data 
sns.lineplot(x=mod_df.index, y=mod_df["DATA"], data=df)
sns.set(rc={'figure.figsize':(15,6)}) #setting the graph size
 
plt.title("CPU comsuption")
plt.xlabel("DateAndTime")
plt.ylabel("comsuption")
plt.grid(True)
plt.legend()
 
#Roate the Date to 90 degree
for label in ax1.xaxis.get_ticklabels():
    label.set_rotation(90)
 
#Title of graph
plt.title("Mits Consumption According to Date")

total = len(mod_df) #total no. of train and prediction dataset
mod_conDf = conDf.set_index("DateAndTime")

train_set = mod_conDf.iloc[:total,:]

#import SARIMA model
from statsmodels.tsa.statespace.sarimax import SARIMAX
 
 
#SARIMA
my_order = (1,1,3)
my_seasonal_order = (1,1,1,12)
 
model = SARIMAX(train_set,order=my_order,seasonal_order=my_seasonal_order)
result = model.fit()

train_set

pred=result.predict(typ='levels') # model predict for test dataset

actual_set = mod_conDf.iloc[:total,:]

expected = np.array(actual_set) 
predictions = np.array(pred)

# RMS ERROR (ROOT MEAN SQUARE ERROR)
# This is used to stydy the model quality
from sklearn.metrics import mean_squared_error
from math import sqrt
mse = mean_squared_error(expected , predictions)
rmse = sqrt(mse)
print('RMSE: %f' % rmse)



nextPred=result.predict(start=total+1,end=total*2,typ='levels') # model predict for test dataset
nextPred

def check_weekday(pred,date):
    # computing the parameter date
    # with len function
    res=len(pd.bdate_range(date,date))
      
    if res == 0 :
      return 1
    else:
      return pred

dataframe = pd.DataFrame()
dataframe["DateAndTime"] = mod_conDf.index[total:total*2] #prediction date and time
dataframe["predicted_data"] = nextPred.values #predicted data

#setting the weekend to zero
dataframe["predicted_data"] = dataframe.apply(lambda pred:  0 if check_weekday(pred["predicted_data"],pred["DateAndTime"]) == 1 else pred["predicted_data"] ,axis=1)
dataframe = dataframe.set_index("DateAndTime")

dataframe

import matplotlib.pyplot as plt #importing module for displaying graph
# graph of actual (actual valuw) value vs predicted value
actual_set.plot(legend=True,label="Actual Data")
pred.plot(legend=True,label="Predicted Data")

#Prediction for next month
dataframe.plot(legend=True,label="Next Predicted Data")

actual_set

pred

plt.plot(pred.index,dataframe["predicted_data"].values)

#Note : pred has a diffrent month but has same day and time
plt.plot(pred.index,pred.values)



predicted_file_name = "prediction.csv" # final file name
dataframe.to_csv(predicted_file_name) # to save the predicted  data into CSV

"""**----------------END-------------------**"""

