import streamlit as st
import app
import snowflake.connector as sf
import os
import re
import time


SNOWFLAKE_ROLE=os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_WAREHOUSE=os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_USER=os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_ACCOUNT_LOCATOR=os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_HOST=os.getenv("SNOWFLAKE_HOST")
SNOWFLAKE_PASSWORD=os.getenv("SNOWFLAKE_PASSWORD")

def stream_data(data):
    for char in data:
        yield char
        time.sleep(0.001)



def connect_to_snowflake(sf_role,sf_warehouse,sf_user,sf_account_locator,sf_host,sf_password):
    conn = sf.connect(
        user=sf_user,
        password=sf_password,
        account=sf_account_locator,
        warehouse=sf_warehouse,
        role=sf_role,
        database='GLOBAL_GOVERNMENT',
        schema='CYBERSYN'

        
        
        
    )
    return conn
try:
    conn=connect_to_snowflake(SNOWFLAKE_ROLE,SNOWFLAKE_WAREHOUSE,SNOWFLAKE_USER,SNOWFLAKE_ACCOUNT_LOCATOR,SNOWFLAKE_HOST,SNOWFLAKE_PASSWORD)
    txt_input=st.text_input(label="Ask anything here...")
    if txt_input:
        with st.spinner("Searching for answer..."):
            response=app.semantic_search(txt_input)
            st.write(stream_data(response)    )
            match = re.search(r"```sql\s*(SELECT[\s\S]*?)```", response, re.IGNORECASE)
            curr=conn.cursor()
            
            curr.execute(match.group(1))
            st.write("Upon executing the query above, the following result was obtained:")
            st.dataframe(curr.fetchall(),width=1000)
        
except Exception as e: 
    st.write(f"`{e}`")
