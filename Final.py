import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from PIL import Image
import emoji
import matplotlib.pyplot as plt
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
data = pd.read_csv('Transformed.csv')
st.write("## THE DATA BEING USED")
data

#Create and name sidebar
st.sidebar.header('Filter the Graphs')
#st.sidebar.write("""#### Choose your SG bias""")
variants=data['variant_grouped'].unique()
variants=variants[variants!='non-who']
locations=data['location'].unique()
def user_input_features():
    time_filter = st.sidebar.slider('Time', 2020, 2021, 2020, 1)
    variant_filter = st.sidebar.multiselect('Variant', variants,variants)
    location_filter = st.sidebar.multiselect('Country', locations, locations)
    #features = pd.DataFrame(user_data)
    #, index=[0])
    return time_filter,variant_filter,location_filter

#df_user = user_input_features()
time_filter,variant_filter,location_filter=user_input_features()
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


st.write("## YOUR CHOSEN WEIGHTINGS: ")
#df_user



#Output rankings based on users selections
st.write(
    """
    ## YOUR PREDICTION OUTPUT
    """
)

data['date']=pd.to_datetime(data['date'], format='%d/%m/%Y')

data['year']=pd.DatetimeIndex(data['date']).year


#year_to_filter = st.slider('year', 2020, 2021, 2020)
filtered_data = data[data['year'] == time_filter]
filtered_data = filtered_data[filtered_data['variant_grouped'].isin(variant_filter)]
filtered_data = filtered_data[filtered_data['location'].isin(location_filter)]
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

if time_filter == 2021:
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
# Don't worry if it doesn't make much sense yet, you're going to see it in action below
PLUS = 800

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
#ax.plot(HANGLES, np.repeat(1 * 24 * 60 + PLUS, 200), color= GREY88, lw=0.7)
# Add our custom grid lines for the radial axis.
# These lines indicate one day, one week, one month and one year.

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


# If you have a look at the beginning of this post, you'll see the inner circle is not white.
# This fill creates the effect of a very light grey background.
ax.fill(HANGLES, np.repeat(PLUS, 200), GREY97)

# Note the 'transform=ax.transAxes'
# It allows us to pass 'x' and 'y' in terms of the (0, 1) coordinates of the axis
# instead of having to use the coordinates of the data.
# (0.5, 0.5) represents the middle of the axis in this transformed coordinate system
ax.text(
    x=0.5, y=0.58, s="********\nCOVID\nCASES\nBY MONTH\n********",
    color=GREY60, va="center", ha="center", ma="center", fontfamily="sans serif",
    fontsize=18, fontweight="bold", linespacing=0.87, transform=ax.transAxes
)



fig



st.write(emoji.emojize("""## GDP :moneybag: vs Infant Mortality :baby_bottle: & COVID-19 :microbe:"""))
st.write("""This section features the lates COVID-19 data from a global and economical perspective: the first visalisation will provide a 
overview of the evlution of Covid cases across the globe, whil the second one will compare the GDP vs Infant Mortality index, an insightful index for the health status of a country, to the number of
Covid cases in that country.""")

# Importing first plot 
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math

st.write("""### COVID-19 Dynamic World Map""")

st.write("""#### The dataset used:""")
df = pd.read_csv('cases_evolution.csv', index_col=0)
df


fig_1 = px.scatter_geo(
    df, 
    locations='countryCode',
    color='continent',
    hover_name='country',
    size='cases',
    projection="natural earth",
    title=f'World COVID-19 Cases - Evolution Over Time',
    animation_frame="date"
)

st.plotly_chart(fig_1)


st.write("""### GDP vs Infant Mortality & Total Cases""")

st.write("""#### The dataset used:""")
# Importing GDP vs Infant mortality dataframe
data = pd.read_csv('data_gdp.csv', index_col=0)
data

# Plot 2