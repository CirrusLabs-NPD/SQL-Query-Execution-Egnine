import os
from flask import Flask, request, jsonify
# import jwt
# import datetime
from .extensions import db
from .routes import main
from flask_jwt_extended import JWTManager
# init_db.py

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://queryexecutionuser:tLZ0t9c3IiEyu1PaezvuhoN1LtPO3ukp@dpg-cq5rgro8fa8c738cbsjg-a.oregon-postgres.render.com/queryexecutiondb_qc81"
    db.init_app(app)

    #Added Debug and Exception
    app.debug = True
    @app.errorhandler(Exception)
    def handle_error(error):
        app.logger.error(f"An error occurred: {str(error)}")
        return jsonify({'message': 'An error occurred'}), 500

    app.register_blueprint(main)

    return app
