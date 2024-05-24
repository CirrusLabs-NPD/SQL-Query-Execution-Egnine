from flask import Flask, request, jsonify
import pandas as pd
import psycopg2
import os
import snowflake.connector 
from dotenv import load_dotenv

from flask_cors import CORS , cross_origin  # Import CORS
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
def snowflake_establish(): 
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

# conn = connect_to_db
# cur = conn.cursor()

# cur.close()
# conn.close()
### Flask portion ###

app = Flask(__name__)
CORS(app)
allowed_origins = [
    "http://localhost:3000",  # Replace with the actual domains you want to allow
]
CORS(app, origins=allowed_origins, methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Authorization"], supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        # Process the file using pandas
        try:
            df = pd.read_excel(file_path)
            # Do something with the dataframe (e.g., print or process)
            return jsonify({"message": "File uploaded and processed successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)



### start with the SQL queries 

# server_name = 
# server_id = 


# df["query_1"]
# df["query_2"]