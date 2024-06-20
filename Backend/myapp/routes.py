# from flask import Flask, Blueprint, jsonify, redirect, url_for ,request ,make_response ,redirect_template , session
from flask import Flask, Blueprint, jsonify, redirect, url_for, request, make_response, session
from datetime import datetime , timedelta
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
            statement = upload_data_pg1(df)
            # Do something with the dataframe (e.g., print or process)
            return jsonify({"message": statement,
                            "data": df_json}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
def upload_data_pg1 (df): 
    current_time = datetime.now()
    
    # Iterate over DataFrame rows
    for index, row in df.iterrows():
        qry_name = row['Description']
        sql_qry_1 = row['Query_1']
        sql_qry_2 = row['Query_2']
        suite_name = row['Suite_Name']
        sql_qry1_db_id = row['Query_1_DB']
        sql_qry2_db_id = row['Query_2_DB']
        qry_expected_op = row['Expected_Result']

        print(qry_name, sql_qry_1, sql_qry_2, suite_name, sql_qry1_db_id, sql_qry2_db_id, qry_expected_op)

        suite = MdSuite.query.filter_by(suite_name=suite_name).first()

        if suite:
            suite_id = suite.suite_id
        else:
            suite_id = None  # Handle the case where the suite is not found


            # Create a new record
        new_qry = MdSqlqry(
            qry_name=qry_name,
            sql_qry_1=sql_qry_1,
            sql_qry_2=sql_qry_2,
            suite_id=suite_id,
            sql_qry1_db_id=sql_qry1_db_id,
            sql_qry2_db_id=sql_qry2_db_id,
            qry_expected_op=qry_expected_op,
            created_dt=current_time,
            modified_dt=current_time
        )
        db.session.add(new_qry)
    
    db.session.commit()

    return 'Data inserted or updated successfully'
        
# sample dataframes for test purposes, to be replaced by data from PG or pd.read_excel 
# note import from backedn as one single df, will write code to auto split it here
# couldn't run due to Pg issue, need help in actually running the code

df_backend_fp = pd.read_excel("/Users/Raghav/Documents/Emory /Emory Srping Sem 2024/Internship/SQL-Query-Execution-Egnine/Backend/myapp/assets/test_1.xlsx") # dataframe to represent all the data regarding the queries in the backend

def pg_2_Db_to_Df (): 
    retrieval = session.query(MdSqlqry.qry_name,MdSqlqry.suite_id,MdSqlqry.sql_qry_1,MdSqlqry.sql_qry_2,MdSqlqry.qry_expected_op).all()
    df = pd.DataFrame(retrieval, columns=['Descritpion','suite_name','Query_1','Query_2','Expected_result'])
    return df

@main.route('/get_data', methods=['GET'])
@cross_origin()
def get_dataframes():
    df = pg_2_Db_to_Df
    return df.to_json(orient='records')



@main.route('/post_dataframe', methods=['POST'])
@cross_origin()
def receive_dataframe():
    data = request.get_json()
    received_df = pd.read_json(data['dataframe'], orient='split')
    print(received_df)
    return jsonify({'status': 'success', 'message': 'DataFrame received successfully'})

@main.route('/submit_selection', methods=['POST'])
@cross_origin
def submit_selection():
    selected_rows = request.json.get('selected_rows')
    df = pg_2_Db_to_Df
    selected_df = df[df.index.isin(selected_rows)]
    return selected_df.to_json(orient='records')


@main.route('/table1',methods = ['GET'])
@cross_origin()
def table1():
    df_sample = pd.read_excel("/Users/Raghav/Documents/Emory /Emory Srping Sem 2024/Internship/SQL-Query-Execution-Egnine/Backend/myapp/assets/Test2(summary_rep).xlsx")
    table = df_sample.to_json(orient="records")
    return jsonify({"data": table})

@main.route('/table2', methods = ['GET'])
@cross_origin()
def table2(): 
    df_sample = pd.read_excel("/Users/Raghav/Documents/Emory /Emory Srping Sem 2024/Internship/SQL-Query-Execution-Egnine/Backend/myapp/assets/test_1.xlsx")
    table = df_sample.to_json(orient="records")
    return jsonify({"data": table})

