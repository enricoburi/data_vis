import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
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
import math

linkedinlink = '[Github](https://github.com/patrickld/data_vis/)'

#Create header
st.write(emoji.emojize("""# :microbe: COVID-19 PandeMap :microbe:"""))
st.write("""## How it works""")
st.write("This tool will enable users to quickly visualize COVID-19 global evolution, "
         "track the development of the virus and its variants and measure the correlation "
         "between the development of a country and the number of COVID-19 cases.")
st.write("##### For viewing the Sourcecode, click here:", linkedinlink)

#image
#image = Image.open('Tiger.jpg')
#st.image(image)

#Bring in the data
data = pd.read_csv('data.csv')
st.write("## THE DATA BEING USED")
data=data.drop(["Unnamed: 0","Climate"], axis=1)

#Transformation of Date column
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
    time_1,time_2 = st.sidebar.date_input("Choose a Range in Time:", value = (data.date.min(),data.date.max()), min_value =data.date.min(), max_value=data.date.max())
    variant_filter = st.sidebar.multiselect('Variant', variants,variants)
    country_filter = st.sidebar.selectbox("Select a region:", country_list)
    return time_1, time_2, variant_filter,country_filter

time_1, time_2, variant_filter, country_filter = user_input_features()

if st.sidebar.checkbox("Display all Data"):
    data1=data
    all_data_textbox = True
else:
    all_data_textbox = False
    if country_filter == 'All':
        data1=data[(data.variant_grouped.isin(variant_filter)) & (time_1<=data.date) & (time_2>=data.date)]
    else:
        data1 = data[data.Continent == country_filter]
        data1 = data1[(data1.variant_grouped.isin(variant_filter)) & (time_1<=data1.date) & (time_2>=data1.date)]
data1


st.write("## Chosen Filters: ")
if all_data_textbox == True:
    st.write("All Data is chosen")
else:
    "Timeframe: " +str(time_1) + " to " + str(time_2)
    str_val = ", ".join(variant_filter)
    "Chosen Variants: " + str(str_val)
    "Chosen country: " + str(country_filter)


#Output rankings based on users selections
st.write(
    """
    ## Overview of the Variants
    """
)

def graph3(data):
  '''
  Expects data.csv or its subsets as input
  Returns the graph showing cumulative cases by variant over time
  '''

  # Data manipulation: cumulative counts of cases by date and variant
  sum_variant = data.groupby(["variant_grouped"])["num_sequences"].sum().reset_index()
  sum_variant.columns = ["Variant", "Cases"]
#  sum_variant = sum_variant.Variant.sort_values(ascending=False)[:5]

  # Define interaction
  click = alt.selection_single(encodings=['color'], on="mouseover")

  # Create plot
  graph = alt.Chart(sum_variant).mark_bar(
    opacity=0.7,
    interpolate='basis',
    line=True).properties(
    title='Cases by Variant').encode(
    x=alt.X("Cases:Q", scale=alt.Scale(type='log'), stack=None),
    y=alt.Y("Variant:N", sort='-x', title=None),
    color=alt.Color('Variant:N', scale=alt.Scale(scheme='category20c')),
    tooltip = [alt.Tooltip('Variant:N'),alt.Tooltip('Cases:Q')],
    opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))
  ).add_selection(
    click
  ).properties(width=600)

  return graph

#################


#create bar chart
def graph3_2(df):
  '''
  Expects data.csv or its subsets as input
  Returns the graph showing cumulative cases by variant over time
  '''

  # Data manipulation: cumulative counts of cases by date and variant
  variantsum = df.groupby(["variant_grouped", "Country"])["num_sequences"].sum().reset_index()
  variantsum.columns = ["Variant", "Country", "Cumulative Cases"]

  # Define interaction
  click = alt.selection_single(encodings=['color'], on="mouseover")
  # Create plot

  graph = alt.Chart(variantsum).mark_bar(
    opacity=0.7,
    interpolate='basis',
    line=True).properties(
    title='Cases by Variant').encode(
    x=alt.X('Cumulative Cases:Q', stack = 'normalize'),
    y=alt.Y("Country:N", title=None),
    color=alt.Color('Variant:N', scale=alt.Scale(scheme='category20c'),legend=alt.Legend(title="Variants by color")),
    tooltip = [alt.Tooltip('Country:N'),alt.Tooltip('Cumulative Cases:Q')],
    opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))
  ).add_selection(
    click
  ).properties(width=600)

  return graph

st.altair_chart(graph3_2(data1))


#################
data['year']=pd.DatetimeIndex(data['date']).year
data['month']=pd.DatetimeIndex(data['date']).month


st.write("""#### Cases by Variant Over Time  :chart_with_upwards_trend: """)

st.altair_chart(graph3(data1))
    #    df_results  = results_output()

# ------ Buri's graphs
#col3,col4 = st.columns((.1,2))

# Disable default datapoints limit in Altair
alt.data_transformers.disable_max_rows()

def graph2(data):
  '''
  Expects data.csv or its subsets as input
  Returns the graph showing cumulative cases by variant over time
  '''

  # Data manipulation: cumulative counts of cases by date and variant
  cumsum_variant = data.groupby(["variant_grouped", "date"])["num_sequences"].sum().groupby(level=0).cumsum().reset_index()
  cumsum_variant.columns = ["Variant", "date", "Cumulative Cases"]

  # Define interaction
  click = alt.selection_single(encodings=['color'], on="mouseover")

  # Create plot
  graph = alt.Chart(cumsum_variant).mark_area(
      opacity=0.7,
      interpolate='basis',
      line=True).properties(
      title='Cumulative Cases by Variant over time').encode(
      x=alt.X("date:T",
          title=None),
      y=alt.Y("Cumulative Cases:Q"),
      color=alt.Color('Variant:N',
          scale=alt.Scale(scheme='category20c')),
      tooltip = [alt.Tooltip('Variant:N')],
      opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))
  ).add_selection(
      click
  ).properties(width=600)


  return graph


#with col4:
st.altair_chart(graph2(data1))



st.write(emoji.emojize("""## :microbe: Dynamic World Map & GDP vs Infant Mortality Index :microbe:"""))

st.write("""This section features the lates COVID-19 data from a global and economical perspective: the first visalisation will provide a
overview of the evlution of Covid cases across the globe, whil the second one will compare the GDP vs Infant Mortality index, an insightful index for the health status of a country, to the number of
Covid cases in that country.""")

# Importing first plot
st.write("""#### World COVID-19 Cases - Evolution Over Time :earth_africa: """)

st.write("""##### The dataset used:""")
df = pd.read_csv('cases_evolution.csv', index_col=0)
df



fig_1 = px.scatter_geo(
    df,
    locations='countryCode',
    color='continent',
    hover_name='country',
    projection='orthographic',
    size='cases',
    title=f'World COVID-19 Cases - Evolution Over Time',
    animation_frame="date"
)

st.plotly_chart(fig_1)


st.write("""#### GDP :moneybag: vs Infant Mortality  :baby_bottle: & Total Cases""")

st.write("""##### The dataset used:""")
# Importing GDP vs Infant mortality dataframe
data = pd.read_csv('data_gdp.csv', index_col=0)
data

# Plot 2
bubble_fig = px.scatter(data, x='Infant mortality (per 1000 births)',
                                y='GDP ($ per capita)',
                                color='Continent',
                                size='Tot number of cases',
                                log_x=True,
                                hover_name="Country",
                                hover_data=['GDP ($ per capita)', 'Infant mortality (per 1000 births)'],
                                size_max=70)


#bubble_fig.update_layout(hovermode='closest')
st.plotly_chart(bubble_fig)
# hovertemplaye=None
# hovermode="x unified"
