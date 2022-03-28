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

chosen_variants = data.groupby('variant_grouped')['num_sequences'].sum().sort_values(ascending=False)[:5]


#Create and name sidebar
st.sidebar.header('Filter the Graphs')
#st.sidebar.write("""#### Choose your SG bias""")

def user_input_features():
    time_1,time_2 = st.sidebar.date_input("Choose a Range in Time:", value = (data.date.min(),data.date.max()), min_value =data.date.min(), max_value=data.date.max())
    variant_filter = st.sidebar.select_slider('Variant', chosen_variants.keys())
    #                           multiselect
    country_filter = st.sidebar.selectbox("Select a region:", sorted(set(data["Country"])))
    return time_1, time_2, variant_filter,country_filter

time_1, time_2, variant_filter,country_filter = user_input_features()

#time_range = DateTimeRange(time_1, time_2)
data[(data.Country == country_filter) & (data.variant_grouped == variant_filter) & (time_1<=data.date) & (time_2>=data.date)]

if st.sidebar.checkbox("Display all Data"):
    def user_input_biased():
        thisyear = st.sidebar.slider('2021 weighting', 0, 100, 100, 5)
        lastyear = st.sidebar.slider('2020 weighting', 0, 100, 80, 5)
        biased_data = {'this year': thisyear/100,
                       'last year': lastyear/100}
        biased = pd.DataFrame(biased_data, index=[0])
        return biased


    df_user_biased = user_input_biased()

else:
    def user_input_biased():
        thisyear = 100
        lastyear = 60
        biased_data = {'this year': thisyear / 100,
                       'last year': lastyear / 100}
        biased = pd.DataFrame(biased_data, index=[0])
        return biased
    df_user_biased = user_input_biased()


st.write("## Chosen Filters: ")
df_user

#Output rankings based on users selections
st.write(
    """
    ## Overview of the Variants
    """
)

def results_output():

    fig = Figure()
    ax = fig.subplots()
    sns.barplot(x=data.groupby('variant_grouped')['num_sequences'].sum().sort_values(ascending=False)[:5],
                y=data.groupby('variant_grouped')['num_sequences'].sum().sort_values(ascending=False)[:5].keys(), color='blue', ax=ax)
    ax.set_xlabel('# of Occurances')
    ax.set_ylabel('Variants')
    st.pyplot(fig)

df_results  = results_output()
