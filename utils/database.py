
#database setting
from langchain_community.utilities import SQLDatabase
ENDPOINT=""
PORT=""
USER=""
REGION=""
DBNAME="" 
PASSWORD=""

CONNECTION_STRING = f"postgresql+psycopg2://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DBNAME}?sslmode=require"
db = SQLDatabase.from_uri(CONNECTION_STRING)
