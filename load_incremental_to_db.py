import pandas as pd
import pymysql
from sqlalchemy import create_engine
import MySQLdb
import time

host = "localhost"
user = "root"
password = ""
db = "trips_db"

# Construct the connection URL with an empty password
connection_url = f"mysql+mysqldb://{user}:{password}@{host}/{db}"

# Create an SQLAlchemy engine and connect to the database
engine = create_engine(connection_url)
conn = engine.connect()

chunk_size = 1000  # Number of rows to load per iteration
total_iterations = 100  # Number of iterations

for iteration in range(total_iterations):
    start_row = iteration * chunk_size
    
    df = pd.read_csv("./data/yellow_tripdata_2021-01.csv.gz", 
                     skiprows=range(1, start_row + 1),  # Skip to the next batch of data
                     nrows=chunk_size, 
                     compression='gzip')

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # Load the batch into the database
    df.to_sql(name="yellow_tripdata", con=conn, index=False, if_exists='append')
    print(f"loading {iteration} batch")
    # Sleep for 5 minutes
    time.sleep(30)  # 300 seconds = 5 minutes
