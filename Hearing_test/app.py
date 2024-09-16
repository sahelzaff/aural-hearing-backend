from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from utils import generate_pdf_report

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire application

# Serve generated tones
@app.route('/api/hearing-test/play-tone', methods=['GET'])
def play_hearing_tone():
    frequency = request.args.get("frequency", "1000")
    ear = request.args.get("ear", "right")

    # File path for the sound
    file_path = f"tones/{frequency}Hz_{ear}.wav"
    if not os.path.exists(file_path):
        return jsonify({"error": "Tone not found"}), 404

    return send_file(file_path, as_attachment=True)

# API to handle user responses and generate a report
@app.route('/api/hearing-test/submit', methods=['POST'])
def submit_hearing_test():
    data = request.json

    # Validate input data
    if 'full_name' not in data or 'age' not in data or 'contact' not in data or 'answers' not in data:
        return jsonify({"error": "Invalid input data"}), 400

    # Generate PDF report
    pdf_file = generate_pdf_report(data)

    # Return the report
    return send_file(pdf_file, as_attachment=True)

# Route for status page
@app.route('/')
def status():
    return render_template('status.html')

if __name__ == '__main__':
    # Set host to '0.0.0.0' to make the app available externally
    # Port should be set by the environment variable PORT, default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
