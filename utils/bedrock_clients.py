# Opensearch & Quicksight Setting
import boto3
from botocore.config import Config
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


client_qs = boto3.client('quicksight', region_name='us-west-2')

#connection
host = '' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
region = ''
service = ''
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

osl_client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)

index_name = ""
dimensions = 1024

client = boto3.client("bedrock-runtime", region_name="us-west-2",config=Config(retries={'max_attempts': 10}))