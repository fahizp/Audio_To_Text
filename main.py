import os
from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def convert_audio(file_path, output_format="wav"):
    audio = AudioSegment.from_file(file_path)
    output_file = file_path.replace(file_path.split('.')[-1], output_format)
    audio.export(output_file, format=output_format)
    return output_file

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return "Could not request results from Google Speech Recognition service; {0}".format(e)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    converted_file = convert_audio(file_path)
    transcription = transcribe_audio(converted_file)

    os.remove(file_path)
    os.remove(converted_file)
    
    return jsonify({"transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True)
