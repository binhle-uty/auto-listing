import streamlit as st
import pandas as pd
import numpy as np

import plotly.graph_objs as go
from plotly.subplots import make_subplots
pd.options.plotting.backend = "plotly"

from supabase import create_client, Client
from datetime import datetime, timedelta
import re
import psycopg2
## GLOBAL PARAMETERS

SUPABASE_URL = "https://sxoqzllwkjfluhskqlfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4b3F6bGx3a2pmbHVoc2txbGZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDIyODE1MTcsImV4cCI6MjAxNzg1NzUxN30.FInynnvuqN8JeonrHa9pTXuQXMp9tE4LO0g5gj0adYE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1avXZgp1DIg7weP9GbDRrOH-T4SKvrfX-oJW4HE73aQE/export?format=csv&gid=0"

feature_map = {     'STT':'id',
                    'Tên':'title',
                   'CUSTOMERS':'customer',
                   'Asin liên quan':'asin',
                   'NGÀY':'insert_date',}
headers = [
            "id",
            "sys_run_date",
            "asin",
            "title",
            "customer",
            "insert_date",
        ]

def set_page_info():
    st.set_page_config(layout='wide', page_title='MAIN PAGE', page_icon='./logo/UTY_logo_ORI.png',)
    new_title = '<p style="font-family:sans-serif; font-size: 42px;">TỰ ĐỘNG HOÁ LISTING</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.text("")


def read_doc():
    df = pd.read_csv(GOOGLE_SHEET_URL)
    return df

def upload_file(capture_key:bool=True):
    # st.title("Upload file", disabled=capture_key)
    file = st.file_uploader("Upload file", 
                     accept_multiple_files=False, 
                     key="file_uploader_key",
                     type=['csv','xlsx'], 
                     help="File uploader for auto-listing", 
                     on_change=None, 
                     disabled=capture_key, 
                     label_visibility="hidden")
    return file

def save_to_supabase(row):
    table = "auto_listing_table"
    row = row[headers].copy()
    row["sys_run_date"] = row["sys_run_date"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # Convert rows to list of dictionaries and handle NaN values
        rows_list = row.replace({np.nan: None}).to_dict(orient="records")
        # Insert the rows into the database using executemany
        response = (
            supabase.table(f"{table}")
            .upsert(rows_list)
            .execute()
        )
        if hasattr(response, "error") and response.error is not None:
            raise Exception(f"Error inserting rows: {response.error}")
        st.success(f"Rows inserted successfully")
    except Exception as e:
        st.error(f"Error with rows: {e}")


def execute(df, at_index):
    with st.container():
        if len(df)!=0:
            if st.button("BẮT ĐẦU XỬ LÝ", key="exe_button"):
                df = df.rename(columns=feature_map)
                df['sys_run_date'] = datetime.now()
                df['id'] = df['id'] + at_index
                df = df[headers]
                st.success(f"Preprocess data")
                save_to_supabase(df)
                

def fetch_existing_asin_main():
    conn = None
    try:
        # Connect to your database
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres.sxoqzllwkjfluhskqlfl",
            password="5giE*5Y5Uexi3P2",
            host="aws-0-us-west-1.pooler.supabase.com",
        )
        cur = conn.cursor()
        # Execute a query
        cur.execute(
            "SELECT * FROM auto_listing_table a"
        )
        # Fetch all results
        df_existed = pd.DataFrame(cur.fetchall(), columns=headers)
        # Convert list of tuples to list
        asins = list(df_existed['asin'].unique())
        return asins, df_existed
    except Exception as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def convert_datetime(date:str):
    date_converted = datetime.strptime(date,"%d/%m/%Y")
    return date_converted.strftime("%Y-%m-%d")

def load_google_data():
    st.markdown("## Load data từ GOOGLE SHEET")
    with st.spinner('Wait for it...'):
        df = read_doc()
        df['NGÀY'] = df["NGÀY"].apply(convert_datetime)
    st.success('DATA LOADED!', icon="✅")
    st.empty()
    return df



if __name__ == '__main__':
    for_developer = False
    set_page_info()
    df = pd.DataFrame()
    list_asin, df_existed = fetch_existing_asin_main()
    at_index = df_existed['id'].max()
    
    toggle = st.toggle("Upload file để tự động hoá?")

    if toggle:
        file = upload_file(capture_key=not toggle)
        if file:
            df = pd.read_csv(file)
    else:
        df = load_google_data()

    if len(df)!=0:
        st.dataframe(df)

    execute(df, at_index)