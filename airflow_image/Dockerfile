# Base image
FROM apache/airflow:2.6.3

# User airflow
USER airflow

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements.txt
COPY requirements.txt .

# Install python packages
RUN pip install -r requirements.txt