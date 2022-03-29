import pandas as pd
import altair as alt

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
  )
  
  return graph
