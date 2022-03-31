import streamlit as st
import pandas as pd
import os
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
covidlink='[Kaggle](https://www.kaggle.com/datasets/yamqwe/omicron-covid19-variant-daily-cases?select=covid-variants.csv)'

st.set_page_config(
    page_title="A Dashboard Template",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache()
def fake_data():
    """some fake data"""

    dt = pd.date_range("2021-01-01", "2021-03-01")
    df = pd.DataFrame(
        {"datetime": dt, "values": np.random.randint(0, 10, size=len(dt))}
    )

    return df


def sidebar_caption():
    """This is a demo of some shared sidebar elements.
    Reused this function to make sure we have the same sidebar elements if needed.
    """

    #st.sidebar.header("Yay, this is a sidebar")
    #st.sidebar.markdown("This is a markdown element in the **sidebar**.")


def filter_table_option():

    show_n_records = st.sidebar.slider('Show how many', 0, 30, 1)

    return show_n_records


class Page:
    def __init__(self, name, data, **kwargs):
        self.name = name
        self.data = data
        self.kwargs = kwargs

    def content(self):
        """Returns the content of the page"""

        raise NotImplementedError("Please implement this method.")

    def title(self):
        """Returns the title of the page"""
        st.header(f"{self.name}")

    def __call__(self):
        #self.title()
        self.content()



class About(Page):
    def __init__(self, data, **kwargs):
        name = "About"
        super().__init__(name, data, **kwargs)


    def content(self):

        st.write(emoji.emojize("""# :microbe: COVID-19 PandeMap :microbe:"""))
        st.write("""## How it works""")
        st.write("This tool will enable users to quickly visualize COVID-19 global evolution, "
        "track the development of the virus and its variants and measure the correlation "
        "between the development of a country and the number of COVID-19 cases.")
        st.write("##### For viewing the Sourcecode, click here:", linkedinlink)
        st.write("""## Navigating the app""")
        st.write("The app consists of 4 pages, including this introduction page. "
        " To navigate to the other pages, click on the options in the sidebar. "
        "Given below is a short description of what each page shows.")
        st.write("##### 1: Covid by Variants ")
        st.write("The first page is a view of the covid spread by variants. We can "
        "compare covid spreads in different locations at different times at the "
        "variant level of granularity ")
        st.write("##### 2: How Covid Spread")
        st.write("In the second page, we go deeper into understanding the spread of covid. "
        "We see the evolution of covid over time and also, make a comparison of regions by GDP "
        "and infant mortalities and covid cases to see if there is some trend that is observable. ")
        st.write("##### 3: Monthly covid evolution")
        st.write("Here, we have a monthly view of how covid spread by location "
        "and variants ")
        st.write("###### We have taken the covid data from", covidlink)

class Page2(Page):
    def __init__(self, data, **kwargs):
        name = "Page2"
        super().__init__(name, data, **kwargs)
    def content(self):
        #Create header
        st.write(emoji.emojize("""# :microbe: COVID-19 - A study by variants:"""))
        #st.write("""## How it works""")
        #st.write("This tool will enable users to quickly visualize COVID-19 global evolution, "
        "track the development of the virus and its variants and measure the correlation "
        "between the development of a country and the number of COVID-19 cases."
        #st.write("##### For viewing the Sourcecode, click here:", linkedinlink)


        #Bring in the data
        data = pd.read_csv('data.csv')
        #st.write("## THE DATA BEING USED")
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
            st.write("Timeframe: " +str(time_1) + " to " + str(time_2))
            str_val = ", ".join(variant_filter)
            st.write("Chosen Variants: " + str(str_val))
            st.write("Chosen country: " + str(country_filter))


        #Output rankings based on users selections
        st.write(
            """
            ## Overview of the Variants
            """
        )
        def page123(data):

          def graph1(data, click):
            '''
            Expects data.csv or its subsets as input
            Returns the horizontal bar chart showing the total case by variant
            '''

            #Data manipulation: simple sum of cases by variant
            total_sum_variant = data[["variant_grouped", "num_sequences"]]
            total_sum_variant.columns = ["Variant", "Total Cases"]

            graph = alt.Chart(total_sum_variant).mark_bar(
                opacity=0.7).properties(
                width=880,
                title='Total Cases by Variant').encode(
                x=alt.X('sum(Total Cases):Q',
                    title="Total Cases"),
                y=alt.Y('Variant:N',sort='-x',
                    title=None),
                color=alt.Color('Variant:N',
                    scale=alt.Scale(scheme='category20c')),
                tooltip = [alt.Tooltip('Variant:N'),alt.Tooltip('Cases:Q')],
                opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))).add_selection(
                click
            )

            return graph

          def graph2(data, click):
            '''
            Expects data.csv or its subsets as input
            Returns the graph showing cumulative cases by variant over time
            '''

            # Data manipulation: cumulative counts of cases by date and variant
            cumsum_variant = data.groupby(["variant_grouped", "date"])["num_sequences"].sum().groupby(level=0).cumsum().reset_index()
            cumsum_variant.columns = ["Variant", "date", "Cumulative Cases"]

            # Define interaction (needs to be global variable for cross-chart interaction)
            # click = alt.selection_single(encodings=['color'], on="mouseover")

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
                tooltip = [alt.Tooltip('Variant:N'),alt.Tooltip('Cases:Q')],
                opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))).add_selection(
                click
            )

            return graph

          def graph3(data, click):
            '''
            Expects data.csv or its subsets as input
            Returns the graph showing cumulative cases by variant over time
            '''

            # Data manipulation: cumulative counts of cases by date and variant
            sum_variant = data.groupby(["variant_grouped", "date"])["num_sequences"].sum().reset_index()
            sum_variant.columns = ["Variant", "date", "Cases"]

            # Define interaction (needs to be global variable for cross-chart interaction)
            # click = alt.selection_single(encodings=['color'], on="mouseover")

            # Create plot
            graph = alt.Chart(sum_variant).mark_area(
              opacity=0.7,
              interpolate='basis',
              line=True).properties(
              title='Cases by Variant over time').encode(
              x=alt.X("date:T", title=None),
              y=alt.Y("Cases:Q", stack=None),
              color=alt.Color('Variant:N', scale=alt.Scale(scheme='category20c')),
              tooltip = [alt.Tooltip('Variant:N'),alt.Tooltip('Cases:Q')],
              opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))).add_selection(
              click
            )

            return graph

          def graph3_2(data, click):
            '''
            Expects data.csv or its subsets as input
            Returns the graph showing cumulative cases by variant over time
            '''

            # Data manipulation: cumulative counts of cases by date and variant
            variantsum = data.groupby(["variant_grouped", "Country"])["num_sequences"].sum().reset_index()
            variantsum.columns = ["Variant", "Country", "Cumulative Cases"]

            # Define interaction
            #click = alt.selection_single(encodings=['color'], on="mouseover")
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
            )#.properties(width=600)

            return graph

          click = alt.selection_single(encodings=['color'], on="mouseover", resolve="global")

          return graph1(data,click) & (graph2(data, click) | graph3(data, click) & graph3_2(data, click))

        st.altair_chart(page123(data1))


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



class Page3(Page):
    def __init__(self, data, **kwargs):
        name = "Page2"
        super().__init__(name, data, **kwargs)
    def content(self):
        st.write(emoji.emojize("""## :microbe: Dynamic World Map & GDP vs Infant Mortality Index :microbe:"""))

        st.write("""This section features the lates COVID-19 data from a global and economical perspective: the first visalisation will provide a
        overview of the evlution of Covid cases across the globe, whil the second one will compare the GDP vs Infant Mortality index, an insightful index for the health status of a country, to the number of
        Covid cases in that country.""")

        # Importing first plot
        st.write("""#### World COVID-19 Cases - Evolution Over Time :earth_africa: """)

        #st.write("""##### The dataset used:""")
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


def main():
    """A streamlit app template"""

    st.sidebar.title("Navigation")

    PAGES = {
        "About the app": About,
        "Covid by Variants": Page2,
        "Evolution of Covid": Page3,

    }

    # Select pages
    # Use dropdown if you prefer
    selection = st.sidebar.radio("Pages", list(PAGES.keys()))
    sidebar_caption()

    page = PAGES[selection]

    DATA = {"base": fake_data()}

    with st.spinner(f"Loading Page {selection} ..."):
        page = page(DATA)
        page()


if __name__ == "__main__":
    main()
