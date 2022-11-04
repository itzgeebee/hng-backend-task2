import json
from flask import Flask, g, jsonify, make_response
from flask_cors import CORS
from flask_expects_json import expects_json
from jsonschema import ValidationError
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
CORS(app)

schema = {
    'type': 'object',
    'properties': {
        "operation_type": {"type": "string",
                           "enum": ["addition",
                                    "subtraction",
                                    "multiplication",
                                    "division",
                                    "add",
                                    "divide",
                                    "multiply",
                                    "subtract", "-", "+", "*", "/"]},
        "x": {"type": "number"},
        "y": {"type": "number"}
    },
    'required': ["operation_type", "x", "y"]
}

@app.errorhandler(400)
def bad_request(error):
    if isinstance(error.description, ValidationError):
        original_error = error.description
        return make_response(jsonify({'success': False,
                                      'error': original_error.message}), 400)
    # handle other "Bad Request"-errors
    return jsonify({"success": False, "error": error.description,
                    "message": "bad request"}), 400


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


def response_format(operation_type: str, result: float) -> dict:
    return {"operation_type": operation_type, "result": result,
            "slackUsername": "itzgeebee"}

@app.route('/', methods=['POST'])
@expects_json(schema)
def do_math():
    data = g.data
    operation_type = data['operation_type']
    x = data['x']
    y = data['y']
    result = 0

    if operation_type == "addition" or operation_type == "add" or operation_type == "+":
        result = x + y
    elif operation_type == "subtraction" or operation_type == "subtract" or operation_type == "-":
        result = x - y
    elif operation_type == "multiplication" or operation_type == "multiply" or operation_type == "*":
        result = x * y
    elif operation_type == "division" or operation_type == "divide" or operation_type == "/":
        result = x / y

    return jsonify(response_format(operation_type, result))

if __name__ == '__main__':
    app.run(host='0.0.0.0')