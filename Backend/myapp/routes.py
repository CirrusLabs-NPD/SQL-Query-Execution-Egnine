# from flask import Flask, Blueprint, jsonify, redirect, url_for ,request ,make_response ,redirect_template , session
from flask import Flask, Blueprint, jsonify, redirect, url_for, request, make_response, session

from datetime import datetime , timedelta

import jwt

from functools import wraps

from myapp.auth import create_token, decode_token

from .extensions import db

from .models import MdDatabase, MdDbConfig ,MdPrivs ,MdResultSet ,MdRole ,MdSqlqry ,MdSuite ,MdTempResultSet ,Users, QueryExecnBatch

import requests

from flask_bcrypt import Bcrypt  

from flask_cors import CORS , cross_origin  # Import CORS

from sqlalchemy.orm.exc import NoResultFound

import json
# import app

from flask_jwt_extended import create_access_token, jwt_required ,get_jwt_identity

import os

main = Blueprint('main', __name__)
bcrypt = Bcrypt()

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

allowed_origins = [
    "http://localhost:3000",  # Replace with the actual domains you want to allow
    "https://cirrusinsight-ai.onrender.com",
]

CORS(app, origins=allowed_origins, methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Authorization"], supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
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

# Your authentication decorator
# def token_required(func):
#     @wraps(func)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         if not token:
#             return jsonify({'message': 'Token is missing'}), 401
#         token = token.split(" ")[1]
#         payload = decode_token(token)
#         if not payload:
#             return jsonify({'message': 'Token is invalid or expired'}), 401
#         return func(payload, *args, **kwargs)
#     return decorated

# @main.route('/loginRegister', methods=['POST'])
# @cross_origin()
# def login():
#     data = request.json  # Assuming the request data is sent as JSON
#     username = data.get('username')
#     user = User.query.filter_by(username=username).first()

#     if not user:
#         # If the user does not exist, you can create a new user here
#         new_user = User(username=username)
#         db.session.add(new_user)
#         db.session.commit()

#         # Generate an access token for the new user
#         access_token = create_access_token(identity=str(new_user.id), expires_delta=timedelta(days=120))
#         success_message = 'User created successfully.'
#     else:
#         # If the user exists, generate an access token for the existing user
#         access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=120))
#         success_message = 'Login successful.'

#     # Return the access token as a JSON response
#     return jsonify({'access_token': access_token, 'message': success_message}), 200


# @main.route('/protected_resource', methods=['GET'])
# def protected_resource():
#     # Get the JWT token from the request or from the user's session (if applicable)
#     jwt_token = get_jwt_token()
#     # Define the API URL you want to access
#     api_url = "https://cirrusinsightsbe.onrender.com/protected_resource"
#     # Create headers with the Authorization header containing the JWT token
#     headers = {
#         "Authorization": f"Bearer {jwt_token}",
#         "Content-Type": "application/json",
#     }

#     # Make the authenticated HTTP request
#     response = requests.get(api_url, headers=headers)
#     # Handle the response and return a JSON response to the client
#     if response.status_code == 200:
#         return jsonify({'message': 'Success'})
#     elif response.status_code == 401:
#         return jsonify({'message': 'Authentication failed'}), 401
#     else:
#         return jsonify({'message': 'Request failed'}), 500


# def get_jwt_token():
#     # Implement logic to retrieve the JWT token from the user's session or request
#     # This can vary depending on your application's authentication mechanism
#     return create_token  # Replace with the actual JWT token


# @main.route('/protected_route')
# @token_required
# def protected_route(current_user):
#     # The current_user parameter will receive the payload from the JWT token
#     return jsonify({'message': f'Hello, user {current_user["user_id"]}'})

# @main.route('/protected')
# def protected():
#     token = request.headers.get('Authorization')
#     if not token:
#         return 'Token missing', 401
#     token = token.split(" ")[1]
#     payload = decode_token(token)
#     if not payload:
#         return 'Invalid or expired token', 401
    

# @main.route('/')
# def index():
#     users = User.query.all()
#     users_list_html = [f"<li>{ user.username }</li>" for user in users]
#     return f"<ul>{''.join(users_list_html)}</ul>"


# @main.route('/add/<username>')
# def add_user(username):
#     db.session.add(User(username=username))
#     db.session.commit()
#     return redirect(url_for("main.index"))

# @main.route('/categories', methods=['GET'])
# @jwt_required()
# @cross_origin()
# def get_categories():
#     try:
#         current_user_id = get_jwt_identity()
#         print(current_user_id)
#         categories = Category.query.all()

#         category_list = []
#         for category in categories:
#             # Use a filter condition to fetch questions related to the current category
#             questions = Question.query.filter_by(category_id=category.id).all()

#             category_data = {
#                 "id": category.id,
#                 "position": category.position,
#                 "name": category.name,
#                 "questions": []
#             }

#             for question in questions:
#                 # Use a filter condition to fetch answers related to the current question
#                 answers = Answer.query.filter_by(question_id=question.id, user_id=current_user_id).all()

#                 question_data = {
#                     "id": question.id,
#                     "text": question.question,
#                     "answer": " ".join([answer.answer for answer in answers])
#                 }
#                 category_data["questions"].append(question_data)

#             # Fetch the solution data based on the current category and user_id
#             solutions = Solution.query.filter_by(category_id=category.id, user_id=current_user_id).all()
#             category_data["solution"] = [{"id": solution.id, "solution": solution.solution} for solution in solutions]
            
#             category_list.append(category_data)

#         return jsonify({"categories": category_list})
    
#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token has expired'}, 401)
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}, 401)

# @main.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     username = data.get('username')
#     plaintext_password = data.get('password')
#     existing_user = User.query.filter_by(username=username).first()
#     if existing_user:
#         return jsonify({'message': 'Username already exists'}), 400
#     hashed_password = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')
#     new_user = User(username=username, password=hashed_password)
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({'message': 'User registered successfully'}), 201  # Return 201 Created status code In this code

# @main.route('/questions/<int:question_id>/answer', methods=['POST'])
# @jwt_required()
# @cross_origin()
# def create_or_update_answer(question_id):
#     try:
#         # Get the request JSON data
#         current_user_id = get_jwt_identity()
#         data = request.json
#         # print(question_id,data)
#         # Check if the question with the specified ID exists
        
#         question = Question.query.filter_by(id=question_id).first()
#         # print(question)
    
#         if not question:
#             return jsonify({"error": "Question not found"}), 404
#         # Check if an answer for this question already exists

#         answer = Answer.query.filter_by(question_id=question_id, user_id=current_user_id).first()
#         print(answer,"answer")


#         if answer:
#             # Update the existing answer
#             answer.answer = data.get('answer', '')
#         else:
#             # Create a new answer
#             print(current_user_id,"hello")
#             answer = Answer(question_id=question_id, user_id=current_user_id ,answer=data.get('answer', ''))
#             db.session.add(answer)
#         # Commit changes to the database
#         db.session.commit()
#         # Return the response
#         return jsonify({"id": answer.id, "answer": answer.answer}), 200

#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token has expired'}, 401)
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}, 401)

# @main.route('/categories/<int:category_id>/solution', methods=['POST'])
# @jwt_required()
# @cross_origin()
# def create_or_update_solution(category_id):
#     try:
#         # Get the request JSON data
#         current_user_id = get_jwt_identity()
#         data = request.json

#         # Check if the category with the specified ID exists
#         category = Category.query.get(category_id)
#         print(category)
#         if not category:
#             return jsonify({"error": "Category not found"}), 404
#         # Check if a solution for this category already exists
#         solution = Solution.query.filter_by(category_id=category_id, user_id=current_user_id).first()
#         if solution:
#             # Update the existing solution
#             solution.solution = data.get('solution', '')
#         else:
#             # Create a new solution
#             solution = Solution(category_id=category_id, user_id=current_user_id , solution=data.get('solution', ''))
#             db.session.add(solution)
#         # Commit changes to the database
#         db.session.commit()
#         # Return the response
#         return jsonify({"id": solution.id, "solution": solution.solution}), 200
    
#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token has expired'}, 401)
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}, 401)

# @main.route('/end_session', methods=['POST'])
# @jwt_required()
# @cross_origin()
# def end_session():
#     try:
#         current_user_id = get_jwt_identity()
#         try:
#             user_id = current_user_id  # Replace with the actual user ID
#             # Get all answers and solutions related to the user
#             answers = Answer.query.filter_by(user_id=user_id).all()
#             solutions = Solution.query.filter_by(user_id=user_id).all()
            
#             # Create a dictionary to store history data by category
#             history_data_by_category = []

#             # Query the database to get the category ID based on some criteria
#             category_id = get_category_id(current_user_id)

#             # Retrieve all categories from the database
#             categories = Category.query.all()

#             # Iterate through categories and store answers and solutions by category
#             for category in categories:
#                 # Filter answers and solutions by category (replace with your actual filtering logic)
#                 category_answers = [answer.serialize() for answer in answers if Question.query.get(answer.question_id).category_id == category.id]
#                 category_solutions = [solution.serialize() for solution in solutions if solution.category_id == category.id]

#                 if category_answers or category_solutions:
#                     category = Category.query.get(category_id)
#                     # Create the category entry in history_data_by_category
#                     category_entry = {
#                         "answer": category_answers,
#                         "solutions": category_solutions
#                     }
#                     history_data_by_category.append(category_entry)
    
#             # Insert history data as JSON into the History table
#             history_entry = History(
#                 user_id=user_id,
#                 category_id=category_id,  # Replace with the actual category ID if needed
#                 history=json.dumps(history_data_by_category)  # Serialize the dictionary to JSON
#             )
#             db.session.add(history_entry)
#             db.session.commit()

#             answers_to_delete = Answer.query.filter_by(user_id=user_id).all()
#             for answer in answers_to_delete:
#                 db.session.delete(answer)

#             solution_to_delete = Solution.query.filter_by(user_id=user_id).all()
#             for solution in solution_to_delete:
#                 db.session.delete(solution)

#             db.session.commit()
#             response_data = {
#                 'message': 'Session ended successfully',
#                 'history_by_category': history_data_by_category
#             }

#             return jsonify(response_data), 200
#         except NoResultFound:
#             return jsonify({'error': 'No data found for the user'}), 404
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500
        
#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token has expired'}, 401)
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}, 401)

# # Your Category model definition remains unchanged in your 'models.py' file
# # Be sure to import the Category model where needed in your code

# def get_category_id(user_id):
#     last_solution = Solution.query.filter_by(user_id=user_id).order_by(Solution.id.desc()).first()
#     print(last_solution)
#     print(last_solution.category_id)
#     if last_solution:
#         return last_solution.category_id
#     else:
#         return None
    
# @main.route('/delete_data', methods=['DELETE'])
# @jwt_required()
# @cross_origin()
# def delete_data():
#     try:
#         current_user_id = get_jwt_identity()
#         # Delete answers for the specified user ID
#         Answer.query.filter_by(user_id=current_user_id).delete()
#         # Delete solutions for the specified user ID
#         Solution.query.filter_by(user_id=current_user_id).delete()
#         # Commit changes to the database
#         db.session.commit()
#         return jsonify({'message': 'Data deleted successfully'}), 200
    
#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token has expired'}, 401)
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}, 401)


# @main.route('/history', methods=['GET'])
# @jwt_required()
# @cross_origin()
# def get_history():
#     try:

#         current_user_id = get_jwt_identity()
#         try:
#             # Fetch history items for the current user with associated user and category details
#             history_items = History.query.filter_by(user_id=current_user_id).all()

#             # Create a list to store history data with category, user, and content
#             history_data = []

#             for history_item in history_items:
#                 category = Category.query.get(history_item.category_id)
#                 user = User.query.get(history_item.user_id)

#                 history_data.append({
#                     "id": history_item.id,
#                     "content": history_item.history,
#                     "time": history_item.updated_at,
#                     "category": {
#                         "id": category.id,
#                         "name": category.name,  # Adjust this based on your Category model
#                         # Add other category details as needed
#                     },
#                     "user": {
#                         "id": user.id,
#                         "name": user.username,  # Adjust this based on your User model
#                         # Add other user details as needed
#                     }
#                 })

#             if not history_data:
#                 return jsonify({'message': 'No history data found for the current user'}), 404


#             response_data = {
#                 "history": history_data
#             }

#             return jsonify(response_data), 200
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500

#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token has expired'}, 401)
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}, 401)