import os
import wave
import time
import speech_recognition as sr
from django.conf import settings
import threading
import pyaudio
from .models import AudioRecord
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
import nltk
from nltk.tokenize import sent_tokenize
from django.urls import reverse  # Import the reverse function

# Download the necessary NLTK data
nltk.download('punkt')

# Global variables
recording = False
audio_frames = []

def start_recording(request):
    global recording
    recording = True
    threading.Thread(target=record_audio).start()
    return render(request, 'speech_to_text/index.html')

def stop_recording(request):
    global recording
    recording = False
    return render(request, 'speech_to_text/index.html')

def record_audio():
    global recording, audio_frames
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)

    audio_frames = []
    start_time = time.time()
    while recording:
        data = stream.read(chunk)
        audio_frames.append(data)
        if not recording:
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    if audio_frames:
        # Save the audio file
        output_dir = os.path.join(settings.BASE_DIR, 'output')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"output_{timestamp}.wav"
        file_path = os.path.join(output_dir, filename)
        file_path = os.path.abspath(file_path)
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(audio_frames))
        wf.close()
        print(f"Saved audio file to: {file_path}")
        
        # Calculate duration
        duration = time.time() - start_time

        # Save record to database
        AudioRecord.objects.create(
            file_name=filename,
            file_path=file_path,
            duration=duration
        )

def speech_to_text(request):
    # Get the latest record
    latest_record = AudioRecord.objects.order_by('-created_at').first()

    if latest_record:
        text = convert_audio_to_text(latest_record.file_path)
        
        # Read the content of the generated text file
        txt_file = os.path.splitext(latest_record.file_path)[0] + ".txt"
        try:
            with open(txt_file, "r", encoding="utf-8") as file:
                file_content = file.read()
        except FileNotFoundError:
            file_content = None
    else:
        text = None
        file_content = None

    return render(request, 'speech_to_text/index.html', {'text': text, 'file_content': file_content})

def list_records(request):
    records = AudioRecord.objects.all().order_by('-created_at')
    return render(request, 'speech_to_text/list_records.html', {'records': records})

def convert_audio_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
    try:
        text = r.recognize_google(audio_data)
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)
        # Join the sentences with periods
        punctuated_text = '. '.join(sentences) + '.'

        # Save the punctuated text to a file
        txt_file = os.path.splitext(audio_file)[0] + ".txt"
        with open(txt_file, "w", encoding="utf-8") as file:
            file.write(punctuated_text)

        # Save the transcription to the AudioRecord model
        record = AudioRecord.objects.get(file_path=audio_file)
        record.transcription = punctuated_text
        record.save()

        return punctuated_text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Error: {e}"

def index(request):
    if request.method == 'POST':
        if 'start_recording' in request.POST:
            return start_recording(request)
        elif 'stop_recording' in request.POST:
            return stop_recording(request)
        elif 'convert' in request.POST:
            return speech_to_text(request)
        elif 'summarize' in request.POST:
            # Get the content of the output.txt file
            output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../output/output.txt')
            try:
                with open(output_file_path, 'r') as file:
                    text = file.read()
            except FileNotFoundError:
                text = ''

            # Redirect to the 'summarize' view in the 'texts' app and pass the text as a GET parameter
            summarize_url = reverse('summarize') + '?text=' + text
            return redirect(summarize_url)

    return render(request, 'speech_to_text/index.html')


def view_transcription(request, record_id):
    record = get_object_or_404(AudioRecord, id=record_id)
    return render(request, 'speech_to_text/view_transcription.html', {'record': record})