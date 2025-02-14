
import GenerateEmbeddings
import os
import yaml
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import datetime

# Function to read a PDF file page by page
def create_documents(file_path):
    data=[]
    c=1
    for yaml_files in os.listdir(file_path):
        if yaml_files.endswith(".yaml"):
            print(yaml_files)
            with open(yaml_files,'r',encoding='utf-8') as fp:
                yaml_data=yaml.safe_load(fp)
                document_data={}
                for table in yaml_data['tables']:
                    document_data={
                        "id":str(c)+datetime.datetime.now().strftime(r"%Y%m%d%H%M%S"),
                        "table":{
                                            "table_name": table['name'],
                                            "table_description": table['description'],
                                            "base_table":{
                                                "database": table['base_table']['database'],
                                                "schema": table['base_table']['schema'],
                                            }
                                }
                            }
                    for column in table['dimensions']:
                        document_data['table']['columns']={
                            "column_name": column['name'],
                            "column_desc": column['description'],
                            "column_type": column['data_type'],
                            "column_expr": column["expr"],
                            "column_sample_value": ",".join(column["sample_values"]) if "sample_values" in column else None,
                            }
            data.append(document_data)  
            c+=1    

    return data
        
def create_search_index():
    # Configuration of AI Search Service
    service_name = 'gppg-ai-service'
    admin_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = 'semantics'
    endpoint = f"https://{service_name}.search.windows.net/"


    search_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(admin_key)
        )
    data=create_documents(os.curdir)
    res=search_client.upload_documents(documents=data)
    print(res)

create_search_index()