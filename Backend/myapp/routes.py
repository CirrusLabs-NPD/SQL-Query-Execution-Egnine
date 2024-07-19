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
import mysql.connector 
import re

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
            df.dropna(subset=['Query_1'])
            df = df.fillna('')
            df = df.drop_duplicates(subset=['Suite_Name','Description','Query_1','Query_2','Query_1_DB','Query_2_DB','Expected_Result'])
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



def pg_2_Db_to_Df ():
    session = db.session()
    try:
        retrieval = session.query(MdSqlqry.qry_name,MdSuite.suite_name,MdSqlqry.sql_qry_1,MdSqlqry.sql_qry_2,MdSqlqry.qry_expected_op).join(MdSuite, MdSqlqry.suite_id== MdSuite.suite_id).all()
        df = pd.DataFrame(retrieval, columns=['Description','Suite_Name','Query_1','Query_2','Expected_result'])
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
        result_1 = Sf_qry(row['sql_qry_1'])
        if row['sql_qry_2'] == '': 
            result_2 = ''
        else: 
            result_2 = Sf_qry(row['sql_qry_2'])
        # Create MdResultSet record
        result_set = MdResultSet(
            rs_batch_id=batch_id,
            qry_id=get_qry_id(row['qry_name']),
            sql_qry_1_op=result_1,
            sql_qry_2_op=result_2,
            qrn_execn_status=row['qrn_execn_status'],
            sql_qry_1=row['sql_qry_1'],  # Save SQL Query 1
            sql_qry_2=row['sql_qry_2'],  # Save SQL Query 2
            expected_op=row['expected_result']  # Save Expected Result
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
    if row['sql_qry_2'] == '':
        result2 = ''
    else:
        result2 = Sf_qry(row['sql_qry_2'])
    result1_pf = pass_fail(result1,row["expected_result"])
    result2_pf = pass_fail(result2,row["expected_result"])
    print(result1_pf)
    print(result2_pf)
    if row['sql_qry_2'] == '':
        if result1_pf:
            return "Pass"
        else:
            return "Fail"
    elif result1_pf and result2_pf: 
        return "Pass"
    else: 
        return "Fail"


def pass_fail(value,condition_str):
    condition_str = str(condition_str)
    if value == 'Query Does not exist' or value == 'Exception error' :
        return False
    if value == '':
        return False
    if type(value) == str:
        print(value)
        return False
    value = int(value)
    if condition_str[0]=='>':
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

# snow flake query function
def Sf_qry(qry):
        
    connection_string = "snowflake://CL1NARESH:1SQLupload@sg85113.central-india.azure/CL_TEST/PUBLIC?warehouse=COMPUTE_WH"

    # Parse the connection string and extract the necessary components
    pattern = re.compile(
        r'snowflake://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<account>[^/]+)/(?P<database>[^/]+)/(?P<schema>[^?]+)\?warehouse=(?P<warehouse>.+)')
    match = pattern.match(connection_string)

    if match:
        conn = snowflake.connector.connect(
            user=match.group('user'),
            password=match.group('password'),
            account=match.group('account'),
            database=match.group('database'),
            schema=match.group('schema'),
            warehouse=match.group('warehouse')
        )   
     
    cursor = conn.cursor()
    try: 
        cursor.execute(qry)
        result = cursor.fetchone()[0]
        return result
    except snowflake.connector.ProgrammingError:
        result = 'Query Does Not Exist'
        return result
    except Exception as e: 
        result = str(e)
        return result
    finally:
        cursor.close()
        conn.close()


def My_sql_qry(qry):
    connection_string = "mysql://avnadmin:AVNS_Z-En5yCZDiVyP6Wd52e@sql-engine-mysql-raghav2761-1c8d.i.aivencloud.com:11788/defaultdb?ssl-mode=REQUIRED"
    pattern = re.compile(r'mysql\+mysqlconnector://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<database>.+)')
    match = pattern.match(connection_string)

    if match:
        conn = mysql.connector.connect(
            host=match.group('host'),
            user=match.group('user'),
            password=match.group('password'),
            database=match.group('database'),
            port=match.group('port')
        )

    cursor = conn.cursor()
    try: 
        cursor.execute(qry)
        result = cursor.fetchone()[0]
        return result
    except mysql.connector.ProgrammingError:
        result = 'Query Does Not Exist'
        return result
    except Exception as e: 
        result = str(e)
        return result
    finally:
        cursor.close()
        conn.close()

 


def pg_3_report():
    retrieval = session.query().all()
    df = pd.DataFrame() # here there need to be columns created for each (batch_id, qry_name, pass/fail)
    return df 

@main.route('/table1', methods=['GET'])
@cross_origin()
def table1():
    result_sets = db.session.query(MdResultSet, MdSqlqry, MdSuite, QueryExecnBatch) \
        .join(MdSqlqry, MdResultSet.qry_id == MdSqlqry.qry_id) \
        .join(MdSuite, MdSqlqry.suite_id == MdSuite.suite_id) \
        .join(QueryExecnBatch, MdResultSet.rs_batch_id == QueryExecnBatch.batch_id) \
        .add_columns(MdResultSet.qrn_execn_status, MdResultSet.sql_qry_1, MdResultSet.sql_qry_2, MdResultSet.expected_op) \
        .all()

    suite_names = []
    run_dates = []
    batch_ids = []
    total_counts = []
    pass_counts = []
    fail_counts = []

    for result_set, sql_qry, suite, batch, qrn_execn_status, sql_qry_1, sql_qry_2, expected_op in result_sets:
        suite_names.append(suite.suite_name)
        run_dates.append(batch.batch_start_dt.strftime('%Y-%m-%d %H:%M:%S'))
        batch_ids.append(batch.batch_id)
        total_counts.append(1)
        if qrn_execn_status == 'Pass':
            pass_counts.append(1)
            fail_counts.append(0)
        else:
            pass_counts.append(0)
            fail_counts.append(1)

    df = pd.DataFrame({
        'Suite Name': suite_names,
        'Run Date': run_dates,
        'Batch Id': batch_ids,
        'Total Count': total_counts,
        'Pass Count': pass_counts,
        'Fail Count': fail_counts
    })

    grouped_df = df.groupby(['Batch Id', 'Suite Name', 'Run Date']).agg({
        'Total Count': 'sum',
        'Pass Count': 'sum',
        'Fail Count': 'sum'
    }).reset_index()

    grouped_df['Pass Percentage'] = (grouped_df['Pass Count'] / grouped_df['Total Count']) * 100
    grouped_df['Fail Percentage'] = (grouped_df['Fail Count'] / grouped_df['Total Count']) * 100
    grouped_df = grouped_df.drop(columns=['rs_id', 'qry_id','Batch Id'], errors='ignore')
    grouped_df = grouped_df.iloc[::-1]
    table = grouped_df.to_json(orient="records")
    return jsonify({"data": table})

@main.route('/table2', methods=['GET'])
@cross_origin()
def table2():
    subquery = db.session.query(func.max(QueryExecnBatch.batch_id).label('max_batch_id')).subquery()
    result_sets = db.session.query(
        MdSqlqry.qry_name.label('Query Name'),
        MdSuite.suite_name.label('Suite Name'),
        MdResultSet.sql_qry_1_op.label('SQL Query 1 Output'),
        MdResultSet.sql_qry_2_op.label('SQL Query 2 Output'),
        MdResultSet.qrn_execn_status.label('Query Execution Status'),
        MdResultSet.sql_qry_1.label('SQL Query 1 Name'),
        MdResultSet.sql_qry_2.label('SQL Query 2 Name'),
        QueryExecnBatch.batch_start_dt.label('Batch Start Time'),
        QueryExecnBatch.batch_end_dt.label('Batch End Time'),
        MdResultSet.expected_op.label('Expected Result')
    ).join(MdSqlqry, MdResultSet.qry_id == MdSqlqry.qry_id) \
        .join(MdSuite, MdSqlqry.suite_id == MdSuite.suite_id) \
        .join(QueryExecnBatch, MdResultSet.rs_batch_id == QueryExecnBatch.batch_id) \
        .all()

    df = pd.DataFrame(result_sets, columns=[
        'Query Description', 'Suite Name', 'SQL Query 1 Output', 'SQL Query 2 Output',
        'Query Execution Status', 'SQL Query 1 Name', 'SQL Query 2 Name',
        'Batch Start Time', 'Batch End Time', 'Expected Result'
    ])
    df = df[['Suite Name', 'Query Description', 'SQL Query 1 Name', 'SQL Query 2 Name',
             'SQL Query 1 Output', 'SQL Query 2 Output', 'Expected Result',
             'Query Execution Status', 'Batch Start Time', 'Batch End Time']]
    df['Batch Start Time'] = pd.to_datetime(df['Batch Start Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['Batch End Time'] = pd.to_datetime(df['Batch End Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.iloc[::-1]
    table = df.to_json(orient="records")
    return jsonify({"data": table}), 200

@main.route('/addSuite', methods=['POST'])
@cross_origin()
def insert_suite():
    data = request.get_json()
    if not data or 'suite_name' not in data or 'suite_description' not in data or 'suite_created_by' not in data:
        return jsonify({"error": "Invalid data"}), 400
    suite_name = data['suite_name']
    suite_description = data['suite_description']
    suite_created_by = data['suite_created_by']
 
    existing_suite = db.session.query(MdSuite).filter_by(suite_name=suite_name).first()
    if existing_suite:
        return jsonify({"error": "Suite with this name already exists"}), 400

    # Get the maximum suite_id and increment by 1
    max_suite_id = db.session.query(db.func.max(MdSuite.suite_id)).scalar()
    new_suite_id = max_suite_id + 1 if max_suite_id else 1
    # Create a new MdSuite instance with default values
    new_suite = MdSuite(
        suite_id= new_suite_id,
        suite_name=suite_name,
        suite_description=suite_description,
        suite_created_by=suite_created_by,
        suite_priority=None,
        suite_created_dt=datetime.now(),
        suite_modified_dt=None
    )
    db.session.add(new_suite)
    try:
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@main.route('/getSuite', methods=['GET'])
@cross_origin()
def get_suites():
    try:
        # Query all records from the MdSuite table
        suites = MdSuite.query.all()
        # Convert the records into a list of dictionaries
        suite_list = [{
            'suite_id': suite.suite_id,
            'suite_name': suite.suite_name,
            'suite_description':suite.suite_description,
            'suite_created_by':suite.suite_created_by,
            "suite_priority":suite.suite_priority,
            'suite_created_dt': suite.suite_created_dt,
            'suite_modified_dt': suite.suite_modified_dt
        } for suite in suites]
        # Return the list as a JSON response
        suite_list.sort(key=lambda x: x['suite_id'], reverse=True)
        return jsonify({"data": suite_list}), 200
    except Exception as e:
        # Handle any errors that occur during the query
        return jsonify({"error": str(e)}), 500