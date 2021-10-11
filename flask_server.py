from flask import Flask, json, request
from flask_cors import CORS, cross_origin
from flask import send_file
import main

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#CORS(app, max_age=3600, resources={r"*": {"origins": ["*","https://ban-sc.idc.tarento.com"]}})

subtitle_dir = "/home/ec2-user/vakyansh-client-realtime-v2/vakyansh-client-code/subtitles/"
speaker_diarization_dir = "/home/ec2-user/vakyansh-client-realtime-v2/vakyansh-client-code/speaker_diarization/"


@app.route('/gen_srt_from_youtube_url',methods=['POST'])
@cross_origin()
def gen_srt_from_youtube_url():
    body = request.get_json()
    input = body["url"]
    language = body["language"]
    result = main.flaskresponse(input,language,input_format='url',output_format='srt')
    if(result):
        tmp = json.dumps(result)
        #tmp.headers.add('Access-Control-Allow-Origin', 'https://ban-sc.idc.tarento.com')
        return tmp
    else:
        return json.dumps({'gen_srt_from_youtube_url':'false'})

@app.route('/gen_srt_from_file',methods=['POST'])
@cross_origin()
def gen_srt_from_file():
    body = request.get_json()
    input = body["file"]
    language = body["language"]
    result = main.flaskresponse(input,language,input_format='file',output_format='srt')
    if(result):
        tmp = json.dumps(result)
        #tmp.headers.add('Access-Control-Allow-Origin', 'https://ban-sc.idc.tarento.com')
        return tmp
    else:
        return json.dumps({'gen_srt_from_file':'false'})

@app.route('/gen_speaker_diarization_from_file',methods=['POST'])
@cross_origin()
def gen_speaker_diarization_from_file():
    body = request.get_json()
    input = body["file"]
    language = body["language"]
    result = main.flaskresponse(input,language,input_format='file',output_format='diarization')
    if(result):
        tmp = json.dumps(result)
        #tmp.headers.add('Access-Control-Allow-Origin', 'https://ban-sc.idc.tarento.com')
        return tmp
    else:
        return json.dumps({'gen_speaker_diarization_from_file':'false'})

@app.route('/get_srt/<filename>',methods=['GET'])
@cross_origin()
def get_srt(filename):
    try:
        return send_file(subtitle_dir+str(filename), as_attachment=True)
    except:
        return json.dumps({'get_srt':'false'})

@app.route('/get_speaker_diarization/<filename>',methods=['GET'])
@cross_origin()
def get_speaker_diarization(filename):
    try:
        return send_file(speaker_diarization_dir+str(filename), as_attachment=True)
    except:
        return json.dumps({'get_srt':'false'})

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port=5001, debug=True)
