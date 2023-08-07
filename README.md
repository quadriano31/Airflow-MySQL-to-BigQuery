# Airflow-MySQL-to-BigQuery
 Using Binlog replication to perform CDC


## Folder structure
```bash
root/
├──airflow_image
│   └── Dockerfile
│   └── requirements.txt
├── dags/
│   └── package/
│      └── config.py
│   └── full_load.py
│   └── incremental_load_cdc.py
├── data/
│   └── yellow_tripdata_2021-01.csv.gz
├── logs/
├── .env
├── plugins
├── load_data_to_db.py
├── load_incremental_to_db.py
├── my.cnf
└── docker-compose.yml
```
## PREREQUISITE 

Docker & Docker compose 

Clone the repo and run docker compose up, Ensure that all containers are healthy

## Loading the data to MySQL Server 

To Download the Employee DB and load to MySQL
```bash 
    run docker container exec -it mysql-container-id /bin/bash 
    bash curl -LOk https://github.com/datacharmer/test_db/archive/refs/heads/master.zip
    yum install unzip 
    cd test_db-master/
    mysql -t < employees.sql

```

## To Setup MYSQL connection to Airflow 

```bash
    run docker network inspect 
    Copy the gateway  
    This will be used to setup the connection in airflow 
    The gateway will be the host the Airflow will use to connect to MySQL 
    Login -- root
    Leave password blank 
```


## TO ENABLE BIN LOG REPLICATION ON MYSQL 

Create a .cnf file and map it to MySQL 

```bash
[mysqld]
server-id		 = 1
log_bin			 = bin.log
expire_logs_days = 10
max_binlog_size  = 100M
binlog-format    = row #Very important if you want to receive write, update and delete row events
```

Enter the container 

### 
if you get the error mysqld: [Warning] World-writable config file 

run the comand below 

```bash
    run docker container exec -it mysql-container-id /bin/bash
    enter the container and RUN chmod 644 /etc/mysql/conf.d/my.cnf


```
## TO confirm if BINARY LOG REPLICATION IS ON 
```bash 
    mysql -uroot
    set @@global.show_compatibility_56=ON; 
    select variable_value as "BINARY LOGGING STATUS (log_bin) :: " 
    from information_schema.global_variables where variable_name='log_bin';
```

### CREATE A GCP PROJECT 

Create a GCP project, BigQuery Dataset and Table 
Modify the CONFIG.py file and add the new details created accordingly 
Create BigQuery Dataset [click here](https://cloud.google.com/bigquery/docs/datasets)

### Permisions to give service account 

```bash
Bigquery Admin or all of the following 
BigQuery Connection admin
Bigquery Connection user
BigQuery user
```
## Improvement 
```bash
Add CI/CD 
Migrate Dags to GCP Cloud Composer
Integrate with GCP Secrets

```

### Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please create a GitHub issue or submit a pull request.

### License
This project is licensed under the MIT License.


