from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from speech_test import get_speech_tests
import io
from test_report_generate import generate_hearing_report  # Import the report generation function

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000","http://localhost:3001", "https://stagingauralhearingcare.netlify.app"]}})

# Global variable to store the generated report
generated_report = None

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
    if ear not in ['left', 'right'] or round_number not in [1, 2, 3]:
        return jsonify({"error": "Invalid ear or round number"}), 400

    try:
        speech_tests = get_speech_tests()
        audio_data = next(audio for r, _, _, audio in speech_tests[ear] if r == round_number)
        
        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f'speech_test_{ear}_round_{round_number}.wav'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

@app.route('/api/hearing-test/play-tone', methods=['GET'])
def play_hearing_tone():
    frequency = request.args.get("frequency", "1000")
    ear = request.args.get("ear", "right")


    valid_frequencies = ["1000", "2000", "3000", "4000"]
    valid_ears = ["left", "right"]

    if frequency not in valid_frequencies or ear not in valid_ears:
        return jsonify({"error": "Invalid frequency or ear parameter"}), 400

   
    file_path = f"tones/{frequency}Hz_{ear}.wav"
    if not os.path.exists(file_path):
        return jsonify({"error": "Tone not found"}), 404

    return send_file(file_path, as_attachment=True)

# @app.route('/api/hearing-test/submit', methods=['POST'])
# def submit_hearing_test():
#     data = request.json

#     if 'full_name' not in data or 'age' not in data or 'contact' not in data or 'answers' not in data or 'decibelLevels' not in data or 'speechTestResults' not in data:
#         return jsonify({"error": "Invalid input data"}), 400

#     decibel_levels = data['decibelLevels']
#     speech_test_results = data['speechTestResults']

#     # Process the data and generate the PDF report
#     pdf_file = merge_with_template('Template_Report.pdf', data, decibel_levels, speech_test_results)

#     return send_file(pdf_file, as_attachment=True)

@app.route('/api/hearing-test/submit', methods=['POST'])
def submit_hearing_test():
    global generated_report
    data = request.json

    if 'full_name' not in data or 'age' not in data or 'contact' not in data or 'answers' not in data or 'decibelLevels' not in data or 'speechTestResults' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    try:
        # Generate the report using the data
        generated_report = generate_hearing_report(data)
        
        return jsonify({"message": "Test results received and report generated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating report: {str(e)}"}), 500

@app.route('/api/hearing-test/report', methods=['GET'])
def get_hearing_test_report():
    global generated_report
    if generated_report is None:
        return jsonify({"error": "No report has been generated yet"}), 404
    
    return jsonify(generated_report), 200

@app.route('/')
def status():
    return render_template('status.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)