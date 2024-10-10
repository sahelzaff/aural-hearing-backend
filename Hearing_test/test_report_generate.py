import random
import numpy as np

def generate_hearing_report(user_data):
    # Calculate speech test score
    correct_words = ["Boat", "Cat", "Orange", "Banana", "Bird", "King", "Cat", "Boat", "Bird", "Banana", "Dog", "Book"]
    total_correct = 0
    total_tests = len(user_data['speechTestResults'])
    
    for result in user_data['speechTestResults']:
        selected = result['selectedWords']
        correct = correct_words[:min(len(correct_words), len(selected))]
        round_score = sum([1 if word == correct[i] else 0.5 if word in correct else 0 for i, word in enumerate(selected)])
        total_correct += round_score
    
    speech_score = (total_correct / (total_tests * 3)) * 100  # Assuming 3 words per round
    
    # Analyze decibel levels
    right_ear_barely = user_data['decibelLevels'].get('4000Hz right Ear barely', 0)
    left_ear_barely = user_data['decibelLevels'].get('4000Hz left Ear barely', 0)
    right_ear_loudest = user_data['decibelLevels'].get('4000Hz right Ear loudest', 0)
    left_ear_loudest = user_data['decibelLevels'].get('4000Hz left Ear loudest', 0)
    
    # Calculate average hearing threshold
    avg_threshold = (right_ear_barely + left_ear_barely) / 2
    
    # Calculate dynamic range
    right_ear_range = right_ear_loudest - right_ear_barely
    left_ear_range = left_ear_loudest - left_ear_barely
    avg_range = (right_ear_range + left_ear_range) / 2
    
    # Age factor adjustment
    age = int(user_data.get('age', 0))
    age_factor = max(0.7, 1 - (age - 18) * 0.005) if age >= 18 else 1.0
    
    # Helper function to adjust qualitative score
    def adjust_qualitative_score(feedback_key, feedback_value):
        adjustment_map = {
            "Always": -15,
            "Often": -10,
            "Sometimes": -5,
            "Rarely": -2,
            "Never": 0
        }
        return adjustment_map.get(feedback_value, 0)
    
    # Qualitative answers influence
    feedback = user_data['answers']
    qualitative_score_adjustment = sum([
        adjust_qualitative_score(key, feedback.get(key, 'Never'))
        for key in ['hearing_description', 'conversation_follow', 'phone_conversation', 'high_pitched_sounds', 'noisy_environments']
    ])
    
    # Calculate base hearing score
    base_score = 100 - (avg_threshold / 2)  # Assuming 100 dB is the max threshold
    
    # Adjust score based on speech recognition, dynamic range, age, and qualitative feedback
    hearing_score = (
        base_score * 0.4 +
        speech_score * 0.3 +
        (avg_range / 2) * 0.1 +  # Assuming 100 dB is the max range
        qualitative_score_adjustment
    ) * age_factor
    
    hearing_score = max(0, min(100, hearing_score))  # Clamp the score between 0 and 100
    
    # Determine hearing status
    if hearing_score > 90:
        status = "Excellent Hearing"
    elif hearing_score > 80:
        status = "Good Hearing"
    elif hearing_score > 70:
        status = "Mild Hearing Loss"
    elif hearing_score > 60:
        status = "Moderate Hearing Loss"
    elif hearing_score > 40:
        status = "Moderately Severe Hearing Loss"
    elif hearing_score > 20:
        status = "Severe Hearing Loss"
    else:
        status = "Profound Hearing Loss"
    
    # Generate detailed recommendation
    if status in ["Moderate Hearing Loss", "Moderately Severe Hearing Loss", "Severe Hearing Loss", "Profound Hearing Loss"]:
        recommendation = (
            "Based on the results, we strongly recommend consulting an audiologist for a comprehensive hearing evaluation. "
            "Early intervention can significantly improve your quality of life and prevent further hearing deterioration."
        )
    elif status == "Mild Hearing Loss":
        recommendation = (
            "Your hearing shows signs of mild loss. We recommend scheduling a professional hearing evaluation to address "
            "any concerns and discuss potential solutions to improve your hearing experience."
        )
    else:
        recommendation = (
            "Your hearing appears to be in good condition. To maintain your hearing health, we recommend annual check-ups "
            "and protecting your ears from loud noises. If you experience any changes in your hearing, don't hesitate to consult a professional."
        )
    
    # Generate report
    report = {
        "name": user_data.get("full_name"),
        "age": age,
        "hearing_status": status,
        "score_percentage": round(speech_score, 2),
        "hearing_score": round(hearing_score, 2),
        "right_ear_threshold": right_ear_barely,
        "left_ear_threshold": left_ear_barely,
        "right_ear_loudest": right_ear_loudest,
        "left_ear_loudest": left_ear_loudest,
        "recommendation": recommendation
    }
    return report