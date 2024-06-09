# CirrusInsightsNowAIBE Python 3.12/
These are the steps to follow to run the CirrusInsights-BE in your local system.

1) Clone this repository: https://github.com/CirrusLabs-NPD/CirrusInsightsBE

2) Install Pyhton and Pip in your System and Dbvever(Recomended) or any other postgresql supported applications.

3) Install Flask in your system : pip install flask

4) Run this code for installing all the requirements : pip install -r .\requirements.txt

5) Create one new file named .env and paste this line DATABASE_URL = postgresql://cirrusinsightsnow_user:uJLD1ua3sX3pn0KELr7htDLMsIBl01Zq@dpg-ck5ul5tdrqvc73eoa8s0-a.oregon-postgres.render.com/cirrusinsightsnow

6) Open terminal and create a virtual environment : python -m venv myapp

7) Run this line to activate the virtual environment: myapp\Scripts\activate

8) Run this line to run the code in local : flask run

9) Run this line to open the flask shell : flask shell

10) To create the database in your local system run this line : db.create_all()

# To run the db in Dbvever or in other application, add these following to connect the db.

Host : dpg-ck5ul5tdrqvc73eoa8s0-a.oregon-postgres.render.com
Database : cirrusinsightsnow
UserName : cirrusinsightsnow_user
Password : uJLD1ua3sX3pn0KELr7htDLMsIBl01Zq
