import time
from datetime import datetime,timedelta
import os

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

from airflow.providers.mysql.hooks.mysql import MySqlHook
from google.cloud import bigquery
from google.oauth2 import service_account

# Import other packages
from packages.config import CONFIG

# Set Google Cloud credentials file path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/opt/airflow/dags/key.json'


# Define default_args dictionary for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 2, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Instantiate the DAG
dag = DAG(
    'full_copy',
    default_args=default_args,
    description='DAG to extract data from MySQL and load it into Google BigQuery',
    schedule_interval="0 23 * * 0",
    tags=['load_gcp'],
    catchup=False,
)

# Define the SQL extract task
def check_table_exist():
    try:
        hook = MySqlHook(mysql_conn_id="mysql_conn_id", schema='employees')
        query = f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{CONFIG.DB}' AND table_name = '{CONFIG.TABLE_NAME}'
        """
        records = hook.get_records(sql=query)
        print(records)
        tbl_name = records[0]
        return tbl_name
    except Exception as e:
        print("Data extract error: " + str(e))

check_table_exist_task = PythonOperator(
    task_id='sql_extract',
    python_callable=check_table_exist,
    dag=dag,
)

#check bigquery table exist 
def create_bigquery_table():
    try:
        client = bigquery.Client()
        dataset_ref = client.dataset(CONFIG.DATASET_REF)
        table_ref = dataset_ref.table(CONFIG.TABLE_NAME)
        schema = []  # Define your schema here
        
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table, exists_ok=True)  # Create if not exists
        print(f"BigQuery table {CONFIG.TABLE_NAME} created or already exists.")
    except Exception as e:
        print("BigQuery table creation error: " + str(e))

create_bigquery_table_task = PythonOperator(
    task_id='create_bigquery_table',
    python_callable=create_bigquery_table,
    dag=dag,
)

# Define the GCP load task
def gcp_load(tbl_name):
    try:
        client = bigquery.Client()
        job_config = bigquery.job.LoadJobConfig()
        project_id = CONFIG.PROJECT_ID
        dataset_ref = CONFIG.DATASET_REF
        TABLE = CONFIG.TABLE_NAME
        table_id = f"{project_id}.{dataset_ref}.{TABLE}"
        rows_imported = 0
        job_config = bigquery.job.LoadJobConfig()
        # Set write_disposition parameter as WRITE_APPEND for appending to the table
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

        hook = MySqlHook(mysql_conn_id="mysql_conn_id", schema='employees')

        for table_name in tbl_name:
            # print(table_name)
            query = f'SELECT * FROM {table_name}'
            df = hook.get_pandas_df(query)
            print(f'Importing rows {rows_imported} to {rows_imported + len(df)}... for table {table_name}')
            
            # Then proceed with the data loading
            job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()  
            table = client.get_table(table_id)  # Make an API request.
            print(
                f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}"
            )

    except Exception as e:
        print("Data load error: " + str(e))

gcp_load_task = PythonOperator(
    task_id='gcp_load',
    python_callable=gcp_load,
    op_args=[check_table_exist_task.output],
    dag=dag,
)

check_table_exist_task >> create_bigquery_table_task >> gcp_load_task
