from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import numpy as np
import soundfile as sf
import io
from test_report_generate import generate_hearing_report
from speech_test import get_speech_tests, pan_audio
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:3001", "https://stagingauralhearingcare.netlify.app"]}})

def generate_tone(frequency, duration=1, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * frequency * t)
    return (tone * 32767).astype(np.int16)

@app.route('/api/speech-test', methods=['GET'])
def get_speech_test_audio():
    try:
        speech_tests = get_speech_tests()
        
        result = {}
        for ear in ['left', 'right']:
            result[ear] = []
            for round_number, conversation_number, words, _ in speech_tests[ear]:
                result[ear].append({
                    "round_number": round_number,
                    "conversation_number": conversation_number,
                    "words": words,
                    "audio_url": f"/api/speech-test/{ear}/audio/{round_number}"
                })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/speech-test/<ear>/audio/<int:round_number>', methods=['GET'])
def serve_speech_test_audio(ear, round_number):
    if ear not in ['left', 'right'] or round_number not in [1, 2]:
        return jsonify({"error": "Invalid ear or round number"}), 400

    try:
        speech_tests = get_speech_tests()
        audio_file = next(audio_file for r, _, _, audio_file in speech_tests[ear] if r == round_number)
        
        print(f"Attempting to serve audio file: {audio_file}")
        
        if not os.path.exists(audio_file):
            print(f"Audio file not found: {audio_file}")
            return jsonify({"error": f"Audio file not found: {audio_file}"}), 404

        panned_audio = pan_audio(audio_file, ear)
        
        return send_file(
            io.BytesIO(panned_audio),
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'speech_test_{ear}_round_{round_number}.wav'
        )
    except Exception as e:
        print(f"Error serving audio file: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    

@app.route('/api/hearing-test/play-tone', methods=['GET'])
def play_hearing_tone():
    frequency = int(request.args.get("frequency", "1000"))
    ear = request.args.get("ear", "right")

    valid_frequencies = [250, 500, 1000, 2000, 4000, 8000]
    valid_ears = ["left", "right"]

    if frequency not in valid_frequencies or ear not in valid_ears:
        return jsonify({"error": "Invalid frequency or ear parameter"}), 400

    tone = generate_tone(frequency)
    
    # Create stereo audio with the tone in the specified ear
    stereo_tone = np.zeros((len(tone), 2), dtype=np.int16)
    if ear == "left":
        stereo_tone[:, 0] = tone
    else:
        stereo_tone[:, 1] = tone

    buffer = io.BytesIO()
    sf.write(buffer, stereo_tone, 44100, format='wav')
    buffer.seek(0)

    return send_file(buffer, mimetype='audio/wav')

@app.route('/api/hearing-test/submit', methods=['POST'])
def submit_hearing_test():
    data = request.json
    print("Received data:", data)  # Add this line for debugging

    if not all(key in data for key in ['full_name', 'age', 'contact', 'answers', 'toneTestResults', 'speechTestResults']):
        return jsonify({"error": "Invalid input data"}), 400

    try:
        report = generate_hearing_report(data)
        return jsonify({"message": "Test results received and report generated successfully", "report": report}), 200
    except Exception as e:
        print("Error generating report:", str(e))  # Add this line for debugging
        return jsonify({"error": f"Error generating report: {str(e)}"}), 500

@app.route('/api/hearing-test/report', methods=['GET'])
def get_hearing_test_report():
    # This route should be implemented to return the last generated report
    # For now, we'll return a placeholder message
    return jsonify({"message": "Report retrieval not implemented yet"}), 501

@app.route('/')
def status():
    return render_template('status.html')

@app.route('/status')
def status_check():
    return render_template('status.html')

if __name__ == '__main__':
    app.run(debug=True)
    
