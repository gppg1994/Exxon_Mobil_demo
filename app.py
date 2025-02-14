import yaml
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


#Read semantic model
def read_yaml(yaml_file_path):
    
    print("Yaml data not present in session state. Reading the files.")
    all_data=[]
    for yaml_files in os.listdir(yaml_file_path):
        if yaml_files.endswith(".yaml"):
            #streamlit.write(yaml_files)
            with open(yaml_files,'r',encoding='utf-8') as fp:
                #print(fp.name)
                yaml_data=yaml.safe_load(fp)
                all_data.append(str(yaml_data))
                fp.close()
    semantic_model="\n".join(all_data)
    
    #print (semantic_model)
    return semantic_model
    """ with open('data.json', 'w') as outfile:
        json.dump(all_data,outfile) """
    #create prompt

def extract_schema(yaml_data):
    schema_info=[]
    for schema in yaml_data:
        for table in schema.get("tables", []):
            base_table = table.get("base_table", {})
            database = base_table.get("database", "UNKNOWN_DB")
            schema = base_table.get("schema", "UNKNOWN_SCHEMA")
            table_name = base_table.get("table", "UNKNOWN_TABLE")
            
            full_table_name = f"{database}.{schema}.{table_name}"
            columns = [dim["expr"] for dim in table.get("dimensions", [])]
            schema_info.append(f"Table: {full_table_name}, Columns: {', '.join(columns)}")
    return '\n'.join(schema_info)

#yaml_data="\n".join(read_yaml(os.curdir))
 

def semantic_search(input:str)->str:
    semantic_model= read_yaml(os.curdir)  
    #print(semantic_model)
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
    You are an expert Snowflake SQL generator"""
    ),
        ("user", """
    You are an expert in writing optimized Snowflake SQL queries.Given the following database semantic model data in json format within ```, parse the data correctly to understand the database structure, and using that semantic model convert the user's question into an optimized Snowflake SQL query.

    Schema:
    ```
    {semantic_model}
    
    ```

    Carefully read the parsed json data, perform the below actions one after another:
    - Understand the intent and contex of the question asked by the user. the question asked will be in natural language.
    - try to understand which tables and columns are being referred to in the question. Use the ""description"" fields in the json data to understand the context of the columns.
    - Convert the natural language question into a Snowflake SQL query.
    - reverify the SQL query to ensure it is optimized and correct.
    
    Question: {question}
    
    Ensure the SQL uses:
    - Fully qualified table names (DATABASE.SCHEMA.TABLE)
    - Proper JOINs and WHERE conditions
    - Aggregations where necessary
    - 'LIKE' instead of '=' for string comparisons. Use wildcards if required
    - CASE WHEN for conditional logic if required
    - STRICTLY No assumptions or speculations.
    - The query should be able to run in one attempt. It should not have any syntax errors
    - Strictly stick to the given schema. 
    - Only use whatever is explicitly mentioned in the schema

   Provide a very brief explaination as how you constructed the sql query.

    Snowflake SQL Query:
    """)
    ])

    #Initialize LLM
    llm_client=AzureChatOpenAI(
        api_key=OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=OPENAI_DEPLOYMENT_NAME,
        temperature=0.1
    )

    #Create LLM chain
    chain=prompt_template | llm_client | StrOutputParser()

    question=input

    nl_to_sql=chain.invoke({"semantic_model":fr"""{semantic_model}""","question":question})
    return nl_to_sql


#print(semantic_search("Compare state- and city-level metrics to each other. In this case, show Unemployment Rates in New York City vs. New York state"))