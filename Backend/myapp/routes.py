from flask import Flask, Blueprint, jsonify, redirect, url_for, request, make_response, session
from datetime import datetime, timedelta
from .extensions import db
from .models import MdDatabase, MdDbConfig, MdPrivs, MdResultSet, MdRole, MdSqlqry, MdSuite, User, QueryExecnBatch
import requests
from flask_bcrypt import Bcrypt  
from flask_cors import CORS, cross_origin
from sqlalchemy.orm.exc import NoResultFound
import json
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
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

# Define a dictionary to map database names to query execution functions
DB_QUERY_FUNCTIONS = {
    "Snowflake": "Sf_qry",
    "MySQL": "My_sql_qry"
}

def execute_query(db_name, query):
    if db_name in DB_QUERY_FUNCTIONS:
        return globals()[DB_QUERY_FUNCTIONS[db_name]](query)
    else:
        return 'Unsupported database name'

@main.route('/get_suite_list', methods=['GET'])
@cross_origin()
def get_suite_list():
    try:
        suite_names = db.session.query(MdSuite.suite_name).all()
        suite_name_list = [suite_name[0] for suite_name in suite_names]
        return jsonify({"suites": suite_name_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    if 'file' not in request.files or 'suite_name' not in request.form:
        return jsonify({"error": "File and suite_name are required"}), 400
    file = request.files['file']
    suite_name = request.form['suite_name']
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
            df['Suite_Name'] = suite_name  # Add suite name column
            df = df.drop_duplicates(subset=['Suite_Name', 'Description', 'Query_1', 'Query_2', 'Query_1_DB', 'Query_2_DB', 'Expected_Result'])
            df_f10 = df.head(10)
            df_json = df_f10.to_json(orient="records")
            statement = upload_data_pg1(df)

            return jsonify({"message": statement, "data": df_json}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def upload_data_pg1(df):
    current_time = datetime.now()
    
    for index, row in df.iterrows():
        qry_name = row['Description']
        sql_qry_1 = row['Query_1']
        sql_qry_2 = row['Query_2']
        suite_name = row['Suite_Name']
        qry_expected_op = row['Expected_Result']

        # Query the database to get the suite ID
        suite = MdSuite.query.filter_by(suite_name=suite_name).first()
        suite_id = suite.suite_id if suite else None

        # Query the database to get the database ID for Query_1_DB
        db_1 = MdDatabase.query.filter_by(db_name=row['Query_1_DB']).first()
        sql_qry1_db_id = db_1.db_id if db_1 else None

        # Query the database to get the database ID for Query_2_DB
        db_2 = MdDatabase.query.filter_by(db_name=row['Query_2_DB']).first()
        sql_qry2_db_id = db_2.db_id if db_2 else None

        print(qry_name, sql_qry_1, sql_qry_2, suite_name, sql_qry1_db_id, sql_qry2_db_id, qry_expected_op)

        existing_qry = MdSqlqry.query.filter_by(qry_name=qry_name).first()

        if existing_qry:
            existing_qry.sql_qry_1 = sql_qry_1
            existing_qry.sql_qry_2 = sql_qry_2
            existing_qry.suite_id = suite_id
            existing_qry.sql_qry1_db_id = sql_qry1_db_id
            existing_qry.sql_qry2_db_id = sql_qry2_db_id
            existing_qry.qry_expected_op = qry_expected_op
            existing_qry.modified_dt = current_time
        else:
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

@main.route('/submit_selection', methods=['POST'])
@cross_origin()
def submit_selection():
    data = request.get_json()
    if not data or 'tables' not in data:
        return jsonify({"error": "Invalid data"}), 400

    dfs = []
    for table in data['tables']:
        df = pd.DataFrame(table['values'])
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    
    combined_df.rename(columns={
        'column_0': 'qry_name',
        'column_1': 'expected_result',
        'column_2': 'sql_qry_1',
        'column_3': 'sql_qry_2',
        'column_4': 'Suite_Name'
    }, inplace=True)
    
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

    batch_id = batch.batch_id

    for index, row in combined_df.iterrows():
        qry_id, db_name1, db_name2 = get_qry_id_and_db_names(row['qry_name'])
        result_1 = execute_query(db_name1, row['sql_qry_1'])
        result_2 = execute_query(db_name2, row['sql_qry_2']) if row['sql_qry_2'] else ''
        
        result_set = MdResultSet(
            rs_batch_id=batch_id,
            qry_id=qry_id,
            sql_qry_1_op=result_1,
            sql_qry_2_op=result_2,
            qrn_execn_status=row['qrn_execn_status'],
            sql_qry_1=row['sql_qry_1'],
            sql_qry_2=row['sql_qry_2'],
            expected_op=row['expected_result']
        )
        db.session.add(result_set)

    try:
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def get_qry_id_and_db_names(qry_name):
    qry = MdSqlqry.query.filter_by(qry_name=qry_name).first()
    if qry:
        db_name1 = MdDatabase.query.filter_by(db_id=qry.sql_qry1_db_id).first().db_name
        db_name2 = MdDatabase.query.filter_by(db_id=qry.sql_qry2_db_id).first().db_name
        return qry.qry_id, db_name1, db_name2
    else:
        return None, None, None

def pass_fail_create(row):
    qry_id, db_name1, db_name2 = get_qry_id_and_db_names(row['qry_name'])
    result1 = execute_query(db_name1, row['sql_qry_1'])
    result2 = execute_query(db_name2, row['sql_qry_2']) if row['sql_qry_2'] else ''

    if any(comp in row['expected_result'] for comp in ['aggregate_compare', 'structure_compare', 'sample_rows_compare']):
        condition_str = row['expected_result'].split(':')[1]
        pass_fail_status = pass_fail(result1, result2, condition_str)
    else:
        result1_pf = pass_fail(result1, result1, row["expected_result"])
        result2_pf = pass_fail(result2, result2, row["expected_result"])
        pass_fail_status = result1_pf and result2_pf if row['sql_qry_2'] else result1_pf
    
    return "Pass" if pass_fail_status else "Fail"

def pass_fail(value1, value2, condition_str):
    # Handle special cases based on the condition string
    if condition_str == 'aggregate_compare':
        return compare_aggregate(value1, value2)
    elif condition_str == 'structure_compare':
        return compare_structure(value1, value2)
    elif condition_str == 'sample_rows_compare':
        return compare_sample_rows(value1, value2)
    
    # Original comparison logic
    if value1 in ['Query Does not exist', 'Exception error', ''] or value2 in ['Query Does not exist', 'Exception error', '']:
        return False
    if isinstance(value1, str) or isinstance(value2, str):
        return False

    value1 = int(value1)
    value2 = int(value2)

    if condition_str.startswith(">"):
        threshold = float(condition_str[1:])
        return value1 > threshold
    elif condition_str.startswith("<"):
        threshold = float(condition_str[1:])
        return value1 < threshold
    elif condition_str.startswith("=="):
        target = float(condition_str[2:])
        return value1 == target
    else:
        return False

def compare_aggregate(value1, value2):
    # Assuming value1 and value2 are lists of dictionaries with aggregated data
    if not value1 or not value2:
        return False
    
    aggregate1 = sum(item['value'] for item in value1)
    aggregate2 = sum(item['value'] for item in value2)
    
    return aggregate1 == aggregate2

def compare_structure(value1, value2):
    # Assuming value1 and value2 are lists of column names
    if not value1 or not value2:
        return False
    
    return set(value1) == set(value2)

def compare_sample_rows(value1, value2):
    # Assuming value1 and value2 are lists of dictionaries representing rows
    if not value1 or not value2:
        return False

    sample1 = value1[:4]  # Get the first 4 rows from value1
    sample2 = value2[:4]  # Get the first 4 rows from value2
    
    return sample1 == sample2

def Sf_qry(qry):
    connection_string = "snowflake://CL1NARESH:1SQLupload@sg85113.central-india.azure/CL_TEST/PUBLIC?warehouse=COMPUTE_WH"
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
        return 'Query Does Not Exist'
    except Exception as e:
        return str(e)
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
        return 'Query Does Not Exist'
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

def pg_2_Db_to_Df():
    session = db.session()
    try:
        retrieval = session.query(MdSqlqry.qry_name, MdSuite.suite_name, MdSqlqry.sql_qry_1, MdSqlqry.sql_qry_2, MdSqlqry.qry_expected_op).join(MdSuite, MdSqlqry.suite_id == MdSuite.suite_id).all()
        df = pd.DataFrame(retrieval, columns=['Description', 'Suite_Name', 'Query_1', 'Query_2', 'Expected_result'])
        return df
    finally:
        session.close()

@main.route('/get_data', methods=['GET'])
@cross_origin()
def get_dataframes():
    df = pg_2_Db_to_Df()
    table = df.to_json(orient='records')
    return jsonify({"data": json.loads(table)})

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
    grouped_df = grouped_df.drop(columns=['rs_id', 'qry_id', 'Batch Id'], errors='ignore')
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

    max_suite_id = db.session.query(db.func.max(MdSuite.suite_id)).scalar()
    new_suite_id = max_suite_id + 1 if max_suite_id else 1

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
        suites = MdSuite.query.all()
        suite_list = [{
            'suite_id': suite.suite_id,
            'suite_name': suite.suite_name,
            'suite_description': suite.suite_description,
            'suite_created_by': suite.suite_created_by,
            "suite_priority": suite.suite_priority,
            'suite_created_dt': suite.suite_created_dt,
            'suite_modified_dt': suite.suite_modified_dt
        } for suite in suites]
        suite_list.sort(key=lambda x: x['suite_id'], reverse=True)
        return jsonify({"data": suite_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/table3', methods=['GET'])
@cross_origin()
def table3():
    last_batch_id = db.session.query(func.max(QueryExecnBatch.batch_id)).scalar()
    result_sets = db.session.query(MdResultSet, MdSqlqry, MdSuite, QueryExecnBatch) \
        .join(MdSqlqry, MdResultSet.qry_id == MdSqlqry.qry_id) \
        .join(MdSuite, MdSqlqry.suite_id == MdSuite.suite_id) \
        .join(QueryExecnBatch, MdResultSet.rs_batch_id == QueryExecnBatch.batch_id) \
        .filter(QueryExecnBatch.batch_id == last_batch_id) \
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
    grouped_df = grouped_df.drop(columns=['Batch Id'], errors='ignore')
    grouped_df = grouped_df.iloc[::-1]
    table = grouped_df.to_json(orient="records")
    return jsonify({"data": table})


@main.route('/table4', methods=['GET'])
@cross_origin()
def table4():
    last_batch_id = db.session.query(func.max(QueryExecnBatch.batch_id)).scalar()
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
        .filter(QueryExecnBatch.batch_id == last_batch_id) \
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
