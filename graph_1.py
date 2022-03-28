import matplotlib.pyplot as plt
import numpy as np
from google.colab import drive
import pandas as pd
import datetime


drive.mount('/content/drive')
path = '/content/drive/MyDrive/Uni/T2/Data Vis/Assingment_4/Transformed.csv'
df = pd.read_csv(path)
df.head()

def date_change(date_str):
  format_str = '%d/%m/%Y' # The format
  datetime_obj = datetime.datetime.strptime(date_str, format_str)
  # print(datetime_obj.date())
  return datetime_obj.date()

df["date2"] = df["date"].apply(date_change)

# create dataset
height = df["variant_grouped"].value_counts()[:5].sort_index() 
bars = df["variant_grouped"].value_counts()[:5].index.tolist()
y_pos = np.arange(len(bars))
 
# Create horizontal bars
plt.barh(y_pos, height)
 
# Create names on the x-axis
plt.yticks(y_pos, bars)
 
# Show graphic
plt.show()
