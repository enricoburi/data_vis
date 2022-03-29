import pandas as pd
import altair as alt

# Disable default datapoints limit in Altair
alt.data_transformers.disable_max_rows()

def graph3(data):
  '''
  Expects data.csv or its subsets as input
  Returns the graph showing cumulative cases by variant over time
  '''

  # Data manipulation: cumulative counts of cases by date and variant
  sum_variant = data.groupby(["variant_grouped", "date"])["num_sequences"].sum().reset_index()
  sum_variant.columns = ["Variant", "date", "Cases"]

  # Define interaction
  click = alt.selection_single(encodings=['color'], on="mouseover")

  # Create plot
  graph = alt.Chart(sum_variant).mark_area(
    opacity=0.7,
    interpolate='basis',
    line=True).properties(
    title='Cases by Variant over time').encode(
    x=alt.X("date:T", title=None),
    y=alt.Y("Cases:Q", stack=None),
    color=alt.Color('Variant:N', scale=alt.Scale(scheme='category20c')),
    tooltip = [alt.Tooltip('Variant:N')],
    opacity = alt.condition(click, alt.value(0.9), alt.value(0.1))
  ).add_selection(
    click
  )
  
  return graph
