from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_question', methods=['POST'])
def get_question():
    data = request.json
    category = data['category']
    difficulty = data['difficulty']
    parameters = {
        "amount": 1,
        "category": category,
        "difficulty": difficulty,
        "type": "multiple"
    }
    response = requests.get(url="https://opentdb.com/api.php", params=parameters)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
