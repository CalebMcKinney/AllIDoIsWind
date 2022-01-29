from pydoc import describe
from re import S
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
import requests

ROWS_PER_PERIOD = 7500

slist = ["KIKT", "KMIS", "PCNT2", "VCAT2", "FMOA1", "KBQX"]
urls = {s:"https://www.ndbc.noaa.gov/data/realtime2/"+s+".txt" for s in slist}

station = st.sidebar.selectbox("Select a station:",slist)

#r = requests.get(urls[station])
#open(station + '.txt', 'wb').write(r.content)

st.header(station)
st.text(urls[station])

# Here, download from url and convert to csv :)
df = pd.read_csv(station+".csv", header=0)
#df = pd.read_csv(station + '.txt', sep=" ", keep_default_na=False)
#df = df.drop(labels=0, axis=0)

df = df.head(ROWS_PER_PERIOD)

df = df.apply(pd.to_numeric, errors="coerce")
df = df.dropna(subset=["WSPD","WDIR"])
df = df.reset_index(drop=True)

df["full_date"]=[dt.datetime(year, month, day, hour, minute) for year, month, day, hour, minute 
    in zip(df["YY"], df["MM"], df["DD"], df["hh"], df["mm"])]

df["Date"] = pd.to_datetime(df["full_date"])
means = df.groupby(by=pd.Grouper(freq="D", key="Date", ))[["WSPD", "WDIR"]].mean()[::-1]
means = means.round(2)

fig = px.line(
    means, 
    x = means.index, 
    y = "WSPD", 
    title = "45 Day Historical Wind Data<br><sup>Hover to see wind direction.</sup>",
    custom_data=["WDIR"])

fig.update_xaxes(title_text="Date")
fig.update_yaxes(title_text="Mean Wind Speed")
fig.update_traces(hovertemplate="Wind Speed: %{y} m/s<br>Wind Direction: %{customdata[0]}°")
fig.update_layout(hovermode="x unified")

st.plotly_chart(fig)

min_date = dt.date.today() - dt.timedelta(45)

wind_rose_date = st.date_input(
    label="Select a Date to Visualize Wind Direction", 
    min_value=min_date,
    max_value=dt.date.today())

selected_df = df.loc[wind_rose_date == pd.to_datetime(df['full_date']).dt.date][["full_date", "WDIR", "WSPD"]]

selected_df['time'] = df['full_date'].dt.time
selected_df = selected_df.set_index(['time'])

#st.dataframe(selected_df)

wind_rose_fig = px.scatter_polar(
    selected_df, r="WSPD", theta="WDIR",
    color="WSPD", template="plotly_dark",
    color_discrete_sequence= px.colors.sequential.Plasma_r,
    custom_data=[selected_df.index],
    title="Daily Wind Direction Plot")

wind_rose_fig.update_traces(hovertemplate="Time: %{customdata[0]}<br>Wind Speed: %{r} m/s<br>Wind Direction: %{theta}")

st.plotly_chart(wind_rose_fig)