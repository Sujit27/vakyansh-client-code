from flask import Flask, json, request
from flask_cors import CORS
from flask import send_file
import main

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*","https://ban-sc.idc.tarento.com"]}})

@app.route('/generate_srt',methods=['POST'])
def generate_srt():
    body = request.get_json()
    url = body["url"]
    language = body["language"]
    result = main.flaskresponse(url,language)
    if(result):
        return json.dumps(result)
    else:
        return json.dumps({'generate_srt':'false'})

# @app.route('/get_srt',methods=['GET'])
# def download_srt():
#     body = request.get_json()
#     filename = body["filename"]
#     return send_file("/home/ec2-user/vakyansh-client-v2/vakyansh-client-code/subtitles/"+filename, as_attachment=True)

@app.route('/get_srt/<filename>',methods=['GET'])
def get_srt(filename):
    try:
        return send_file("/home/ec2-user/vakyansh-client-realtime-v2/vakyansh-client-code/subtitles/"+str(filename), as_attachment=True)
    except:
        return json.dumps({'get_srt':'false'})

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=5001, debug=True)
