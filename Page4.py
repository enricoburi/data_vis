from __future__ import annotations
from ctypes import sizeof
from genericpath import exists
from pickle import TRUE
from turtle import color, fillcolor
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

import altair as alt

from PIL import Image
import emoji
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime
from datetimerange import DateTimeRange
import seaborn as sns
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
from streamlit_plotly_events import plotly_events
import math


data = pd.read_csv('/Users/greshmababu/Downloads/data.csv')
data=data.drop(["Unnamed: 0","Climate"], axis=1)
def date_change(date_str):
            format_str = '%Y-%m-%d' # The format
            datetime_obj = datetime.strptime(date_str, format_str)
            # print(datetime_obj.date())
            return datetime_obj.date()

data["date"] = data["date"].apply(date_change)

variants=data['variant_grouped'].unique()
variants=variants[variants!='non-who']
locations=data['Country'].unique()
chosen_variants = data.groupby('variant_grouped')['num_sequences'].sum().sort_values(ascending=False)[:5]


#Create and name sidebar
st.sidebar.header('Filter the Graphs')
#st.sidebar.write("""#### Choose your SG bias""")
variants=data['variant_grouped'].unique()
variants=variants[variants!='non-who']
locations=data['Country'].unique()
country_list = sorted(set(data["Continent"]))
country_list.insert(0,'All')
sorted(country_list)

def user_input_features():
            time_filter = st.sidebar.slider('Time', 2020, 2021, 2020, 1)
            variant_filter = st.sidebar.multiselect('Variant', variants,variants)
            country_filter = st.sidebar.selectbox("Select a region:", country_list)
            return time_filter, variant_filter,country_filter

time_filter, variant_filter, country_filter = user_input_features()
st.write(emoji.emojize("""# :microbe: COVID-19 Cases by month:"""))
st.write("This interactive plot gives an overview of the monthly trends in covid evolution. "
"The filters on the left give the option of choosing the year, region and variant we wish "
"to study. On choosing any of the filters, both the plots will adjust accordingly. ")

st.write("""### Click on any of the months on the first visualization to see the variant distribution """
"of the total cases in that month. """)
data['year']=pd.DatetimeIndex(data['date']).year
data['month']=pd.DatetimeIndex(data['date']).month
data['month']=pd.to_datetime(data['month'], format='%m').dt.month_name()
#data

#print(data)
if st.sidebar.checkbox("Display all Data"):
    data1=data
    all_data_textbox = True
else:
    all_data_textbox = False
    data=data[data.year==time_filter]
    if country_filter == 'All':
        data1=data[data.variant_grouped.isin(variant_filter)]
    else:
        data1 = data[data.Continent == country_filter]
        data1 = data1[data1.variant_grouped.isin(variant_filter)]
#data1

sum_month = data1.groupby(["month"])["num_sequences"].sum().reset_index()

NEW=['January','February','March','April', 'May','June', 'July','August', 'September','October','November','December' ]

r_cord=[]

for i in NEW:
    if i not in np.array(sum_month['month']):
        r_cord.append(0)
    else:
        r_cord.append(int(sum_month[sum_month['month']==i].num_sequences))

D=[]
for i in range(len(r_cord)):
    D.append([NEW[i],r_cord[i]])

Cases=pd.DataFrame(D, columns=["Month","Number of cases"])

col1, col2 =st.columns(2)
col1.metric("Year: ", time_filter)
col2.metric("Region: ", country_filter)

col1, col2 = st.columns(2)

theta =np.linspace(90,450,13)
theta=theta[0:12]
selected_points={}
with col1:
    fig = go.Figure()
    circle=np.linspace(0,360,60)
    circle_r=np.empty(len(circle))
    circle_r.fill(0.1)
    marker_size=r_cord/np.linalg.norm(r_cord)
    marker_size=marker_size*100
    fig.add_trace(go.Scatterpolar(
            r = circle_r,
            theta = circle,
            mode = 'lines',
            #hoverinfo='skip',
            line_color = 'green',
            #hoverinfo=None,
            hoverinfo='skip',
            showlegend = False
        ))
    a=str(np.sum(r_cord))
    
    fig.add_trace(go.Barpolar(
        r=r_cord,
        theta=theta,
        width=[1,1,1,1,1,1,1,1,1,1,1,1,],
        #marker_color=["#E4FF87", '#709BFF', '#709BFF', '#FFAA70', '#FFAA70', '#FFDF70', '#B6FFB4'],
        marker_line_color="green",
        text=['January','February','March','April', 'May','June', 'July','August', 'September','October','November','December' ],
        marker_line_width=1,
        opacity=0.8,
        #text=r_cord,
        #hoverinfo='text',
        hovertemplate ='Total no of cases<br>%{r:.2f}'
        
    )
    )
    fig.add_trace(go.Scatterpolar(
        r=[5,5,5,5,5,5,5,5,5,5,5,5],
        theta=theta,
        mode='markers + text',
        text=['January','February','March','April', 'May','June', 'July','August', 'September','October','November','December' ],
        fillcolor='green',
        marker_size=marker_size,
        customdata = [[NEW[i],r_cord[i]] for i in range(len(r_cord))],
        #name=r_cord,
        textposition="middle center",
        #hoverinfo='name',
        hovertemplate= '%{customdata[0]}<br>Total no of cases:<br>%{customdata[1]:.3f}'
    ))

    fig.add_trace(go.Scatterpolar(
        r=r_cord,
        theta=theta,
        mode='markers',
        fillcolor='green',
        marker_size=r_cord
    ))

    fig.update_layout(showlegend=False,
        template=None,
        polar = dict(
            radialaxis = dict(range=[-4, 5], showline=False, showgrid=False,showticklabels=False, ticks=''),
            angularaxis = dict(showline=False,showticklabels=False, showgrid=False, ticks='')
        )
    )

    selected_points = plotly_events(fig)

month='All'
if len(selected_points)!=0:
    month=selected_points[0]['pointNumber']
    month=NEW[month]
    data2=data1[data1['month']==month]
else:
    data2=data1

df  = data2.groupby(["variant_grouped"])["num_sequences"].sum().reset_index()
df=df.rename(columns={"variant_grouped":"Variants", "num_sequences":"Total No. of cases"})
df=df.sort_values(by=['Variants'],ascending=True)
with col2:
    fig2= px.bar(df, x="Total No. of cases", y="Variants", orientation='h', color="Variants")
    fig2

#st.write("The first plot represents total number of ")


if month!='All':
    st.write("#### Month chosen: "+ month)

st.write("The first visualization encodes the number of covid cases in each month through the marker size. "
"For quantitative understanding, the values are given in the hover table as well. The second visualization "
"is a representation of the covid cases during the time period (year/month if selected) by variants. ")
st.write("Given below is also the data table for covid cases in each month." )
Cases
