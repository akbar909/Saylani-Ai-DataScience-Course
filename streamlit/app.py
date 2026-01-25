import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
st.title("Police Data Analysis")
df = pd.read_csv("police.csv")
st.dataframe(df)

st.write("Statistical Summary:")
st.write(df.describe())

st.write("DataFrame Info:")
buffer = io.StringIO()
df.info(buf=buffer)
s = buffer.getvalue()
st.text(s)

df.drop('county_name', axis=1, inplace=True)

df['driver_age_raw'] = pd.to_numeric(df['driver_age_raw'], errors='coerce').astype('Int64')
df['driver_age'] = pd.to_numeric(df['driver_age'], errors='coerce').astype('Int64')

df['stop_date'] = pd.to_datetime(df['stop_date'])
df['stop_time'] = pd.to_datetime(df['stop_time'], format='%H:%M').dt.time

buffer = io.StringIO()
df.info(buf=buffer)
s = buffer.getvalue()
st.text(s)

st.write("Missing Values in Each Column:")
st.write(df.isnull().sum())

df = df.dropna(subset=[
    'driver_gender', 'driver_age_raw', 'driver_age', 'driver_race',
    'violation_raw', 'violation', 'stop_outcome', 'is_arrested', 'stop_duration'
])

categorical_cols = [
    'driver_gender', 'driver_race', 'violation_raw', 'violation',
    'stop_outcome', 'is_arrested', 'stop_duration'
]
df[categorical_cols] = df[categorical_cols].fillna('Unknown')

df['driver_age_raw'] = df['driver_age_raw'].fillna(df['driver_age_raw'].median())
df['driver_age'] = df['driver_age'].fillna(df['driver_age'].median())

df['search_type'] = df['search_type'].fillna('None')

st.write("After Handling Missing Values in Each Column:")
st.write(df.isnull().sum())

st.write("Duplicate Rows Count:")
st.write(df.duplicated().sum())

df = df.drop_duplicates()

st.write("Duplicate Rows After Removal:")
st.write(df.duplicated().sum())

st.write("Driver Gender Distribution:")
st.bar_chart(df['driver_gender'].value_counts())
st.write("Violation Distribution:")
st.bar_chart(df['violation'].value_counts())
# another distribution chart
st.write("Stop Outcome Distribution:")
st.bar_chart(df['stop_outcome'].value_counts())
st.write("Arrest Distribution:")
st.bar_chart(df['is_arrested'].value_counts())
st.write("Stop Duration Distribution:")
st.bar_chart(df['stop_duration'].value_counts())
st.write("Driver Age Distribution:")
fig, ax = plt.subplots()
ax.hist(df['driver_age'].dropna(), bins=20)
ax.set_xlabel('Driver Age')
ax.set_ylabel('Count')
ax.set_title('Driver Age Distribution')
st.pyplot(fig)

df['year_month'] = df['stop_date'].dt.to_period('M')
st.line_chart(df['year_month'].value_counts().sort_index())

st.write("Correlation Matrix:")
st.dataframe(df.corr(numeric_only=True))

