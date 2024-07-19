CREATE TABLE "md_database" (
  "db_id" integer,
  "db_name" varchar(2),
  "on_cloud_flg" varchar(2),
  "created_at" timestamp
);

CREATE TABLE "users" (
  "id" integer PRIMARY KEY,
  "username" varchar,
  "role" varchar,
  "created_dt" timestamp,
  "modified_dt" timestamp
);

CREATE TABLE "md_db_config" (
  "db_id" integer,
  "db_url1" varchar(2),
  "db_url2" varchar(2),
  "db_url3" varchar(2),
  "db_user_id" integer,
  "db_password" varchar(2),
  "created_dt" timestamp,
  "modified_dt" timestamp
);

CREATE TABLE "md_role" (
  "role_id" integer,
  "role_name" varchar(2),
  "role_group" varchar(2),
  "role_created_dt" timestamp,
  "role_modified_dt" timestamp
);

CREATE TABLE "md_privs" (
  "priv_id" integer,
  "role_id" integer,
  "privileage_name" varchar(2),
  "created_dt" timestamp,
  "modified_dt" timestamp
);

CREATE TABLE "md_suite" (
  "suite_id" integer,
  "suite_name" varchar(2),
  "suite_priority" integer,
  "suite_created_dt" timestamp,
  "suite_modified_dt" timestamp
);

CREATE TABLE "md_sqlqry" (
  "qry_id" integer,
  "qry_name" varchar(2),
  "sql_qry_1" varchar(2),
  "sql_qry_2" varchar(2),
  "suite_id" integer,
  "created_dt" timestamp,
  "modified_dt" timestamp
);

CREATE TABLE "query_execn_batch" (
  "batch_id" integer,
  "batch_dt" timestamp,
  "batch_start_dt" timestamp,
  "batch_end_dt" timestamp,
  "batch_status" varchar(2)
);

CREATE TABLE "md_temp_result_set" (
  "rs_batch_id" integer,
  "qry_id" integer,
  "sql_qry_1_result" varchar(2),
  "sql_qry_2_result" varchar(2)
);

CREATE TABLE "md_result_set" (
  "rs_batch_id" integer,
  "qry_id" integer,
  "sql_qry_1_result" varchar(2),
  "sql_qry_2_result" varchar(2),
  "qrn_execn_flg" integer,
  "qrn_execn_status" integer
);
ALTER TABLE "md_database" ADD FOREIGN KEY ("db_id") REFERENCES "md_db_config" ("db_id");

ALTER TABLE "md_db_config" ADD FOREIGN KEY ("db_user_id") REFERENCES "users" ("id");

ALTER TABLE "md_privs" ADD FOREIGN KEY ("role_id") REFERENCES "md_role" ("role_id");

ALTER TABLE "md_sqlqry" ADD FOREIGN KEY ("suite_id") REFERENCES "md_suite" ("suite_id");

ALTER TABLE "md_temp_result_set" ADD FOREIGN KEY ("qry_id") REFERENCES "md_sqlqry" ("qry_id");

ALTER TABLE "md_temp_result_set" ADD FOREIGN KEY ("rs_batch_id") REFERENCES "query_execn_batch" ("batch_id");

ALTER TABLE "md_result_set" ADD FOREIGN KEY ("qry_id") REFERENCES "md_temp_result_set" ("qry_id");

ALTER TABLE "md_result_set" ADD FOREIGN KEY ("rs_batch_id") REFERENCES "query_execn_batch" ("batch_id");

ALTER TABLE "md_result_set" ADD FOREIGN KEY ("rs_batch_id") REFERENCES "md_temp_result_set" ("rs_batch_id");


