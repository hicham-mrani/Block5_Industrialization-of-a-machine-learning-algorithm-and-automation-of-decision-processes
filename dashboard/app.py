import streamlit as st
from PIL import Image
import urllib.request
import pandas as pd
import numpy as np
import plotly.express as px

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
    Purpose of this dashboard : \n\n
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
    df = pd.read_excel(fname, engine='openpyxl', sheet_name='rentals_data')
    return df


st.text('Loading data...')

fname = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx"
df = pd.read_excel(fname, engine='openpyxl', sheet_name='rentals_data')

fname = "https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv"
df_pricing = pd.read_csv(fname, index_col=0)

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

# add feature to the original dataset
df['checkout'] = checkout

st.subheader('Dataset Preview')

if st.checkbox('Show processed data'):
    st.subheader('Overview of 10 random rows')
    st.write(df.sample(10))
st.markdown(
    """
        This is not the original dataset, this one have been cleaned before
    """
)
st.markdown("---")


category_orders = {"checkout": ["Early", "Late 0-15 mins", "Late 15-30 mins",
                                "Late 30-60 mins", "Late 1-2 hours", "Late > 2 hours", "NA"]}
color_discrete_sequence = ["#008000", "#ffbaba",
                           "#ff7b7b", "#ff5252", "#ff0000", "#a70000", "Black"]

st.header("Distribution of rentals being on time or late by their status")
fig1 = px.histogram(df.sort_values(by="delay_at_checkout_in_minutes"),
                    x='state',
                    color="checkout",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig1, use_container_width=True)
st.markdown(
    """
        Around 3 200 Getaround users canceled their ride possibly due to the delay at checkout.
    """
)
st.markdown("---")

st.header("Which checkin type is mostly concerned by the delays ?")
fig2 = px.histogram(df.sort_values(by="delay_at_checkout_in_minutes"),
                    x='state',
                    facet_col='checkin_type',
                    color="checkout",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig2, use_container_width=True)
st.markdown(
    """
        Here we can see that canceled drives mostly concern the mobile checkin type,\nso if we have to resolve the problem, we should prioritise this checkin mode
    """
)
st.markdown("---")

fig3 = px.histogram(df.sort_values(by="delay_at_checkout_in_minutes"),
                    x="checkout",
                    color="checkout",
                    facet_row="checkin_type",
                    color_discrete_sequence=color_discrete_sequence
                    )
st.plotly_chart(fig3, use_container_width=True)
st.markdown(
    """
        Once again the mobile checkin type is the most concerned, the delays here is more important than connected checkin.\n\n In fact the mobile checkin require the presence of owner + driver
    """
)
st.markdown("---")

# Treshold
df.dropna(subset=['delay_at_checkout_in_minutes'], inplace=True)
min = df["delay_at_checkout_in_minutes"] <= df["delay_at_checkout_in_minutes"].quantile(
    0.01)
max = df["delay_at_checkout_in_minutes"] >= df["delay_at_checkout_in_minutes"].quantile(
    0.99)
df_delay_bis = df.loc[~ (min | max), :]

late_drivers = df_delay_bis["delay_at_checkout_in_minutes"] > 0
df_late_drivers = df_delay_bis[late_drivers]


st.header('What about treshold ?')
st.subheader('Plotted distribution')
fig4 = px.histogram(df_late_drivers, x="delay_at_checkout_in_minutes",
                    histfunc='count', facet_row="checkin_type")
st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    """
        If we need to apply a treshold we should focus mobile checkin type and target delays plus than 2 hours.
    """)
st.markdown("---")

st.header("Can we estimate money lost due to the delays ?")

df_late_drivers_mobile = df_late_drivers[df_late_drivers["checkin_type"] == "mobile"]
df_late_drivers_connect = df_late_drivers[df_late_drivers["checkin_type"] == "connect"]
delay_median_mobile = np.median(
    df_late_drivers_mobile["delay_at_checkout_in_minutes"])
delay_median_connect = np.median(
    df_late_drivers_connect["delay_at_checkout_in_minutes"])

# Mobile Checkin Type
st.subheader("Mobile Checkin Type")
nb_delays = len(df_late_drivers_mobile)
st.write(f"{nb_delays} are concerned by delays (short/long)")
delay_median_mobile = np.median(df_late_drivers_mobile["delay_at_checkout_in_minutes"])
st.write(f"the delay is about : {delay_median_mobile} minutes")
avg_price_rent_by_day = np.mean(df_pricing["rental_price_per_day"])  # price by day
st.write(f"Plus we know that the average price of car rent is about : {avg_price_rent_by_day}$ by day")
avg_price_rent_by_min = avg_price_rent_by_day / 1_440
st.write(f"That represent : {round(avg_price_rent_by_min, ndigits=3)} $ by minute")
money_loss = avg_price_rent_by_min * delay_median_mobile
st.write(f"so getaround loss about {money_loss} $ for each delay")
st.write(f"so getaround loss about {money_loss * nb_delays} $ for {nb_delays} delays")
st.markdown("---")

## Connect Checkin Type
st.subheader("Connect Checkin Type")
nb_delays = len(df_late_drivers_connect)
st.write(f"{nb_delays} are concerned by delays (short/long)")
delay_median_connect = np.median(df_late_drivers_connect["delay_at_checkout_in_minutes"])
st.write(f"the delay is about : {delay_median_connect} minutes")
avg_price_rent_by_day = np.mean(df_pricing["rental_price_per_day"]) ## price by day
st.write(f"Plus we know that the average price of car rent is about : {avg_price_rent_by_day}$ by day")
avg_price_rent_by_min = avg_price_rent_by_day / 1_440
st.write(f"That represent : {round(avg_price_rent_by_min, ndigits=3)} $ by minute")
money_loss = avg_price_rent_by_min * delay_median_connect
st.write(f"so getaround loss about {money_loss} $ for each delay")
st.write(f"so getaround loss about {money_loss * nb_delays} $ for {nb_delays} delays")
