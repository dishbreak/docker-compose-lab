from bottle import Bottle
import json

cache = {}

app = Bottle()


@app.get("/")
def say_hello():
    return json.dumps({"message": "oh hai dere"})


if __name__ == '__main__':
    app.run(host="0.0.0.0")
