import pandas as pd
#from tkcalendar import *
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from dateutil.relativedelta import relativedelta

pd.options.mode.copy_on_write = True
#plt.rcParams['figure.figsize'] = (20, 12)

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df_import_export=pd.read_excel(uploaded_file, sheet_name='Import_Export_kWhs')
    df_generation=pd.read_excel(uploaded_file, sheet_name='kWhs Generated')
    df_tariffs=pd.read_excel(uploaded_file, sheet_name='Tariffs')
    
    nmi=df_import_export.iloc[0,0]
    meter_number=df_import_export.iloc[1,1]
    if str(nmi)[0] == '1':
        currency = '€'
        
    elif str(nmi)[0] == '6':
        currency = '$'

    del df_import_export['NMI']
    del df_import_export['Meter Number']
    del df_import_export['Type']
    del df_tariffs['NMI']
    del df_tariffs['Meter Number']
    df_import_export['Date']= pd.to_datetime(df_import_export['Date'],format='%d/%m/%Y')
    df_tariffs['Date']= pd.to_datetime(df_tariffs['Date'],format='%d/%m/%Y')
    min_date=min(df_import_export['Date'])
    max_date=max(df_import_export['Date'])
    default_date = max_date - relativedelta(days=6)
  
    start_date = st.date_input("Enter Start Date", value = default_date, min_value = min_date, max_value = max_date)
    #st.write("Start Date is:", start_date)
    
    end_date = st.date_input("Enter End Date", min_value = min_date, max_value = max_date)
    #st.write("End Date is:", end_date)
    
    no_of_days = ((end_date - start_date).days)+1
    
    df_daily_tariff = df_tariffs.copy()
    df_daily_tariff = df_daily_tariff[(df_daily_tariff['Direction'] == 'Consumption')]
    del df_daily_tariff['Direction']
    del df_daily_tariff['Standing Charge']
    #df_daily_tariff.set_index(['Date'], inplace=True)
    df_daily_tariff = df_daily_tariff.loc[df_daily_tariff['Date'].dt.date >= start_date]
    df_daily_tariff = df_daily_tariff.loc[df_daily_tariff['Date'].dt.date <= end_date]
        
    df_daily_import_export_kWhs = df_import_export.copy()
    #cols_to_sum = df_daily_import_export_kWhs.columns[ 2 : df_daily_import_export_kWhs.shape[1]]
    #df_daily_import_export_kWhs['Daily Total kWhs'] = df_daily_import_export_kWhs[cols_to_sum].sum(axis=1)
    #df_daily_import_export_kWhs = df_daily_import_export_kWhs.drop(df_daily_import_export_kWhs.iloc[:, 2:-1],axis = 1)

    df_daily_import_kWhs = df_daily_import_export_kWhs[(df_daily_import_export_kWhs['Direction'] == 'Consumption')]
    del df_daily_import_kWhs['Direction']
    #df_daily_import_kWhs.rename({'Daily Total kWhs': 'Import_kWh'}, axis='columns', inplace=True)
    
    df_daily_import_kWhs = df_daily_import_kWhs.loc[df_daily_import_kWhs['Date'].dt.date >= start_date]
    df_daily_import_kWhs = df_daily_import_kWhs.loc[df_daily_import_kWhs['Date'].dt.date <= end_date]
    
    df_daily_import_kWhs['Date'] = df_daily_import_kWhs['Date'].dt.strftime('%d/%m/%Y')

    #df_daily_tariff.set_index(['Date'], inplace=True)
    #df_daily_import_kWhs.set_index(['Date'], inplace=True)
    
    #df_cost = df_daily_import_kWhs * df_daily_tariff
    
    df_daily_import_kWhs_long = df_daily_import_kWhs.melt(id_vars='Date',var_name='Time', value_name='kWhs')
    #st.dataframe(df_daily_import_kWhs_long)
    sns.set_theme(style="darkgrid", context="talk")  # options: paper, notebook, talk, poster
    ax = sns.catplot(kind='bar', data=df_daily_import_kWhs_long, x='Time', y='kWhs', row='Date', height=5, aspect=2)
    plt.xticks(rotation=45, fontsize=10)
    
    st.subheader("The following graphs show the kWhs imported from the grid for each half hourly interval, beginning at midnight", divider = "red")
    st.pyplot(ax)
    
    df_daily_tariff['Date'] = df_daily_tariff['Date'].dt.strftime('%d/%m/%Y')
    df_daily_import_kWhs.set_index(['Date'], inplace=True)
    df_daily_tariff.set_index(['Date'], inplace=True)
    df_cost = df_daily_import_kWhs * df_daily_tariff
    df_cost = df_cost.copy().reset_index()
    
    df_cost = df_cost.melt(id_vars='Date',var_name='Time', value_name='cents')
    sns.set_theme(style="darkgrid", context="talk")  # options: paper, notebook, talk, poster
    ax = sns.catplot(kind='bar', data=df_cost, x='Time', y='cents', row='Date', height=5, aspect=2)
    plt.xticks(rotation=45, fontsize=10)
    
    st.subheader(f"The following graphs show the cost per half hour in {currency} cents and are exclusive of tax", divider = "red")
    st.pyplot(ax)
    
    #st.dataframe(df_cost)
