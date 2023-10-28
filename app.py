# main page, routes on main.py


from flask import Flask
from flask_cors import CORS
from main import main

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}) # asssuming react server is running here
app.register_blueprint(main, url_prefix="/")

if __name__ == "__main__":
    app.run(debug=True)