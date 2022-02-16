from flask import Flask, json, request
from flask_cors import CORS, cross_origin
from flask import send_file
from werkzeug.utils import secure_filename
import os
import main
import config
import glob
import uuid
import base64
import pysrt
from utilities import media_conversion
import shutil
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#CORS(app, max_age=3600, resources={r"*": {"origins": ["*","https://ban-sc.idc.tarento.com"]}})

subtitle_dir = config.SUBTITLE_DIR
speaker_diarization_dir = config.SPEAKER_DIARIZATION_DIR

app.config['UPLOAD_PATH'] = config.UPLOAD_DIR
if not os.path.isdir(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

def get_transcription_from_srt_text(srt_text):
    with open('temp.srt', 'w') as f:
            f.write(srt_text)
    subs = pysrt.open('temp.srt')
    transcription = ''
    for sub in subs:
        text = sub.text
        if text != '[ Voice is not clearly audible ]':
            transcription = transcription + ' ' + text

    return transcription

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
    input_ =body["file_name"]
    input='uploads/'+input_
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
    input_ = body["file_name"]
    input='uploads/'+input_
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
        return json.dumps({'get_speaker_diarization':'false'})

@app.route('/upload',methods=['POST'])
@cross_origin()
def upload():
    try:
        if not os.path.isdir(app.config['UPLOAD_PATH']):
            os.mkdir(app.config['UPLOAD_PATH'])
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return_path = str(os.path.join(app.config['UPLOAD_PATH'], filename))
        file_unique=str(uuid.uuid1())+'.wav'
        new_path = str(os.path.join(app.config['UPLOAD_PATH'],file_unique))
        os.rename(return_path, new_path)
        return json.dumps({'uploaded_file , please make sure copy this file name  for further operations ': file_unique })

    except:
        return json.dumps({'upload':'false'})

@app.route('/get_transcription',methods=['POST'])
@cross_origin()
def get_transcription():
    try:
        start_time=datetime.now()
        body = request.get_json()
        language = body["source"]
        base64_string = body["audioContent"]

        uniqueID=str(uuid.uuid1())
        temp_wav=uniqueID+'.wav'

        if not os.path.exists(uniqueID):
            os.makedirs(uniqueID)
        
        decoded_string = base64.b64decode(base64_string)
        wav_file = open(temp_wav, "wb")
        wav_file.write(decoded_string)

        input = os.path.join(uniqueID,'input_audio.wav')
        try:
            os.remove(input)
        except OSError:
            pass
        media_conversion(temp_wav,uniqueID)
        
        result = main.flaskresponse(input,language,input_format='file',output_format='srt')
        shutil.rmtree(uniqueID)
        os.remove(temp_wav)
        transcription_result=get_transcription_from_srt_text(result["srt"])
        total_time=datetime.now()-start_time
        return json.dumps({"transcript":transcription_result,"prediction_time" :str(total_time)})


    except FileNotFoundError:
        print("Error: input base64 string is not available")
        return json.dumps({'response':'failed'})
    except:
        return json.dumps({'response':'failed'})


if __name__ == '__main__':
    app.run(host = config.HOST_IP, port=config.HOST_PORT, debug=True)
