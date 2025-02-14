from openai import AzureOpenAI
import os 


def create_embeddings(text):
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("OPENAI_API_VERSION")
    )

    response = client.embeddings.create(
        input=text,
        model=os.getenv("EMBEDDING_MODEL")
    )

    # Extract the embeddings
    embeddings = response.data[0].embedding

    return embeddings