import random
import numpy as np
from scipy import stats
from advanced_analysis import (
    calculate_hearing_metrics, calculate_age_factor, calculate_qualitative_adjustment,
    calculate_speech_recognition_score, calculate_hearing_score, get_hearing_status, get_recommendation
)

def generate_hearing_report(user_data):
    print("Received user data:", user_data)  # Add this line for debugging

    # Check if toneTestResults exists and is not empty
    if 'toneTestResults' not in user_data or not user_data['toneTestResults']:
        raise ValueError("toneTestResults is missing or empty")

    # Calculate hearing metrics
    avg_threshold, avg_dynamic_range, frequency_thresholds, dynamic_ranges = calculate_hearing_metrics(user_data['toneTestResults'])
    
    # Calculate speech recognition score
    speech_score = calculate_speech_recognition_score(user_data['speechTestResults'])
    
    # Calculate age factor
    age = int(user_data.get('age', 0))
    age_factor = 1 - (0.002 * max(0, age - 40))  # Start decline at age 40
    age_factor = max(0.85, age_factor)  # Cap the minimum at 0.85
    
    # Calculate qualitative adjustment (you might need to implement this function)
    qualitative_adjustment = 0  # Placeholder, implement as needed
    
    # Calculate final hearing score
    hearing_score = calculate_hearing_score(speech_score, avg_threshold, avg_dynamic_range, age_factor, qualitative_adjustment)
    
    # Get hearing status and recommendation
    hearing_status = get_hearing_status(hearing_score)
    recommendation = get_recommendation(hearing_status)
    
    # Calculate confidence interval
    confidence_interval = stats.norm.interval(0.95, loc=hearing_score, scale=2)
    
    # Generate report
    report = {
        "name": user_data.get("full_name"),
        "age": age,
        "hearing_status": hearing_status,
        "speech_recognition_score": round(speech_score, 2),
        "hearing_score": round(hearing_score, 2),
        "confidence_interval": [round(ci, 2) for ci in confidence_interval],
        "avg_threshold": round(avg_threshold, 2),
        "avg_dynamic_range": round(avg_dynamic_range, 2),
        "age_factor": round(age_factor, 2),
        "qualitative_adjustment": round(qualitative_adjustment, 2),
        "recommendation": recommendation,
        "frequency_thresholds": {k: round(v, 2) for k, v in frequency_thresholds.items()},
        "dynamic_ranges": {k: round(v, 2) for k, v in dynamic_ranges.items()}
    }
    return report
