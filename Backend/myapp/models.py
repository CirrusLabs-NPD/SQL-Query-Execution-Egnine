from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class MdDatabase(Base):
    __tablename__ = 'md_database'
    db_id = Column(Integer, primary_key=True)
    db_name = Column(String(255))
    on_cloud_flg = Column(String(255))
    created_at = Column(DateTime)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    role = Column(String(255))
    created_dt = Column(DateTime)
    modified_dt = Column(DateTime)

class MdDbConfig(Base):
    __tablename__ = 'md_db_config'
    db_id = Column(Integer, primary_key=True)
    db_url1 = Column(String(255))
    db_url2 = Column(String(255))
    db_url3 = Column(String(255))
    db_user_id = Column(Integer, ForeignKey('users.id'))
    db_password = Column(String(255))
    created_dt = Column(DateTime)
    modified_dt = Column(DateTime)

    user = relationship('User')

class MdRole(Base):
    __tablename__ = 'md_role'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(255))
    role_group = Column(String(255))
    role_created_dt = Column(DateTime)
    role_modified_dt = Column(DateTime)

class MdPrivs(Base):
    __tablename__ = 'md_privs'
    priv_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('md_role.role_id'))
    privilege_name = Column(String(255))
    created_dt = Column(DateTime)
    modified_dt = Column(DateTime)

    role = relationship('MdRole')

class MdSuite(Base):
    __tablename__ = 'md_suite'
    suite_id = Column(Integer, primary_key=True)
    suite_name = Column(String(255))
    suite_priority = Column(Integer)
    suite_created_dt = Column(DateTime)
    suite_modified_dt = Column(DateTime)

class MdSqlqry(Base):
    __tablename__ = 'md_sqlqry'
    qry_id = Column(Integer, primary_key=True)
    qry_name = Column(String(255))
    sql_qry_1 = Column(String(255))
    sql_qry_2 = Column(String(255))
    suite_id = Column(Integer, ForeignKey('md_suite.suite_id'))
    created_dt = Column(DateTime)
    modified_dt = Column(DateTime)

    suite = relationship('MdSuite')

class QueryExecnBatch(Base):
    __tablename__ = 'query_execn_batch'
    batch_id = Column(Integer, primary_key=True)
    batch_dt = Column(DateTime)
    batch_start_dt = Column(DateTime)
    batch_end_dt = Column(DateTime)
    batch_status = Column(String(255))

class MdTempResultSet(Base):
    __tablename__ = 'md_temp_result_set'
    rs_batch_id = Column(Integer, ForeignKey('query_execn_batch.batch_id'), primary_key=True)
    qry_id = Column(Integer, ForeignKey('md_sqlqry.qry_id'), primary_key=True)
    sql_qry_1_result = Column(String(255))
    sql_qry_2_result = Column(String(255))

class MdResultSet(Base):
    __tablename__ = 'md_result_set'
    rs_batch_id = Column(Integer, ForeignKey('query_execn_batch.batch_id'), primary_key=True)
    qry_id = Column(Integer, ForeignKey('md_temp_result_set.qry_id'), primary_key=True)
    sql_qry_1_result = Column(String(255))
    sql_qry_2_result = Column(String(255))
    qrn_execn_flg = Column(Integer)
    qrn_execn_status = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(['rs_batch_id', 'qry_id'], ['md_temp_result_set.rs_batch_id', 'md_temp_result_set.qry_id']),
    )


