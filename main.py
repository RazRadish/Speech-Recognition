import pyaudio
import wave
import speech_recognition as sr
import time
import vosk


# Set recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000
CHUNK = 8192
RECORD_SECONDS = 20
WAVE_OUTPUT_FILENAME = "output.wav"

# Create PyAudio object
audio = pyaudio.PyAudio()

# Ask if user wants to record audio
record_input = input("Do you want to record audio? (y/n) ")
if record_input.lower() == "y":
    # Open microphone and start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Start Recording...")

    # Record audio data
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("End Recording！")

    # Stop recording and close stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save recorded audio to WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Ask user to input the correct transcription of the audio recording
correct_text = input("Please enter the correct transcription of the audio recording: ").lower()

# Use SpeechRecognition library for speech recognition
recognizer = sr.Recognizer()

# Read WAV file
with sr.AudioFile('output.wav') as source:
    audio = recognizer.record(source)

start_time = time.time()

try:
    text = recognizer.recognize_google(audio).lower()
    print("text:", text)
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError as e:
    print("Error with the request; {0}".format(e))

# Calculate the longest common substring between the recognition results and the correct transcription
def lcs(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

lcs_text = lcs(text, correct_text)
matches = len(lcs_text.replace(" ", ""))
blank_count = correct_text.count(" ")
print("SpeechRecognition accuracy: {:.2f}%".format(matches / (len(correct_text) - blank_count) * 100))

end_time = time.time()  # End timer
elapsed_time = end_time - start_time  # Calculate speech recognition time

print("SR speech recognition time：{:.2f}s".format(elapsed_time))  # Output speech recognition time

# Set paths for Vosk model and language model
model_path = "F:/Model/vosk-model-en-us-0.22-lgraph"

# Initialize Vosk speech recognizer
vosk.SetLogLevel(-1)
model = vosk.Model(model_path)
recognizer = vosk.KaldiRecognizer(model, 32000)

# Open audio file
audio_file = wave.open("output.wav", "rb")

# Read audio data
data = audio_file.readframes(4000)

# Start speech recognition
start_time = time.time()
while len(data) > 0:
    if recognizer.AcceptWaveform(data):
        pass
    data = audio_file.readframes(4000)

end_time = time.time()  # End timer
elapsed_time = end_time - start_time  # Calculate speech recognition time

# Compare the recognition results from Vosk library to the correct transcription
result = recognizer.FinalResult()
vosk_text = result[result.index('"text"')+8:result.index('}')-1].lower()
print("Vosk:"+vosk_text)
vosk_lcs_text = lcs(vosk_text, correct_text)
vosk_matches = len(vosk_lcs_text.replace(" ", ""))
print("Vosk accuracy: {:.2f}%".format(vosk_matches / (len(correct_text) - blank_count) * 100))

print("Vosk speech recognition time：{:.2f}s".format(elapsed_time))