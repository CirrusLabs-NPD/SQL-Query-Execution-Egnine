# SQL-Query-Execution-Egnine
Test sample SQL Queries against higher level environments and stores whether the queries passed or not as well as the output. 

## installation instructions: 
cd into the project directory, 
create two terminals (one for frontend and one for backend) 

### Backend server

''' 
cd Backend 
#(do not create venv it is already created) 
myapp\Scripts\activate #(to start the venv on windows for Mac: source myapp/bin/activate) 
pip install requirements.txt
flask run
'''


### Frontend side 

''' cd sql-engine-test
npm install 
npm start
'''


### notes 

- do no recreate the venv (breaks snowflake) 
- might need to use -force or --legacy-peer-deps for react app becuase material-ui conflicts with some other things

## API documentaion: 

### Page 1: 
- /upload (POST): takes an excel file stores it in uploads folder and pushes to db, sends back: "message" (success message) and "data" (sample of the inserted excel file)
  - note: please refer to the sample excel file for the column names/fields, they are case sensitive including the suite names

### Page 2: 
- /get_data (GET): returns a table with all the queries that have been stored
  - note: need to either optimise or add loading for this part since data take some time to query
- /submit_selection (POST): takes a json in with the associated columns for whatever has been executed and returns a message either succesful or failed 
  - note: use console to see structure of returned json if changing code in the future
  - it also executes against both dbs (snowflake and postgres)
  - subject to optimisation
  - change route in submethod Sf_qry to return the result in other cases as connector or programming error,
  - change route in pass fail to also return actual result (might be easier to make another method one which just return the resuls and another that does pass fail) 

### Page 3: 
- /table1 (GET): returns a json with summary table
- /table1 (GET): returns a json with the details of the last batch
  - edit it to include going in between older pages

### Additional notes: 
- create method to query username
- change credentials for snowflake (it expires in ~25 days)
- credentials for postgres in the __init.py__
- Do NOT RUN FLASK SHELL


## Frontend Documentation: 

### Page 1: 
- located under sql-engine-test/src/components/Cards/FileUpload.js
- need to add toast message for number of rows added/modified

### Page 2: 
- located under sql-engine-test/src/components/Cards/QueryAns.js
- need to add loading or oprimisation for query
- refer to console for the json
- ignore the error which pop-ups it is an error message added by mistake can't get rid of it, (you can understand it ran by the fact you can see the json in the console)

### Page 3: 
- located under sql-engine-test/src/components/Cards/EpicGeneration.js

### Header/Navebar: 
- located in app.js
  - change username to query from backend after creating an API call
  - remove test from the username option
- has naigation for all the pages





