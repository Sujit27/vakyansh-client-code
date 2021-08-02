from flask import Flask, json, request
from flask_cors import CORS
import main

app = Flask(__name__)
CORS(app)



@app.route('/generate_srt',methods=['POST'])
def generate_srt():
    body = request.get_json()
    url = body["url"]
    result = main.flaskresponse(url)
    if(result):
        return json.dumps(result)
    else:
        return json.dumps({'generate_srt':'false'})

if __name__ == '__main__':
    app.run(debug=True)