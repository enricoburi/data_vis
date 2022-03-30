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
country_list = sorted(set(data["Country"]))
country_list.insert(0,'All')
sorted(country_list)

def user_input_features():
    time_1,time_2 = st.sidebar.date_input("Choose a Range in Time:", value = (data.date.min(),data.date.max()), min_value =data.date.min(), max_value=data.date.max())
    variant_filter = st.sidebar.multiselect('Variant', variants,variants)
    country_filter = st.sidebar.selectbox("Select a region:", country_list)
    return time_1, time_2, variant_filter,country_filter

time_1, time_2, variant_filter,country_filter = user_input_features()

if st.sidebar.checkbox("Display all Data"):
    data1=data
    all_data_textbox = True
else:
    data1 = data[(data.variant_grouped.isin(variant_filter)) & (time_1<=data.date) & (time_2>=data.date)]
    all_data_textbox = False
    if country_filter == 'All':
        data1=data1
    else:
        data1 = data[data.Country == country_filter]

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
col1, col2 = st.columns((.15,.3))

def graph3(data):
  '''
  Expects data.csv or its subsets as input
  Returns the graph showing cumulative cases by variant over time
  '''

  # Data manipulation: cumulative counts of cases by date and variant
  sum_variant = data1.groupby(["variant_grouped", "date"])["num_sequences"].sum().reset_index()
  sum_variant.columns = ["Variant", "date", "Cases"]
#  sum_variant = sum_variant.Variant.sort_values(ascending=False)[:5]

  # Define interaction
  click = alt.selection_single(encodings=['color'], on="mouseover")

  # Create plot
  graph = alt.Chart(sum_variant).mark_bar(
    opacity=0.7,
    interpolate='basis',
    line=True).properties(
    title='Cases by Variant').encode(
    x=alt.X("Cases:Q", sort='-x', stack=None),
    y=alt.Y("Variant:N", title=None),
    color=alt.Color('Variant:N', scale=alt.Scale(scheme='category20c'),legend=None),
    tooltip = [alt.Tooltip('Variant:N')],
    opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))
  ).add_selection(
    click
  )

  return graph



with col2:
    st.altair_chart(graph3(data1))
    #    df_results  = results_output()

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
# Don't worry if it doesn't make much sense yet, you're going to see it in action below
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
    x=0.5, y=0.5, s="********\nCOVID\nCASES\nBY MONTH\n********",
    color=GREY60, va="center", ha="center", ma="center", fontfamily="Roboto Mono",
    fontsize=18, fontweight="bold", linespacing=0.87, transform=ax.transAxes
)

with col1:
    fig





st.write("""#### Cases by Variant Over Time  :chart_with_upwards_trend: """)

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
  ).properties(width=800)


  return graph


#with col4:
st.altair_chart(graph2(data1))



# -----



# -----




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
