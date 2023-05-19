from flask import Flask
from flask import request, jsonify
import urllib.request, json
from werkzeug.exceptions import HTTPException
from pybreaker import CircuitBreaker

app = Flask(__name__)

counter: int = 0
t: int = 5

breaker = CircuitBreaker(fail_max=10, reset_timeout=3)

# Do not remove this method.
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

@app.route('/igv')
def igv():
    try:
        tax = breaker.call(get_tax_from_api)
        return jsonify(igv=tax), 200
    except Exception as e:
        raise Exception('too many fails')

@breaker
def get_tax_from_api():
    url = "http://127.0.0.1:5000/tax"

    response = urllib.request.urlopen(url)
    data = response.read()
    data_dict = json.loads(data)

    return int(data_dict["Tax"])

if __name__ == "__main__":
    app.run(debug=True, port=3000)
