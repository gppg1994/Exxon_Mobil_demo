import streamlit as st
import app
import snowflake.connector as sf
import os
import re
import time
import dotenv 
import pandas as pd
from st_aggrid import AgGrid
dotenv.load_dotenv()


SNOWFLAKE_ROLE=os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_WAREHOUSE=os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_USER=os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_ACCOUNT_LOCATOR=os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_HOST=os.getenv("SNOWFLAKE_HOST")
SNOWFLAKE_PASSWORD=os.getenv("SNOWFLAKE_PASSWORD")



def on_suggestion_change():
    st.session_state.suggestion = st.session_state.suggestion_pill
    st.session_state.suggestion_pill = None
def on_chat_input():
    st.session_state.chat_text=st.session_state.chat_input
    #st.session_state.chat_input=None

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

def chat(chat_msg:str):
    if chat_msg is not None:
        with st.chat_message(name="user"):
            st.write(chat_msg)
        with st.spinner("Searching for answer..."):
            response=app.semantic_search(chat_msg)
        match = re.search(r"```sql\s*(SELECT[\s\S]*?)```", response, re.IGNORECASE)
        curr=st.session_state.db_conn.cursor()
        try:
            with st.chat_message(name="ai"):
                if match!=None:
                        curr.execute(match.group(1))
                        df=pd.DataFrame(curr.fetch_pandas_all())
                        st.data_editor(df,use_container_width=True)
                        
                        
                        
                else:
                    st.write("No results were obtained" )
                with st.expander("Know what's under the hood"):
                    st.write(response)
        except Exception as e:
                        st.write(f"Error: {e}")
                        
    

def main():    

    try:
        #conn=connect_to_snowflake(SNOWFLAKE_ROLE,SNOWFLAKE_WAREHOUSE,SNOWFLAKE_USER,SNOWFLAKE_ACCOUNT_LOCATOR,SNOWFLAKE_HOST,SNOWFLAKE_PASSWORD)
        
        chat_msg=None       
        txt_input=st.chat_input(placeholder="Ask anything here...",key="chat_input",on_submit=on_chat_input)
    
                
        
        if 'chat_text' in st.session_state:
            chat_msg=st.session_state.chat_text
            st.session_state.pop('chat_text')
        elif 'suggestion' in st.session_state:
            chat_msg=st.session_state.suggestion
            st.session_state.pop('suggestion')
        print(chat_msg)
        chat(chat_msg)
        sample_questions=["Pull contract descriptions of the largest Missile Defense Agency contract awarded",
                        "Pull 30 contract descriptions given by agricultural department. Also mention the recipient of each contract",
                        "Since 2000, Fetch population for US, Canada, Mexico along with human readable names.",
                        "What are the major holidays in France?",
                        "What are the top 5 industries contributing to employment in the U.S.",
                        "List the top 5 states in U.S with highest homeless people. Provide the names of each state and the number of homeless people in each state",]
        selection=st.pills("Suggestions:",sample_questions,selection_mode="single",key="suggestion_pill",on_change=on_suggestion_change)   

            
    except Exception as e: 
        st.write(f"`{e}`")

if __name__=='__main__':
    try:
        
        
        conn=connect_to_snowflake(SNOWFLAKE_ROLE,SNOWFLAKE_WAREHOUSE,SNOWFLAKE_USER,SNOWFLAKE_ACCOUNT_LOCATOR,SNOWFLAKE_HOST,SNOWFLAKE_PASSWORD)     
        st.session_state['db_conn']=conn
        if 'chat_text' not in st.session_state:
            if 'suggestion' not in st.session_state:
                with st.container():
                    st.markdown("""<div style="text-align: center"> <h1>Welcome to <span style="color: #6EE2E8;font-family: Consolas, 'Courier New', monospace;font-weight: bold">DataLinguist.</span></h1></div>""",unsafe_allow_html=True) #----------Title
                    st.markdown("""<div style="text-align: center"><h3>Your personal data assistant</h3></div>""",unsafe_allow_html=True)#----------Subtitle
                    st.markdown("""<div style="text-align: center"><h6>Ask any question about the data and I will try to provide you with the answer</h6></div>""",unsafe_allow_html=True)#----------Description 
            else:
                st.session_state['heading']=None
        else:
                st.session_state['heading']=None

            
    except Exception as e: 
        st.write(f"`{e}`")    
    
    main()