import streamlit as st
from PIL import Image
import urllib.request
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

# Config
st.set_page_config(
    page_title="🔍 Getaround Delay Analysis",
    page_icon="🚗",
    layout="wide"
)
# App
st.title('📊 Dashboard')
# Loading Image and Text
urllib.request.urlretrieve(
    'https://lever-client-logos.s3.amazonaws.com/2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943.png',
    "getaround_logo.png")
image = Image.open('getaround_logo.png')
col1, col2, col3 = st.columns([1.5, 5, 1.5])
col2.image(image, caption='Getaround user in action (Credit: Getaround.com)')
st.markdown("""
    :wave: Hello there and welcome to this dashboard!\n\n
    When using Getaround, drivers book cars for a specific time period : hours to days.\n
    Users need to bring back the car on time and It happens from time to time that drivers are late for the checkout.\n
    late returns at checkout may generate problems for the next driver. Especially if the car is reserved on the same day,
    it results in negative feedback from customers as they have to wait for the car returning back, some even canceled their rental.\n\n
    :dart: The goal of this dashboard is to give some hints on the impact of introducing time threshold on rentals.
    Within the time threshold, a car will not be displayed in the search results if the requested checkin or checkout times are very close.\n\n
    🚀 Let's start
""")
st.markdown("---")


@st.cache(allow_output_mutation=True)
def load_data():
    fname = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx"
    df = pd.read_excel(fname, engine='openpyxl', sheet_name='rentals_data')
    return df


st.text('Loading data...')
df = load_data()

# add checkout feature
checkout = []
for x in df['delay_at_checkout_in_minutes']:
    if x < 0:
        checkout.append('Early')
    elif x < 15:
        checkout.append('Late 0-15 mins')
    elif x < 30:
        checkout.append('Late 15-30 mins')
    elif x < 60:
        checkout.append('Late 30-60 mins')
    elif x < 120:
        checkout.append('Late 1-2 hours')
    elif x >= 120:
        checkout.append('Late > 2 hours')
    else:
        checkout.append('NA')
df['checkout'] = checkout


# Sidebar
st.sidebar.header("Table of content")
st.sidebar.markdown("""
    * [Preview of data set](#dataset-preview)
    * [Plot 1](#plot-1) - Distribution of rentals being on time or late
    * [Plot 2](#plot-2) - Distribution of rentals being on time or late by their status
    * [Plot 3](#plot-3) - Distribution of rentals being on time or late by their status and checkin types
    * [Plot 4](#plot-4) - A different way of plotting the previous figure
    * [Plot 5](#plot-5) - Distribution of delta time between two rentals
    * [Plot 6](#plot-6) - Correlation between features
    * [Conclusions](#conclusions)
    * [Any solutions?](#any-solutions?)
""")
st.markdown("---")


st.subheader('Dataset Preview')
# Run the below code if the check is checked
if st.checkbox('Show processed data'):
    st.subheader('Overview of 10 random rows')
    st.write(df.sample(10))
st.markdown(
    """This is not the original dataset, this one have been cleaned before""")
st.markdown("---")




st.header('Distribution of Checkin Types, group by state')
fig1 = px.pie(df, names='checkin_type', facet_col='state')
st.plotly_chart(fig1, use_container_width=True)
st.markdown("---")
st.markdown("""Remarques""")
st.markdown("---")

st.header('Distribution of ended/canceled drives, group by cheking types')
fig2 = px.pie(df, names='state', facet_col='checkin_type',
              color_discrete_sequence=['#008000', '#B22222'])
st.plotly_chart(fig2, use_container_width=True)
st.markdown("---")
st.markdown("""Remarques""")
st.markdown("---")

category_orders = {"checkout": ["Early", "Late 0-15 mins", "Late 15-30 mins",
                                "Late 30-60 mins", "Late 1-2 hours", "Late > 2 hours", "NA"]}
color_discrete_sequence = ["#008000", "#ffbaba",
                           "#ff7b7b", "#ff5252", "#ff0000", "#a70000", "Black"]

st.header("Distribution of rentals being on time or late by their status")
fig3 = px.histogram(df.sort_values(by="delay_at_checkout_in_minutes"),
                    x='state',
                    color="checkout",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig3, use_container_width=True)
st.markdown("""
    Around 3 200 Getaround users canceled their ride possibly due to the delay at checkout.
""")
st.markdown("---")

st.markdown(
    "Distribution of rentals being on time or late by their status and checkin types")
fig4 = px.histogram(df.sort_values(by="delay_at_checkout_in_minutes"),
                    x='state',
                    facet_col='checkin_type',
                    color="checkout",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig4, use_container_width=True)
st.markdown("""
    Please check the next figure for the comments.
""")
st.markdown("---")


st.header('Delays rentals distribution in %, group by cheking types')
fig5 = px.histogram(df.sort_values(by="delay_at_checkout_in_minutes"),
                    x="checkout",
                    color="checkout",
                    facet_row="checkin_type",    
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig5, use_container_width=True)
st.markdown("""As you can see, the mobile checkin_Type is the most concerned by the delays (that require the presence of owner + driver)""")
st.markdown("---")

# Treshold
df.dropna(subset=['delay_at_checkout_in_minutes'], inplace=True)
min = df["delay_at_checkout_in_minutes"] <= df["delay_at_checkout_in_minutes"].quantile(0.01)
max = df["delay_at_checkout_in_minutes"] >= df["delay_at_checkout_in_minutes"].quantile(0.99)
df_delay_bis = df.loc[~ (min | max), :]

late_drivers = df_delay_bis["delay_at_checkout_in_minutes"] > 0
df_late_drivers = df_delay_bis[late_drivers]


st.header('What about treshold ?')
st.subheader('Plotted distribution')
fig6 = px.histogram(df_late_drivers, x="delay_at_checkout_in_minutes", histfunc='count', facet_row="checkin_type")
st.plotly_chart(fig6, use_container_width=True)

st.markdown("""As you can see, the mobile checkin_Type is the most concerned by the delays (that require the presence of owner + driver)""")
