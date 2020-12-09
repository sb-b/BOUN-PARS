# coding=utf-8
from flask import Flask, json, g, request, jsonify
import evaluate

app = Flask(__name__)

@app.route("/evaluate", methods=["POST"])
def parse_post():
    json_data = json.loads(request.data)
    input_text = json_data["query"]
    result = evaluate.parse_plaintext(input_text)
    return jsonify(result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, processes=1, use_reloader=False)
