# from flask import Flask, Blueprint, jsonify, redirect, url_for ,request ,make_response ,redirect_template , session
from flask import Flask, Blueprint, jsonify, redirect, url_for, request, make_response, session
from datetime import datetime , timedelta
import jwt
from functools import wraps
from myapp.auth import create_token, decode_token
from .extensions import db
from .models import MdDatabase, MdDbConfig ,MdPrivs ,MdResultSet ,MdRole ,MdSqlqry ,MdSuite ,MdTempResultSet ,User, QueryExecnBatch
import requests
from flask_bcrypt import Bcrypt  
from flask_cors import CORS , cross_origin  # Import CORS
from sqlalchemy.orm.exc import NoResultFound

import json
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity

import os
import pandas as pd 
import random

main = Blueprint('main', __name__)
bcrypt = Bcrypt()

allowed_origins = [
    "http://localhost:3000"

]

CORS(main, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@main.route('/upload', methods=['POST'])
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
            df_f10 = df.head(10)
            df_json = df_f10.to_json(orient="records")
            # Do something with the dataframe (e.g., print or process)
            return jsonify({"message": "File uploaded and processed successfully",
                            "data": df_json}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
# sample dataframes for test purposes, to be replaced by data from PG or pd.read_excel 
# note import from backedn as one single df, will write code to auto split it here
# couldn't run due to Pg issue, need help in actually running the code

df_backend_fp = pd.read_excel("/Users/Raghav/Documents/Emory /Emory Srping Sem 2024/Internship/SQL-Query-Execution-Egnine/Backend/myapp/assets/test_1.xlsx") # dataframe to represent all the data regarding the queries in the backend

def suite_name_array_creation (df): 
    suite_names = df['Suite_Name'].unique()  
    return suite_names

def array_of_df_creation (df, names): 
    df2 = []
    for x in names: 
        split_df = df[df['Suite_Name']==x]
        df2.append(split_df)
    return df2

def dataframes_to_json(dfs, names):
    dfs_json = [df.to_json(orient='split') for df in dfs]
    return jsonify({'dataframes': dfs_json, 'names': names})

@main.route('/get_dataframes', methods=['GET'])
@cross_origin()
def get_dataframes():
    df_names = suite_name_array_creation(df_backend_fp)
    dataframes = array_of_df_creation(df_backend_fp, df_names)
    return dataframes_to_json(dataframes, df_names)



@main.route('/receive_dataframe', methods=['POST'])
@cross_origin()
def receive_dataframe():
    data = request.get_json()
    received_df = pd.read_json(data['dataframe'], orient='split')
    # Process the received DataFrame as needed
    print(received_df)
    return jsonify({'status': 'success', 'message': 'DataFrame received successfully'})


def generate_table(n):
    return [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]

@main.route('/table1',methods = ['GET'])
@cross_origin()
def table1():
    df_sample = pd.read_excel("/Users/Raghav/Documents/Emory /Emory Srping Sem 2024/Internship/SQL-Query-Execution-Egnine/Backend/myapp/assets/test_1.xlsx")
    table_data = df_sample.values.tolist()  # Convert DataFrame to list of lists
    table = {'table': table_data} 
    return jsonify(table)

@main.route('/table2', methods = ['GET'])
@cross_origin()
def table2():
    n = 5  # You can change the size as needed
    table = generate_table(n)
    return jsonify(table)

