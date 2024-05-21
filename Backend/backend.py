from flask import Flask, request, jsonify
import pandas as pd
import psycopg2
import os
import snowflake.connector 
from dotenv import load_dotenv

### dotenv imports ### 

your_account_identifier = os.getenv('your_account_identifier')
your_username = os.getenv('your_username')
password = os.getenv('your_password')
warehouse = os.getenv('your_warehouse')
database = os.getenv('your_database')
schema = os.getenv('your_schema')
sql_database = os.getenv('sql_database')

### Snow Flake connection ### 

conn_params_snowflake = {
    'account': your_account_identifier,
    'user': your_username,
    'password': password,
    'warehouse': warehouse,
    'database': database,
    'schema': schema
}

# Establish the connection
conn_snowflake = snowflake.connector.connect(**conn_params_snowflake)

# Create a cursor object
cur_snowflake = conn_snowflake.cursor()

try:
    cur_snowflake.execute("SELECT CURRENT_VERSION()")
    row = cur_snowflake.fetchone()
    print(f"Snowflake version: {row[0]}")

finally:
    cur_snowflake.close()
    conn_snowflake.close()

### PostGre portion ### 

# Database connection parameters
db_config = {
    'host': 'localhost',
    'dbname': sql_database,
    'user': your_username,
    'port': 5432
}

def connect_to_db():
    conn = psycopg2.connect(**db_config)
    return conn

### Flask portion ###

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, port=5000)