# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 21:56:10 2021

@author: preci
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web 
import warnings   
from functools import reduce
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
style.use("ggplot")

import plotly.io as pio
import plotly.express as px
from sklearn import preprocessing

pio.renderers.default = "browser"

#%% Opciones para visualizar data frames en consola
pd.set_option("display.max_rows",5000)
pd.set_option("display.max_columns",500)
pd.set_option("display.width",1000)
warnings.filterwarnings("ignore")

from datetime import datetime
import pytz
import zipfile, urllib.request, shutil
import os

#%% FUNCIÓN para extraer URL de los datos
def get_COT(url, file_name):
    
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
        
    with zipfile.ZipFile(file_name) as zf:
            zf.extractall()
            
#%% FUNCION 
get_COT('https://www.cftc.gov/files/dea/history/fut_fin_xls_2021.zip',
        '2021.zip')
get_COT('https://www.cftc.gov/files/dea/history/fut_disagg_xls_2021.zip',
        '2021.zip')


# Renaming
os.rename(r'C:\Users\preci\Documents\proyectos\COT FINANCIAL\FinFutYY.xls',
         r'C:\Users\preci\Documents\proyectos\COT FINANCIAL\FinFut21.xls')
os.rename(r'C:\Users\preci\Documents\proyectos\COT FINANCIAL\f_year.xls',
         r'C:\Users\preci\Documents\proyectos\COT FINANCIAL\DisFut21.xls')


#%%
dis_2018 = pd.read_excel('DisFut18.xls')

dis_2019 = pd.read_excel('DisFut19.xls')

dis_2020 = pd.read_excel('DisFut20.xls')

dis_2021 = pd.read_excel('DisFut21.xls')


#%% FINANCIAL FUTURES DATA
data_2018 = pd.read_csv('FinFut18.csv')

data_2019 = pd.read_csv('FinFut19.csv')

data_2020 = pd.read_csv('FinFut20.csv')

data_2021 = pd.read_excel('Finfut21.xls')

Cot = pd.concat([dis_2018,dis_2019,dis_2020,dis_2021,data_2018, data_2019,data_2020,data_2021])


#%%

fechas = Cot.iloc[:,0]
z = []
for i in fechas:
    j = str(i)
    z.append(datetime(year=int('20'+j[:2]),month=int(j[2:4]),day=int(j[4:])))

#%% COLUMNAS NECESARIAS
#'Report_Date_as_MM_DD_YYYY'
Cot = Cot[['Market_and_Exchange_Names' ,'Open_Interest_All', 'Dealer_Positions_Long_All', 'Dealer_Positions_Short_All', 'Asset_Mgr_Positions_Long_All', 'Asset_Mgr_Positions_Short_All',  'Lev_Money_Positions_Long_All', 'Lev_Money_Positions_Short_All', 'Other_Rept_Positions_Long_All', 'Other_Rept_Positions_Short_All', 'Tot_Rept_Positions_Long_All', 'Tot_Rept_Positions_Short_All', 'NonRept_Positions_Long_All', 'NonRept_Positions_Short_All']]
Cot['Date']=z 




#%% POSICIONES NETAS DE TRADERS



Cot['Dealer_Positions_Net'] = np.zeros(len(Cot['Market_and_Exchange_Names']))
Cot['Asset_Mgr_Positions_Net'] = np.zeros(len(Cot['Market_and_Exchange_Names']))
Cot['Lev_Money_Positions_Net'] = np.zeros(len(Cot['Market_and_Exchange_Names']))
Cot['Tot_Rept_Positions_Net'] = np.zeros(len(Cot['Market_and_Exchange_Names']))
Cot['NonRept_Positions_Net'] = np.zeros(len(Cot['Market_and_Exchange_Names']))

for i in range(0,len(Cot['Dealer_Positions_Net'])):
    Cot['Dealer_Positions_Net'].iloc[i]=Cot['Dealer_Positions_Long_All'].iloc[i] - Cot['Dealer_Positions_Short_All'].iloc[i]
    Cot['Asset_Mgr_Positions_Net'].iloc[i]=Cot['Asset_Mgr_Positions_Long_All'].iloc[i] - Cot['Asset_Mgr_Positions_Short_All'].iloc[i]
    Cot['Lev_Money_Positions_Net'].iloc[i]=Cot['Lev_Money_Positions_Long_All'].iloc[i] - Cot['Lev_Money_Positions_Short_All'].iloc[i]
    Cot['Tot_Rept_Positions_Net'].iloc[i]=Cot['Tot_Rept_Positions_Long_All'].iloc[i] - Cot['Tot_Rept_Positions_Short_All'].iloc[i]
    Cot['NonRept_Positions_Net'].iloc[i]=Cot['NonRept_Positions_Long_All'].iloc[i] - Cot['NonRept_Positions_Short_All'].iloc[i]

#%%
# LISTA DE ACTIVOS NECESARIOS 
#futuros = CHICAGO MERCANTILE EXCHANGE'
futs =['CANADIAN DOLLAR', 'EURO FX', 'MEXICAN PESO','SWISS FRANC', 'SOUTH AFRICAN RAND','EURO FX/BRITISH POUND XRATE', 'NEW ZEALAND DOLLAR', 'JAPANESE YEN', 'BRITISH POUND STERLING']
crypto = ['BITCOIN-USD - CBOE FUTURES EXCHANGE']
metals = ['GOLD - COMMODITY EXCHANGE INC.', 'SILVER - COMMODITY EXCHANGE INC.']
indices= ['U.S. DOLLAR INDEX - ICE FUTURES U.S.','NASDAQ-100 STOCK INDEX (MINI) - CHICAGO MERCANTILE EXCHANGE','E-MINI S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE']    
#%%
grupos = Cot.groupby('Market_and_Exchange_Names')
activo = grupos.get_group('GOLD - COMMODITY EXCHANGE INC.')
activo = activo.sort_values(by='Date', ascending=True)
activo = activo.reset_index(drop=True)


#%% CAMBIOS PORCENTUALES de los ultimos 7 periodos
rends = (activo.iloc[-7:,1:13]).pct_change()
rends = rends.set_index(activo['Date'][-7:])*100


#%% GRAFICOS
fig = go.Figure(layout=dict(title=dict(text="COT NET POSITIONS"+' '+activo['Market_and_Exchange_Names'][0])))
fig.add_trace(go.Bar(name='OI',
                     x=activo['Date'],y=activo['Open_Interest_All']
                     ))
fig.add_trace(go.Line(name='Dealer_Positions_Net',
                     x=activo['Date'],y=activo.iloc[:,15]
                     ))
fig.add_trace(go.Line(name='Asset_Mgr_Positions_Net',
                     x=activo['Date'],y=activo.iloc[:,16]
                     ))
fig.add_trace(go.Line(name='Lev_Money_Positions_Net',
                     x=activo['Date'],y=activo.iloc[:,17]
                     ))
fig.add_trace(go.Line(name='Tot_Rept_Positions_Net',
                     x=activo['Date'],y=activo.iloc[:,18]
                     ))
fig.add_trace(go.Scatter(name='NonRept_Positions_Net',
                     x=activo['Date'],y=activo.iloc[:,19]
                     ))
fig.show()


#%% MAS VISUALES de las posiciones netas historicas.
Positions = []
lok  =([1,15,16,17,18,19])
for i in lok:
    x= (activo.iloc[-1,i]-activo.iloc[:,i].min())/(activo.iloc[:,i].max()-activo.iloc[:,i].min())
    Positions.append(x)
    
Positions = pd.DataFrame(Positions).T
Positions.columns  = ['Vol','Dealer', 'Asset_Mgr','Lev_Money','Tot_Rept', 'Non_Rept']
#%%
fig = go.Figure(px.bar(Positions, x=Positions.columns, y = Positions.values[0],
             text=Positions.values[0],
             color=Positions.values[0],
             color_continuous_scale=[(0, "green"), (0.5, "blue"), (1, "red")]))


fig.update_layout(title_text='HISTORIC COT NET POSITIONS'+' '+activo['Market_and_Exchange_Names'][0])
fig.show()

