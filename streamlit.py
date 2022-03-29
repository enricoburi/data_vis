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
time_1, time_2, variant_filter,country_filter

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

data['year']=pd.DatetimeIndex(data['date']).year
data['month']=pd.DatetimeIndex(data['date']).month


#year_to_filter = st.slider('year', 2020, 2021, 2020)
filtered_data = data[data['year'] == time_1.year]
#filtered_data = filtered_data[filtered_data['variant_grouped'].isin(variant_filter)]
#filtered_data = filtered_data[filtered_data['Country'].isin(location_filter)]
group = filtered_data.groupby(['month'])

df2 = group.apply(lambda x: x['num_sequences_total'].unique())

df2=pd.DataFrame(df2)

array=[]
for iter,rows in df2.iterrows():
  a=np.sum(rows[0])
  array.append(a)

df2['Total']=array
TOTAL=df2['Total']

TIME_MAX = np.max(TOTAL)
TIME_MIN = np.min(TOTAL)

# 'low' and 'high' refer to the final dot size.
def scale_to_interval(x, low=100, high=1000):
    return ((x - TIME_MIN) / (TIME_MAX - TIME_MIN)) * (high - low) + low

if time_1.year == 2021:
    NEW=['January','February','March','April', 'May','June', 'July','August', 'September','October','November','December'  ]
else:
    NEW=['May','June', 'July','August', 'September','October','November','December' ]

df2=df2.reindex(NEW)
print(df2.shape)
# Different sades of grey used in the plot
GREY88 = "#e0e0e0"
GREY85 = "#d9d9d9"
GREY82 = "#d1d1d1"
GREY79 = "#c9c9c9"
GREY97 = "#f7f7f7"
GREY60 = "#999999"

# Values for the x axis
ANGLES = np.linspace(0, 2 * np.pi, len(df2), endpoint=False)

# Heights of the lines and y-position of the dot are given by the times.
HEIGHTS = np.array(array)

# Category values for the colors
CATEGORY_CODES = pd.Categorical(df2.index).codes

# Colormap taken from https://carto.com/carto-colors/
COLORMAP = ["#5F4690", "#1D6996", "#38A6A5", "#0F8554", "#73AF48",
            "#EDAD08", "#E17C05", "#CC503E", "#94346E", "#666666"]

# Select colors for each password according to its category.
#COLORS = np.array(COLORMAP)[CATEGORY_CODES]


# This is going to be helpful to create some space for labels within the circle
PLUS = 200

fig, ax = plt.subplots(figsize=(8,8), subplot_kw={"projection": "polar"})

# Set background color to white, both axis and figure.
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Use logarithmic scale for the radial axis
ax.set_rscale('symlog')

# Angular axis starts at 90 degrees, not at 0
ax.set_theta_offset(np.pi / 2)

# Reverse the direction to go counter-clockwise.
ax.set_theta_direction(-1)

# Add lines
ax.vlines(ANGLES, 0 + PLUS, HEIGHTS + PLUS , lw=0.9)

# Add dots
ax.scatter(ANGLES, HEIGHTS + PLUS, s=scale_to_interval(HEIGHTS),picker=True)



for angle, height, label in zip(ANGLES, HEIGHTS, df2.index):
  rotation = np.rad2deg(angle)
  alignment = ""
  if angle >= np.pi/2 and angle < 3*np.pi/2:
        alignment = "right"
        #rotation = rotation + 180
  else:
        alignment = "left"
  ax.text(
        x=angle,
        y=1000,
        s=label,
        ha=alignment,
        va='center',
        picker=True )
        #rotation=rotation,
        #rotation_mode="anchor") ;

# Start by removing spines for both axes
ax.spines["start"].set_color("none")
ax.spines["polar"].set_color("none")

# Remove grid lines, ticks, and tick labels.
ax.grid(False)
ax.set_xticks([])
ax.set_yticklabels([])

HANGLES = np.linspace(0, 2 * np.pi, 200)


for angle, height, label in zip(ANGLES, HEIGHTS, df2.index):
  rotation = np.rad2deg(angle)
  alignment = ""
  if angle >= np.pi/2 and angle < 3*np.pi/2:
        alignment = "right"
        rotation = rotation + 180
  else:
        alignment = "left"
  ax.text(
        x=angle,
        y=1000,
        s=label,
        ha=alignment,
        va='center')
        #rotation=rotation,
        #rotation_mode="anchor")


# This fill creates the effect of a very light grey background.
ax.fill(HANGLES, np.repeat(PLUS, 200), GREY97)

# Note the 'transform=ax.transAxes'
# It allows us to pass 'x' and 'y' in terms of the (0, 1) coordinates of the axis
# instead of having to use the coordinates of the data.
# (0.5, 0.5) represents the middle of the axis in this transformed coordinate system
ax.text(
    x=0.5, y=0.5, s="********\nCOVID\nCASES\nBY MONTH\n********",
    color=GREY60, va="center", ha="center", ma="center", fontfamily="Roboto Mono",
    fontsize=18, fontweight="bold", linespacing=0.87, transform=ax.transAxes
)



fig
