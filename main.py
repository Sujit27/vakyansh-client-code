import grpc
from stub.speech_recognition_open_api_pb2_grpc import SpeechRecognizerStub
from stub.speech_recognition_open_api_pb2 import Language, RecognitionConfig, RecognitionAudio, \
    SpeechRecognitionRequest
import wave
from grpc_interceptor import ClientCallDetails, ClientInterceptor
import uuid
import pafy
import time
from pydub import AudioSegment
from pydub.silence import split_on_silence
import librosa
import os
import subprocess
import generate_chunks 


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


def read_audio():
    with wave.open('/home/sujit27/projects/ASR/vakyansh-client-code/sample_audios/bulletin_hi_truncated_1.wav', 'rb') as f:
        return f.readframes(f.getnframes())


def transcribe_audio_bytes(stub):
    language = "hi"
    audio_bytes = read_audio()
    lang = Language(value=language, name='Hindi')
    config = RecognitionConfig(language=lang, audioFormat='MP3', transcriptionFormat='TRANSCRIPT',
                               enableAutomaticPunctuation=1)
    audio = RecognitionAudio(audioContent=audio_bytes)
    request = SpeechRecognitionRequest(audio=audio, config=config)

    # creds = grpc.metadata_call_credentials(
    #     metadata_plugin=GrpcAuth('access_key')
    # )
    try:
        response = stub.recognize(request)

        print(response.transcript)
    except grpc.RpcError as e:
        e.details()
        status_code = e.code()
        print(status_code.name)
        print(status_code.value)


def transcribe_audio_url(stub):
    language = "hi"
    url = "https://codmento.com/ekstep/test/changed.wav"
    lang = Language(value=language, name='Hindi')
    config = RecognitionConfig(language=lang, audioFormat='WAV', enableAutomaticPunctuation=True)
    audio = RecognitionAudio(audioUri=url)
    request = SpeechRecognitionRequest(audio=audio, config=config)

    response = stub.recognize(request)

    print(response.transcript)


def get_srt_audio_bytes(stub):
    language = "hi"
    audio_bytes = read_audio()
    lang = Language(value=language, name='Hindi')
    config = RecognitionConfig(language=lang, audioFormat='WAV', transcriptionFormat='SRT',
                               enableInverseTextNormalization=False)
    audio = RecognitionAudio(audioContent=audio_bytes)
    request = SpeechRecognitionRequest(audio=audio, config=config)

    # creds = grpc.metadata_call_credentials(
    #     metadata_plugin=GrpcAuth('access_key')
    # )
    response = stub.recognize(request)

    print(response.srt)




def get_srt_audio_url(stub):
    language = "hi"
    url = "https://codmento.com/ekstep/test/changed.wav"
    lang = Language(value=language, name='Hindi')
    config = RecognitionConfig(language=lang, audioFormat='WAV', transcriptionFormat='SRT')
    audio = RecognitionAudio(audioUri=url)
    request = SpeechRecognitionRequest(audio=audio, config=config)

    response = stub.recognize(request)

    print(response.srt)




def read_given_audio(single_chunk):
    with wave.open(single_chunk, 'rb') as f:
        return f.readframes(f.getnframes())

def convert(seconds):
    try:
        milli=str(seconds).split('.')[-1][:2]
    except:
        milli='00'
    return time.strftime(f"%H:%M:%S,{milli}", time.gmtime(seconds))

def get_text_from_wavfile_any_length(stub,audio_file):

    #inputs 
    language = "hi"
    ###########
    output_file_path,start_time_stamp,end_time_stamp=generate_chunks.split_and_store(audio_file)

    for j in range(len(start_time_stamp)):
        single_chunk=os.path.join(output_file_path ,f'chunk{j}.wav')

        audio_bytes = read_given_audio(single_chunk)
        lang = Language(value=language, name='Hindi')
        config = RecognitionConfig(language=lang, audioFormat='MP3', transcriptionFormat='TRANSCRIPT',
                                enableAutomaticPunctuation=1)
        audio = RecognitionAudio(audioContent=audio_bytes)
        request = SpeechRecognitionRequest(audio=audio, config=config)

        # creds = grpc.metadata_call_credentials(
        #     metadata_plugin=GrpcAuth('access_key')
        # )
        try:
            response = stub.recognize(request)

            print(convert(start_time_stamp[j] ),end='  :  ')
            print(convert(end_time_stamp[j] ))

            print(response.transcript)

            print()
        except grpc.RpcError as e:
            e.details()
            status_code = e.code()
            print(status_code.name)
            print(status_code.value)



def download_youtubeaudio(url):
    '''
    Function to download the best available audio from given youtube url
    Accepts url as parameter and returns filename
    '''
    try:
        video = pafy.new(url) 
        bestaudio = video.getbestaudio()
        savedpath = bestaudio.filename
        filepath = "saved_audio" + os.path.splitext(savedpath)[-1]
        bestaudio.download(filepath=filepath)
        return filepath
    except:
        pass

def convert_to_wav(audio_file):
    try:
        if os.path.splitext(audio_file)[-1] == ".m4a":
            subprocess.call(["python","m4atowav.py"]) 
        elif os.path.splitext(audio_file)[-1] == ".mp3":
            sound = AudioSegment.from_mp3(audio_file)
            sound.export("saved_audio.wav", format="wav")
        else:
            sound = AudioSegment.from_file(audio_file)
            sound.export("saved_audio.wav",format="wav")
        os.remove(audio_file)
    except:
        pass

if __name__ == '__main__':
    url = "https://www.youtube.com/watch?v=UoFuE8IObKQ"
    audio_file = download_youtubeaudio(url)
    convert_to_wav(audio_file)
    
    audio_file='saved_audio.wav'

    key = "mysecrettoken"
    interceptors = [MetadataClientInterceptor(key)]
    with grpc.insecure_channel('52.12.126.83:50051') as channel:
        channel = grpc.intercept_channel(channel, *interceptors)
        stub = SpeechRecognizerStub(channel)
        # transcribe_audio_url(stub)
        # transcribe_audio_bytes(stub)
        # get_srt_audio_url(stub)
        # get_srt_audio_bytes(stub)
        get_text_from_wavfile_any_length(stub,audio_file)
