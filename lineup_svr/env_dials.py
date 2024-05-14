import os
from elasticsearch import Elasticsearch

"""
    useful metadata for shared data
    WARN: singleton pattern
    
    FUTURE: use for containerised options storage
"""
# get name of db
env_conn = os.getenv('DB_CONN', 'http://localhost:9200') 

# create connection
db_conn = Elasticsearch([env_conn])

# get name of index
index_name = os.getenv('INDEX_NAME', 'lineup_faces')

# set a min_score, currently unused
min_score = float(os.getenv('MIN_SCORE', '1.54')) 
