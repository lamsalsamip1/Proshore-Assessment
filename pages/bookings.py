import streamlit as st
import pandas as pd
import os
import psycopg2

db_host = 'cleancam.postgres.database.azure.com'
db_name = 'postgres'
db_user = 'lamsalsamip'
db_pass = os.getenv('AZURE_DB_PASSWORD')

conn = psycopg2.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_pass
    )
cur = conn.cursor()

# Fetch data from the database
cur.execute("SELECT booking_id, name, destination, date FROM bookings")
rows = cur.fetchall()

# Create a DataFrame
df = pd.DataFrame(rows, columns=['Booking ID', 'Name', 'Destination', 'Date'])

# Streamlit UI
st.title('Bookings Table')
st.table(df)