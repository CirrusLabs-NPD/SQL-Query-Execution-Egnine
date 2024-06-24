# from flask import Flask, Blueprint, jsonify, redirect, url_for ,request ,make_response ,redirect_template , session
from flask import Flask, Blueprint, jsonify, redirect, url_for, request, make_response, session
from datetime import datetime , timedelta
from .extensions import db
from .models import MdDatabase, MdDbConfig ,MdPrivs ,MdResultSet ,MdRole ,MdSqlqry ,MdSuite ,User, QueryExecnBatch
import requests
from flask_bcrypt import Bcrypt  
from flask_cors import CORS , cross_origin  # Import CORS
from sqlalchemy.orm.exc import NoResultFound
import json
from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity
import os
import pandas as pd 
import random
import snowflake.connector
from sqlalchemy import desc, func

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

        
        existing_qry = MdSqlqry.query.filter_by(qry_name=qry_name).first()

        if existing_qry:
        # Update existing record
            existing_qry.sql_qry_1 = sql_qry_1
            existing_qry.sql_qry_2 = sql_qry_2
            existing_qry.suite_id = suite_id
            existing_qry.modified_dt = current_time
        else:
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

            # Create a new record
        # new_qry = MdSqlqry(
        #     qry_name=qry_name,
        #     sql_qry_1=sql_qry_1,
        #     sql_qry_2=sql_qry_2,
        #     suite_id=suite_id,
        #     sql_qry1_db_id=sql_qry1_db_id,
        #     sql_qry2_db_id=sql_qry2_db_id,
        #     qry_expected_op=qry_expected_op,
        #     created_dt=current_time,
        #     modified_dt=current_time
        # )
        # db.session.add(new_qry)
    
    db.session.commit()

    return 'Data inserted or updated successfully'
        
# sample dataframes for test purposes, to be replaced by data from PG or pd.read_excel 
# note import from backedn as one single df, will write code to auto split it here
# couldn't run due to Pg issue, need help in actually running the code

df_backend_fp = pd.read_excel("/Users/Raghav/Documents/Emory /Emory Srping Sem 2024/Internship/SQL-Query-Execution-Egnine/Backend/myapp/assets/test_1.xlsx") # dataframe to represent all the data regarding the queries in the backend

def pg_2_Db_to_Df ():
    session = db.session()
    try:
        retrieval = session.query(MdSqlqry.qry_name,MdSuite.suite_name,MdSqlqry.sql_qry_1,MdSqlqry.sql_qry_2,MdSqlqry.qry_expected_op).join(MdSuite, MdSqlqry.suite_id== MdSuite.suite_id).all()
        df = pd.DataFrame(retrieval, columns=['Descritpion','Suite_Name','Query_1','Query_2','Expected_result'])
        print(df)
        return df
    finally:
        session.close()

@main.route('/get_data', methods=['GET'])
@cross_origin()
def get_dataframes():
    df = pg_2_Db_to_Df()
    table = df.to_json(orient='records')
    return jsonify({"data": json.loads(table)})

@main.route('/submit_selection', methods=['POST'])
@cross_origin()
def submit_selection():

    data = request.get_json()  # Get the JSON data sent to the endpoint

    if not data or 'tables' not in data:
        return jsonify({"error": "Invalid data"}), 400

    # Combine all the dataframes from different suites into a single dataframe
    dfs = []
    for table in data['tables']:
        df = pd.DataFrame(table['values'])
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    
    # You can now process this combined_df as needed
    combined_df.rename(columns={'column_0':'qry_name',
                                'column_1':'expected_result',
                                'column_2':'sql_qry_1',
                                'column_3':'sql_qry_2',
                                'column_4':'Suite_Name'},inplace=True)
    combined_df['qry_name'] = combined_df['qry_name'].astype(str)
    combined_df['expected_result'] = combined_df['expected_result'].astype(str)
    combined_df['sql_qry_1'] = combined_df['sql_qry_1'].astype(str)
    combined_df['sql_qry_2'] = combined_df['sql_qry_2'].astype(str)
    combined_df['Suite_Name'] = combined_df['Suite_Name'].astype(str)
    if 'sql_qry_1' not in combined_df.columns or 'sql_qry_2' not in combined_df.columns:
        return jsonify({"error": "'sql_qry_1' or 'sql_qry_2' column not found"}), 400
    combined_df["qrn_execn_status"] = combined_df.apply(pass_fail_create, axis=1)
    batch = QueryExecnBatch(
        batch_dt=datetime.now(),
        batch_start_dt=datetime.now(),
        batch_end_dt=datetime.now(),
        batch_status='completed'
    )
    db.session.add(batch)
    db.session.commit()

    batch_id = batch.batch_id  # Get the ID of the newly created batch

    # Process each row in the DataFrame to create MdResultSet records
    for index, row in combined_df.iterrows():
        # Create MdResultSet record
        result_set = MdResultSet(
            rs_batch_id=batch_id,
            qry_id=get_qry_id(row['qry_name']),
            sql_qry_1_op=row['sql_qry_1'],
            sql_qry_2_op=row['sql_qry_2'],
            qrn_execn_status=row['qrn_execn_status']
        )
        db.session.add(result_set)

    try:
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def get_qry_id(qry_name):
    # Function to retrieve qry_id from MdSqlqry based on qry_name
    qry = MdSqlqry.query.filter_by(qry_name=qry_name).first()
    if qry:
        return qry.qry_id
    else:
        return None  # Handle the case where qry_name is not found in MdSqlqry

def pass_fail_create(row):
    result1 = Sf_qry(row['sql_qry_1'])
    result2 = Sf_qry(row['sql_qry_2'])
    result1_pf = pass_fail(result1,row["expected_result"])
    result2_pf = pass_fail(result2,row["expected_result"])
    if result1_pf and result2_pf: 
        return "Pass"
    else: 
        return "Fail"


def pass_fail(condition_str,value):
    if type(value) == str: 
        return False
    if condition_str.startswith(">"):
        threshold = float(condition_str[1:])
        if value > threshold:
            return True
        else:
            return False
    elif condition_str.startswith("<"):
        threshold = float(condition_str[1:])
        if value < threshold:
            return True
        else:
            return False
    elif condition_str.startswith("=="):
        target = float(condition_str[2:])
        if value == target:
            return True
        else:
            return False
    else:
        return False


def Sf_qry(qry):
        
    conn = snowflake.connector.connect(
        user='RAGHAVAGARWALLA',
        password='Dvcn8288--',
        account='mg07208.central-india.azure',
        warehouse='COMPUTE_WH',
        database='CLTEST',
        schema='PUBLIC'
    )
    cursor = conn.cursor()
    try: 
        cursor.execute(qry)
        result = cursor.fetchone()[0]
        return result
    except snowflake.connector.ProgrammingError:
        result = 'fail'
        return result
    except Exception: 
        result = 'fail'
        return result
    finally:
        cursor.close()
        conn.close()

def pg_3_report():
    retrieval = session.query().all()
    df = pd.DataFrame() # here there need to be columns created for each (batch_id, qry_name, pass/fail)
    return df 

@main.route('/table1',methods = ['GET'])
@cross_origin()
def table1():
        # Query MdResultSet and join with related tables to get necessary data
    result_sets = db.session.query(MdResultSet, MdSqlqry, MdSuite, QueryExecnBatch)\
            .join(MdSqlqry, MdResultSet.qry_id == MdSqlqry.qry_id)\
            .join(MdSuite, MdSqlqry.suite_id == MdSuite.suite_id)\
            .join(QueryExecnBatch, MdResultSet.rs_batch_id == QueryExecnBatch.batch_id)\
            .add_columns(MdResultSet.qrn_execn_status)\
            .all()

        # Create lists to store data
    suite_names = []
    run_dates = []
    batch_ids = []
    total_counts = []
    pass_counts = []
    fail_counts = []

        # Iterate through result_sets and calculate counts and percentages
    for result_set, sql_qry, suite, batch, qrn_execn_status in result_sets:
            suite_names.append(suite.suite_name)
            run_dates.append(batch.batch_start_dt.strftime('%d-%b'))
            batch_ids.append(batch.batch_id)  # Assuming you want only day and month
            total_counts.append(1)  # Each row represents one query execution
            if qrn_execn_status == 'pass':
                pass_counts.append(1)
                fail_counts.append(0)
            else:
                pass_counts.append(0)
                fail_counts.append(1)

    # Create DataFrame from collected lists
    df = pd.DataFrame({
        'Suite_name': suite_names,
        'Run_Date': run_dates,
        'Batch_id': batch_ids,
        'Total_cnt': total_counts,
        'Pass_cnt': pass_counts,
        'Fail_cnt': fail_counts
    })

    # Group by Suite_name and Run_Date to calculate aggregates
    grouped_df = df.groupby(['Batch_id','Suite_name','Run_Date']).agg({
        'Total_cnt': 'sum',
        'Pass_cnt': 'sum',
        'Fail_cnt': 'sum'
    }).reset_index()

    # Calculate Pass Percentage and Fail Percentage
    grouped_df['Pass_Percentage'] = (grouped_df['Pass_cnt'] / grouped_df['Total_cnt']) * 100
    grouped_df['Fail_Percentage'] = (grouped_df['Fail_cnt'] / grouped_df['Total_cnt']) * 100

    # Drop unnecessary columns if needed (like rs_id and qry_id)
    grouped_df = grouped_df.drop(columns=['rs_id', 'qry_id'], errors='ignore')
    table = grouped_df.to_json(orient="records")
    return jsonify({"data": table})

@main.route('/table2', methods = ['GET'])
@cross_origin()
def table2(): 
        subquery = db.session.query(func.max(QueryExecnBatch.batch_id).label('max_batch_id')).subquery()

        # Query to fetch MdResultSet with the latest batch_id and join with related tables
        result_sets = db.session.query(MdSqlqry.qry_name, MdSuite.suite_name, MdResultSet.sql_qry_1_op, MdResultSet.sql_qry_2_op, MdResultSet.qrn_execn_status)\
            .join(MdSqlqry, MdResultSet.qry_id == MdSqlqry.qry_id)\
            .join(MdSuite, MdSqlqry.suite_id == MdSuite.suite_id)\
            .join(QueryExecnBatch, MdResultSet.rs_batch_id == QueryExecnBatch.batch_id)\
            .filter(QueryExecnBatch.batch_id == subquery.c.max_batch_id)\
            .all()
        for result_set in result_sets:
            print(result_set)  # This will help you see what data is retrieved
        # Create DataFrame from the query result, excluding rs_id
        df = pd.DataFrame(result_sets, columns=['qry_name', 'Suite_name', 'sql_qry_1_op', 'sql_qry_2_op', 'qrn_execn_status'])

        # Convert DataFrame to JSON and return as response
        table = df.to_json(orient="records")
        return jsonify({"data": table}), 200

