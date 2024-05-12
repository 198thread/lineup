import os
from elasticsearch import Elasticsearch

# Get environment variables
env_conn = os.getenv('DB_CONN', 'http://localhost:9200') 

db_conn = Elasticsearch([env_conn])

index_name = os.getenv('INDEX_NAME', 'lineup_faces')
min_score = float(os.getenv('MIN_SCORE', '1.54')) 