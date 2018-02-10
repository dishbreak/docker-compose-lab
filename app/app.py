from bottle import Bottle, request
import json

cache = {}

app = Bottle()


@app.get("/")
def say_hello():
    return json.dumps({"message": "oh hai dere"})


@app.get("/value")
def get_value():
    return json.dumps({"value": str(cache.get('value'))})


@app.post("/value")
def set_value():
    cache['value'] = str(request.json['value'])


if __name__ == '__main__':
    app.run(host="0.0.0.0")
