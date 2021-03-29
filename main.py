import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import seaborn as sns
import base64
import matplotlib.pyplot as plt
import numpy as np

st.title('English Premier league players visualization and statistics')

st.markdown("""
This app performs simple webscraping of English Premier League Player statistics
* **Python libraries:** base64, pandas, streamlit, bs4
* **Data source:** [fbref.com](https://fbref.com/en/comps/9/stats/Premier-League-Stats#stats_standard).
""")

# Player stats have been obtained from fbref.com
url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats#stats_standard'
#     table_class = 'stats_table sortable min_width now_sortable'
soup = BeautifulSoup(requests.get(url).content, 'html.parser')
# I noticed that tables
table = BeautifulSoup(soup.select_one('#all_stats_standard').find_next(text=lambda x: isinstance(x, Comment)),
                      'html.parser')
df = pd.read_html(str(table))[0]

# some data cleaning

# remove multilevel columns
df.columns = df.columns.droplevel()

# Remove duplicated columns
df = df.loc[:, ~df.columns.duplicated()]

# Remove columns that arent needed.
df.drop(df.columns[[0, 18, 19, 20, 21, 22, 23, 24, 25]], inplace=True, axis=1)

# Nation, ,
# Trim Nation to get last 3 digits
df['Nation'] = df['Nation'].str[-3:]

# Position
# SOme players have more than one position so I will take the first one
df['Pos'] = df['Pos'].str[:2]

# Age
# Remain with only full age of player
# Drop Born year column
df['Age'] = df['Age'].str[:2]
df.drop(['Born'], inplace=True, axis=1)

# I noticed there were 21 inique teams as opposed to 20,on checking there was a team named Squad which is the columns
# name. drop repeated headers scrapped as rows
df.drop(df[df['Squad'] == 'Squad'].index, inplace=True)

# From .describe() I noticed there were duplicate players on checking its because players have played for more than one
# team this season
# df[df['Player'].duplicated(keep=False)]

# change data types
df[['Age', 'MP', 'Starts', 'Min', 'Gls', 'Ast', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR']] = df[
    ['Age', 'MP', 'Starts', 'Min', 'Gls', 'Ast', 'G-PK', 'PK', 'PKatt', 'CrdY', 'CrdR']].apply(pd.to_numeric)

# Streamlit sidebar for Team selection

unique_team = sorted(df.Squad.unique())
selected_team = st.sidebar.multiselect('Team', unique_team, unique_team)

# Side bar for position selection

positions = sorted(df.Pos.unique())
selected_position = st.sidebar.multiselect("Position", positions, positions)

# Apply filters to the data
df_selected = df[(df.Squad.isin(selected_team)) & (df.Pos.isin(selected_position))]

st.dataframe(df_selected)


# add download button for dataframe
# def downloadfile(df):
#     csv = df.to_csv(index=False)
#     b64 = base64.b64encode(csv.encode()).decode()
#     href = f'<a href="data:file/csv;base64,{b64}" download= "PlayersStats.csv"> Download as CSV FIle'
#     return href

def downloadfile(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="download.csv">Download as csv file</a>'
    return href


st.markdown(downloadfile(df_selected), unsafe_allow_html=True)


