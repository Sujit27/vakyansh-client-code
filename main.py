import grpc
from stub.speech_recognition_open_api_pb2_grpc import SpeechRecognizerStub
from stub.speech_recognition_open_api_pb2 import Language, RecognitionConfig, RecognitionAudio, \
    SpeechRecognitionRequest
from grpc_interceptor import ClientCallDetails, ClientInterceptor
import os
import shutil
import subprocess
import generate_chunks
from utilities import *
import config
from argparse import ArgumentParser


class GrpcAuth(grpc.AuthMetadataPlugin):
    def __init__(self, key):
        self._key = key

    def __call__(self, context, callback):
        callback((('rpc-auth-header', self._key),), None)


class MetadataClientInterceptor(ClientInterceptor):

    def __init__(self, key):
        self._key = key

    def intercept(
            self,
            method,
            request_or_iterator,
            call_details: grpc.ClientCallDetails,
    ):
        new_details = ClientCallDetails(
            call_details.method,
            call_details.timeout,
            [("authorization", "Bearer " + self._key)],
            call_details.credentials,
            call_details.wait_for_ready,
            call_details.compression,
        )

        return method(request_or_iterator, new_details)


def get_text_from_wavfile_any_length(stub,audio_file,lang, translation):
    '''
    Given an audio file, segments it and transcribes each segment
    '''

    output_file_path,start_time_stamp,end_time_stamp = generate_chunks.split_and_store(audio_file)
    result = ''
    token = get_auth_token()
    model_id = get_model_id(token, lang, "en")
    for j in range(len(start_time_stamp)):
        single_chunk=os.path.join(output_file_path ,f'chunk{j}.wav')
        audio_bytes = read_given_audio(single_chunk)
        lang1 = Language(value=lang, name=config.language_code_dict[lang])
        recog_config = RecognitionConfig(language=lang1, audioFormat='MP3', transcriptionFormat='TRANSCRIPT',
                                enableAutomaticPunctuation=1)
        audio = RecognitionAudio(audioContent=audio_bytes)
        request = SpeechRecognitionRequest(audio=audio, config=recog_config)

        # creds = grpc.metadata_call_credentials(
        #     metadata_plugin=GrpcAuth('access_key')
        # )
        try:
            response = stub.recognize(request)
            print(j+1)
            result+=(str(j+1))
            result+='\n'
            print(convert(start_time_stamp[j]),end=' --> ')
            result+=convert(start_time_stamp[j])
            result+=' --> '
            print(convert(end_time_stamp[j] ))
            result+=convert(end_time_stamp[j])
            result+='\n'
            print(response.transcript)
            if(translation == True):
                translated_result = get_translation(token, model_id, lang,"en",response.transcript)
                print(translated_result)
                result+=translated_result
            else:
                result+=response.transcript
            print()
            result+='\n\n'

        except grpc.RpcError as e:
            e.details()
            status_code = e.code()
            print(status_code.name)
            print(status_code.value)
    
    with open("subtitle.srt", "w") as text_file:
        text_file.write(result)


def gen_srt_limited_duration(stub,audio_file,language,output_file_path):
    '''
    Given an audio file, generates srt for the first 5 min
    '''
    audio_bytes = read_given_audio(audio_file)
    lang = Language(value=language, name=config.language_code_dict[language])
    recog_config = RecognitionConfig(language=lang, audioFormat='WAV', transcriptionFormat='SRT',
                               enableInverseTextNormalization=False)
    audio = RecognitionAudio(audioContent=audio_bytes)
    request = SpeechRecognitionRequest(audio=audio, config=recog_config)
    response = stub.recognize(request)

    with open(output_file_path, "w") as text_file:
        text_file.write(response.srt)

def gen_srt_full(stub,audio_file,language, translate_to_en):
    '''
    Given an audio file, generates srt 
    '''
    output_dir = 'chunks'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    # chunk audio to 5min chunks
    chunk_files = chunk_audio(audio_file,output_dir)
    output_files = []
    for index,chunk in enumerate(chunk_files):
        output_file_path = os.path.join(output_dir,"subtitle{0}.srt".format(index))
        print("Generating subtitle output for chunk {}".format(index))
        gen_srt_limited_duration(stub,chunk,language, output_file_path)
        output_files.append(output_file_path)
    
    final_srt_file = merge_srt_files(output_files)
    if translate_to_en:
        print("Translating subtitles to english")
        translate_srt_file(final_srt_file,language)
    # shutil.rmtree(output_dir)

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("--url",help="youtub video  url",type=str,required=True)
    parser.add_argument("--lang_code",help="language of video",type=str,required=True,)
    parser.add_argument("--trans_eng",help=" eng Translate ",type=str,)
    args = parser.parse_args()

    translate_to_en=False
    try:
        trans_eng=(args.trans_eng).lower()
        if (trans_eng)=='true' or  (trans_eng)=='yes':
            translate_to_en=True
    except:
        pass

    url = args.url 
    subprocess.call(['youtube-dl {}'.format(url)], shell=True)
    audio_file = download_youtubeaudio(url)

    key = "mysecrettoken"
    interceptors = [MetadataClientInterceptor(key)]
    with grpc.insecure_channel('52.12.126.83:50051') as channel:
        channel = grpc.intercept_channel(channel, *interceptors)
        stub = SpeechRecognizerStub(channel)
        # get_text_from_wavfile_any_length(stub,audio_file,lang=args.lang_code, translation=translate_to_en)
        gen_srt_full(stub,audio_file,args.lang_code, translate_to_en)
