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
    You are an expert in writing optimized Snowflake SQL queries. Using the provided semantic model, convert natural language questions into efficient, production-ready Snowflake SQL queries.

## Input Schema
```json
{semantic_model}
```

## Analysis Process
1. Schema Analysis:
   - Parse and validate the provided JSON semantic model
   - Map table relationships and data hierarchies
   - Identify primary/foreign key relationships
   - Note any specific table/column descriptions for context

2. Question Analysis:
   - Understand the core business question and required metrics
   - Identify relevant tables and columns based on descriptions
   - Map business terms to technical schema elements
   - Determine required aggregations and calculations

3. Query Construction:
   - Build query using Snowflake best practices
   - Optimize for performance
   - Validate against schema constraints
   - Include appropriate error handling

## Query Requirements
- Use fully qualified object names (DATABASE.SCHEMA.TABLE)
- Include explicit column lists (avoid SELECT *)
- Implement proper JOIN conditions with appropriate join types
- Apply efficient filtering in WHERE clauses
- Use appropriate wildcards with LIKE operator for string matching
- Implement CASE statements for conditional logic where needed
- Include appropriate aggregations and GROUP BY clauses
- Add informative column aliases for readability
- Follow Snowflake-specific optimization practices

## Business Question
{question}

## Response Format
1. Query Analysis (2-3 sentences explaining approach)
2. Optimized Snowflake SQL Query
3. Performance Considerations (if any)

## Validation Rules
- Query must reference only tables/columns present in schema
- No assumptions about undocumented relationships
- Query must be syntactically correct
- All object references must be fully qualified
- All string comparisons should use LIKE with appropriate wildcards
- Avoid cartesian products and suboptimal join patterns
- Include appropriate NULL handling
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