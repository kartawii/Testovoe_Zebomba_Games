#!/usr/bin/env python
# coding: utf-8

# 3)	На основе тестовых таблиц payment.csv и users.csv постройте отчёт в системе аналитики (powerBI), содержащий графики отражающие динамику следующих показателей в зависимости от количества дней прошедших с даты регистрации пользователя и принимает следующие значения 3,7,14,28 день
# 
# - % платящих
# - ARPU 
# - ARPPU 
# - Retention 
# 

# In[1]:


# Ипортируем необходимые библиотеки
import pandas as pd
import numpy as np
import datetime as dt


# In[2]:


# создаем df из csv-файлов
payment = pd.read_csv('payment.csv')
payment.columns =['id','transaction_time','amount']

users = pd.read_csv('users.csv')


# In[3]:


#меняем тип данных даты
payment['transaction_time'] = pd.to_datetime(payment['transaction_time'])
payment['transaction_time'] = payment['transaction_time'].dt.to_period('D')

users['create'] = pd.to_datetime(users['create'])
users['create'] = users['create'].dt.to_period('D')


# In[4]:


# Изменяем тип данных в каждой строчке столбца ретеншен, удалю все NaN
users_up = users.dropna().reset_index(drop=True)
for i in range(len(users_up['retention'])):
    users_up['retention'][i] = [int(x) for x in users_up['retention'][i].split(',')]
users_up


# In[5]:


# Соединяем таблицы
df = payment.merge(users_up, on='id', how='inner')
display(df.head())
display(df.tail())


# ## Стоит заметить что мы потеряли 1 строчку из таблицы payment, это произошло потому что у этого ID не было даты регистрации, я бы отправил баг-репорт

# In[6]:


# Вычисляем сколько прошло дней с регистрации при совершении платежа
df['day_when_pay'] = df['transaction_time'] - df['create']
df['day_when_pay'] = df['day_when_pay'] / np.timedelta64(1, 'D')
df['day_when_pay'] = df['day_when_pay'].astype('int')
display(df.head())
display(df.tail())


# In[7]:


# Создам итоговую таблицу, к которой буду прилеплять все вычисления
a = []
for i in range(29):
    a.append(i)
final_table = pd.DataFrame(a)
final_table.columns = ['lifetime']
final_table['count_payers'] = final_table['lifetime']


# In[8]:


# Вычисляем количество платящих
for i in range(final_table['lifetime'].min(), final_table['lifetime'].max()+1):
    final_table['count_payers'][i] = df[df['day_when_pay']<=i]['id'].nunique()
final_table.head()


# In[9]:


# Вычисляем процент платящих
final_table['percent_payers'] = round(final_table['count_payers'] / users['id'].nunique(),2)
final_table.head()


# In[10]:


# Вычисляем ARPU и ARPPU
final_table['ARPU'] = final_table['lifetime']
for i in range(final_table['lifetime'].min(), final_table['lifetime'].max()+1):
    final_table['ARPU'][i] = df[df['day_when_pay']<=i]['amount'].sum()
final_table['ARPPU'] = round(final_table['ARPU']/df['id'].nunique(),2)
final_table['ARPU'] = round(final_table['ARPU']/users['id'].nunique(),2)
final_table.head()


# In[11]:


# Вычисляем classic Retention
final_table['Retention'] = final_table['lifetime']
for i in range(final_table['lifetime'].min(), final_table['lifetime'].max()+1):
    final_table['Retention'][i] = users_up[users_up['retention'].map(lambda v: i in v)]['id'].nunique()
final_table


# In[12]:


# загружаю полученную таблицу в файл, чтобы продолжить работу в Power BI
# final_table.to_csv('final_table.csv')


# ## Возникли проблемы с Power BI, рисовал мне не то что нужно, не успеваю подробнее разобраться, заканчивается отведенное время,  поэтому сделаю функцию прям тут, которая принимает значение дней, и возвращает 4 графика:

# In[13]:


import plotly.express as px


# In[14]:


def draw_graphs(day):
    fig1 = px.line(final_table[final_table.lifetime < day], x ='lifetime', y ='percent_payers',title='Percent_payers')
    fig1.show()
    fig2 = px.line(final_table[final_table.lifetime < day], x ='lifetime', y ='ARPU',title='ARPU')
    fig2.show()
    fig3 = px.line(final_table[final_table.lifetime < day], x ='lifetime', y ='ARPPU',title='ARPPU')
    fig3.show()
    fig4 = px.line(final_table[final_table.lifetime < day], x ='lifetime', y ='Retention',title='Retention')
    fig4.show()


# In[17]:


display(draw_graphs())


# In[ ]:




