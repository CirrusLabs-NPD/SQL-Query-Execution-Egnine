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
    #app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    #app.config['SECRET_KEY'] = "204475107210797805381198621683232319326"

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://queryexecutionuser:2VfcrHUJBtes2Jd7scvVvRMjaClQpbGL@dpg-cpgonqmct0pc739t0vtg-a.oregon-postgres.render.com/queryexecutiondb"

    jwt=JWTManager(app)
    db.init_app(app)

    #Added Debug and Exception
    app.debug = True
    @app.errorhandler(Exception)
    def handle_error(error):
        app.logger.error(f"An error occurred: {str(error)}")
        return jsonify({'message': 'An error occurred'}), 500

    app.register_blueprint(main)

    return app
