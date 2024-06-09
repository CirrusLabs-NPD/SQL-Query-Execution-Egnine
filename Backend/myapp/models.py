from .extensions import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
 
class MdDatabase(db.Model):
    __tablename__ = 'md_database'
    db_id = db.Column(db.Integer, primary_key=True)
    db_name = db.Column(db.String(2))
    on_cloud_flg = db.Column(db.String(2))
    created_at = db.Column(db.DateTime)
    config = db.relationship("MdDbConfig", back_populates="database", uselist=False)
 
class Users(db.Model):
    __tablename__ = 'md_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    role = db.Column(db.String)
    created_dt = db.Column(db.DateTime)
    modified_dt = db.Column(db.DateTime)
    db_configs = db.relationship("MdDbConfig", back_populates="user")
 
class MdDbConfig(db.Model):
    __tablename__ = 'md_db_config'
    db_id = db.Column(db.Integer, primary_key=True)
    db_url1 = db.Column(db.String(2))
    db_url2 = db.Column(db.String(2))
    db_url3 = db.Column(db.String(2))
    db_user_id = db.Column(db.Integer, db.ForeignKey('md_users.id'))
    db_password = db.Column(db.String(2))
    created_dt = db.Column(db.DateTime)
    modified_dt = db.Column(db.DateTime)
    user = db.relationship("Users", back_populates="db_configs")
    database = db.relationship("MdDatabase", back_populates="config")
 
class MdRole(db.Model):
    __tablename__ = 'md_role'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(2))
    role_group = db.Column(db.String(2))
    role_created_dt = db.Column(db.DateTime)
    role_modified_dt = db.Column(db.DateTime)
    privs = db.relationship("MdPrivs", back_populates="role")
 
class MdPrivs(db.Model):
    __tablename__ = 'md_privileages'
    priv_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('md_role.role_id'))
    privileage_name = db.Column(db.String(2))
    created_dt = db.Column(db.DateTime)
    modified_dt = db.Column(db.DateTime)
    role = db.relationship("MdRole", back_populates="privs")
 
class MdSuite(db.Model):
    __tablename__ = 'md_suite'
    suite_id = db.Column(db.Integer, primary_key=True)
    suite_name = db.Column(db.String(2))
    suite_priority = db.Column(db.Integer)
    suite_created_dt = db.Column(db.DateTime)
    suite_modified_dt = db.Column(db.DateTime)
    sqlqrys = db.relationship("MdSqlqry", back_populates="suite")
 
class MdSqlqry(db.Model):
    __tablename__ = 'md_sql_qry'
    qry_id = db.Column(db.Integer, primary_key=True)
    qry_name = db.Column(db.String(2))
    sql_qry_1 = db.Column(db.String(2))
    sql_qry_2 = db.Column(db.String(2))
    suite_id = db.Column(db.Integer, db.ForeignKey('md_suite.suite_id'))
    created_dt = db.Column(db.DateTime)
    modified_dt = db.Column(db.DateTime)
    suite = db.relationship("MdSuite", back_populates="sqlqrys")
 
class QueryExecnBatch(db.Model):
    __tablename__ = 'query_execn_batch'
    batch_id = db.Column(db.Integer, primary_key=True)
    batch_dt = db.Column(db.DateTime)
    batch_start_dt = db.Column(db.DateTime)
    batch_end_dt = db.Column(db.DateTime)
    batch_status = db.Column(db.String(2))
    temp_result_sets = db.relationship("MdTempResultSet", back_populates="batch")
    result_sets = db.relationship("MdResultSet", back_populates="batch")
 
class MdTempResultSet(db.Model):
    __tablename__ = 'md_temp_result_set'
    rs_batch_id = db.Column(db.Integer, db.ForeignKey('query_execn_batch.batch_id'), primary_key=True)
    qry_id = db.Column(db.Integer, db.ForeignKey('md_sql_qry.qry_id'), primary_key=True)
    sql_qry_1_result = db.Column(db.String(2))
    sql_qry_2_result = db.Column(db.String(2))
    batch = db.relationship("QueryExecnBatch", back_populates="temp_result_sets")
    sqlqry = db.relationship("MdSqlqry")
    result_set = db.relationship("MdResultSet", back_populates="temp_result_set")
 
class MdResultSet(db.Model):
    __tablename__ = 'md_result_set'
    rs_batch_id = db.Column(db.Integer, db.ForeignKey('query_execn_batch.batch_id'), primary_key=True)
    qry_id = db.Column(db.Integer, db.ForeignKey('md_temp_result_set.qry_id'), primary_key=True)
    sql_qry_1_result = db.Column(db.String(2))
    sql_qry_2_result = db.Column(db.String(2))
    qrn_execn_flg = db.Column(db.Integer)
    qrn_execn_status = db.Column(db.Integer)
    batch = db.relationship("QueryExecnBatch", back_populates="result_sets")
    temp_result_set = db.relationship("MdTempResultSet", back_populates="result_set")