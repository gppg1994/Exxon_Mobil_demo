import streamlit as st
import app
import snowflake.connector as sf
import os
import re
import time
import dotenv 
import pandas as pd
import io
import xlsxwriter
from mitosheet.streamlit.v1 import spreadsheet

dotenv.load_dotenv()

SNOWFLAKE_ROLE=os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_WAREHOUSE=os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_USER=os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_ACCOUNT_LOCATOR=os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_HOST=os.getenv("SNOWFLAKE_HOST")
SNOWFLAKE_PASSWORD=os.getenv("SNOWFLAKE_PASSWORD")

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

def on_suggestion_change1():
    
    st.session_state.selection=st.session_state.suggestion_pill1
    st.session_state.suggestion_pill1 = None
    
def on_suggestion_change2():
    
    st.session_state.selection=st.session_state.suggestion_pill2
    st.session_state.suggestion_pill2 = None
    
def on_suggestion_change3():
    
    st.session_state.selection=st.session_state.suggestion_pill3
    st.session_state.suggestion_pill3 = None
def get_answer():
    response=app.semantic_search(st.session_state.selection)
    match = re.search(r"```sql\s*(SELECT[\s\S]*?)```", response, re.IGNORECASE)
    curr=st.session_state.db_conn.cursor()
    try:
        if match!=None:
            curr.execute(match.group(1))
            df=pd.DataFrame(curr.fetch_pandas_all())
            query_results=df
                    
                    
        else:
            query_results="No results were obtained"
    except Exception as e:
        query_results=f"`{e}`"
    return (response,query_results)

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)
    processed_data = output.getvalue()  # Get Excel binary data
    return processed_data
@st.fragment()
def download_file(xlsx_data):
    st.download_button("Download(.xlsx)",xlsx_data,file_name=f"export{time.strftime('%Y%m%d%H%M%S')}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@st.fragment()
def display_data(df):
    spreadsheet(df)

st.set_page_config(layout="wide") 

try:
    conn=connect_to_snowflake(SNOWFLAKE_ROLE,SNOWFLAKE_WAREHOUSE,SNOWFLAKE_USER,SNOWFLAKE_ACCOUNT_LOCATOR,SNOWFLAKE_HOST,SNOWFLAKE_PASSWORD)
    st.session_state['db_conn']=conn
    
    if 'selection' not in st.session_state:
        st.session_state.selection=None     
    cols=st.columns(5)
    with cols[0]:
        st.html("""<style>
                    .myspan{
                font-size: 30px;
                font-family: Consolas, 'Courier New', monospace;
                font-weight: bold
            }</style>
            <body>
            <div style="text-align: center"><span class="myspan" style="color: yellow">D</span><span class="myspan">ata</span><span style="color: yellow" class="myspan">L</span><span class="myspan">inguist.</span></div></body>""") #----------Title
    cols=st.columns([1,50,1])
    with cols[1]:
        st.write("""<div style="text-align:center;line-height:1"><span style="color:grey;text-align:center;font-size:15px">Global Government is centered around geographic entities at different levels (e.g. national, state, county, municipal, zip code, census tracts, etc.) and contains a variety of daily, monthly, quarterly and annual indicators.This product serves as a central source of government statistics and reference data. It includes a collection of demographic, economic, government spending, and environmental timeseries data along with commonly used reference data about geographies and holidays. A single, unified schema joins together across the various publishers.<br><br> Ask any question about the data and I will try to provide you with the answer</span></div><br><br>""",unsafe_allow_html=True)  
    cols=st.columns([1,3,1])
    with cols[1]:
        txt_input=st.text_input("Ask me anything",st.session_state.selection)
     
      
    cols=st.columns(3)
    sample_questions=["Pull contract descriptions of the largest Missile Defense Agency contract awarded",
                        "Pull 30 contract descriptions given by agricultural department. Also mention the recipient of each contract",
                        "Since 2000, Fetch population for US, Canada, Mexico along with human readable names.",
                        "What are the major holidays in France?",
                        "What are the top 5 industries contributing to employment in the U.S.",
                        "List the top 5 states in U.S with highest homeless people. Provide the names of each state and the number of homeless people in each state",]
    
          
    with cols[0]:
         selection1=st.pills("Suggestions:",sample_questions[0:2],selection_mode="single",key="suggestion_pill1",on_change=on_suggestion_change1)   
    with cols[1]:
         selection2=st.pills("",sample_questions[2:4],selection_mode="single",key="suggestion_pill2",on_change=on_suggestion_change2)   
    with cols[2]:
         selection3=st.pills("",sample_questions[4:],selection_mode="single",key="suggestion_pill3",on_change=on_suggestion_change3)    

    if txt_input:
        st.session_state.selection=txt_input
        with st.spinner("Searching for answer..."):
            response,results=get_answer()
            with st.chat_message(name="ai"):
                if type(results)==pd.DataFrame:
                    # st.dataframe(results,use_container_width=True)
                    # xlsx_data=convert_df_to_excel(results)
                    # cols=st.columns(8)
                    # with cols.pop():
                    #     download_file(xlsx_data)
                    display_data(results)
                    
                else:
                    st.write(results)
                with st.expander("Know what's under the hood"):
                    st.write(response)
            
        
    
            
except Exception as e: 
    st.write(f"`{e}`")