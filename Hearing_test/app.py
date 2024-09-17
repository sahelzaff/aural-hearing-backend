from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from utils import merge_with_template

app = Flask(__name__)

cors = CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://stagingauralhearingcare.netlify.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "supports_credentials": True
    }
})

@app.route('/api/hearing-test/play-tone', methods=['GET'])
def play_hearing_tone():
    frequency = request.args.get("frequency", "1000")
    ear = request.args.get("ear", "right")

    # Validate inputs
    valid_frequencies = ["1000", "2000", "3000", "4000"]
    valid_ears = ["left", "right"]

    if frequency not in valid_frequencies or ear not in valid_ears:
        return jsonify({"error": "Invalid frequency or ear parameter"}), 400

    # Construct the file path
    file_path = f"tones/{frequency}Hz_{ear}.wav"
    if not os.path.exists(file_path):
        return jsonify({"error": "Tone not found"}), 404

    return send_file(file_path, as_attachment=True)

@app.route('/api/hearing-test/submit', methods=['POST'])
def submit_hearing_test():
    data = request.json

    # Ensure the necessary fields are present in the request
    if 'full_name' not in data or 'age' not in data or 'contact' not in data or 'answers' not in data or 'decibelLevels' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    # Extract decibel levels from the request
    decibel_levels = data['decibelLevels']

    # Generate the PDF using merge_with_template
    pdf_file = merge_with_template('Template_Report.pdf', data, decibel_levels)

    return send_file(pdf_file, as_attachment=True)

@app.route('/')
def status():
    return render_template('status.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
