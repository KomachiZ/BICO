
from utils.bedrock_clients import osl_client, client
import json
from langchain_core.tools import tool
# Setting
index_name = ""
dimensions = 1024
model_id = "amazon.titan-embed-text-v2:0"
field_name = ""

def gen_emb(input_text):
      native_request = {"inputText": input_text}

      # Convert the native request to JSON.
      request = json.dumps(native_request)

      # Invoke the model with the request.
      response = client.invoke_model(modelId=model_id, body=request)

      # Decode the model's native response body.
      model_response = json.loads(response["body"].read())

      # Extract and print the generated embedding and the input text token count.
      embedding = model_response["embedding"]
      #input_token_count = model_response["inputTextTokenCount"]
      return embedding


@tool
def match_accurate_propernoun_tool(input_nouns): 
      """ Accurate matching of proper nouns from 'input_nouns', return an accurate name which commonly used as filter conditions."""
      query_emb = gen_emb(input_nouns)
      search_query = {"query": {"knn": {f"{index_name}": {"vector": query_emb, "k": 1}}}}
      results = osl_client.search(index=index_name, body=search_query)
      return results["hits"]["hits"][0]['_source'][f"{field_name}"]

@tool
def AskKnowledgeBaseAboutQuicksight(query):
      """ Retrieve and generate a response based on the query about xxx from knowledgebase. """
      response = client.retrieve_and_generate(
            input= {
                  'text': f"{query}"
            },
            retrieveAndGenerateConfiguration={
                  'type': 'KNOWLEDGE_BASE',
                  'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': "",
                        'modelArn': ''
                  }
            },
             )
      return response['output']['text']