import pandas as pd 
import pymysql 
from sqlalchemy import create_engine
import MySQLdb

host = "localhost"
user = "root"
password = ""
db = "trips_db"

# Construct the connection URL with an empty password
connection_url = f"mysql+mysqldb://{user}:{password}@{host}/{db}"

# Create an SQLAlchemy engine and connect to the database
engine = create_engine(connection_url)
conn = engine.connect()

df = pd.read_csv("./data/yellow_tripdata_2021-01.csv.gz",nrows=1000,compression='gzip')

df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

#print(df.head())
print(df.info())
#df.to_sql(name="yellow_tripdata",con=conn,index=False)