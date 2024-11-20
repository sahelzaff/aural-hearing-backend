import numpy as np
from scipy import stats

def calculate_hearing_metrics(tone_test_results):
    print("Received tone test results:", tone_test_results)  # Add this line for debugging
    
    frequencies = [4000]  # Adjust this list based on your actual test frequencies
    ears = ['left', 'right']
    
    thresholds = tone_test_results
    
    # Calculate average hearing threshold
    avg_threshold = np.mean([thresholds[f"{freq}Hz {ear} Ear barely"] for freq in frequencies for ear in ears])
    
    # Calculate dynamic range
    dynamic_ranges = {f"{freq}Hz_{ear}": thresholds[f"{freq}Hz {ear} Ear loudest"] - thresholds[f"{freq}Hz {ear} Ear barely"] 
                      for freq in frequencies for ear in ears}
    avg_dynamic_range = np.mean(list(dynamic_ranges.values()))
    
    return avg_threshold, avg_dynamic_range, thresholds, dynamic_ranges

def calculate_age_factor(age):
    age_factor = 1 - (0.002 * max(0, age - 40))  # Start decline at age 40
    return max(0.85, age_factor)  # Cap the minimum at 0.85

def calculate_qualitative_adjustment(answers):
    adjustment_map = {
        "Always": -10,
        "Often": -7,
        "Sometimes": -4,
        "Rarely": -1,
        "Never": 0
    }
    importance_weights = {
        "hearing_description": 1.2,
        "conversation_follow": 1.0,
        "phone_conversation": 0.8,
        "high_pitched_sounds": 1.1,
        "noisy_environments": 1.3
    }
    
    total_adjustment = sum(
        adjustment_map.get(answers.get(key, 'Never'), 0) * importance_weights.get(key, 1.0)
        for key in importance_weights
    )
    
    return max(-20, min(0, total_adjustment))  # Clamp between -20 and 0

def calculate_speech_recognition_score(speech_results):
    correct_words = ["Boat", "Cat", "Orange", "Banana", "Bird", "King", "Cat", "Boat", "Bird", "Banana", "Dog", "Book"]
    total_words = sum(len(round['selectedWords']) for round in speech_results)
    correct_count = sum(word in correct_words for round in speech_results for word in round['selectedWords'])
    return (correct_count / total_words) * 100

def calculate_hearing_score(speech_score, avg_threshold, avg_dynamic_range, age_factor, qualitative_adjustment):
    base_score = 100 - (avg_threshold / 1.5)  # Adjusted threshold impact
    
    hearing_score = (
        base_score * 0.3 +
        speech_score * 0.3 +
        (avg_dynamic_range / 1.5) * 0.2 +
        qualitative_adjustment * 0.2
    ) * age_factor
    
    return max(60, min(100, hearing_score))  # Clamp the score between 60 and 100

def get_hearing_status(hearing_score):
    if hearing_score > 95:
        return "Excellent Hearing"
    elif hearing_score > 90:
        return "Very Good Hearing"
    elif hearing_score > 85:
        return "Good Hearing"
    elif hearing_score > 80:
        return "Slightly Above Average Hearing"
    elif hearing_score > 75:
        return "Average Hearing"
    elif hearing_score > 70:
        return "Slightly Below Average Hearing"
    elif hearing_score > 65:
        return "Borderline Hearing"
    else:
        return "Mild Hearing Concerns"

def get_recommendation(hearing_status):
    if hearing_status in ["Borderline Hearing", "Mild Hearing Concerns"]:
        return (
            "While your hearing is generally good, there might be room for improvement in certain areas. "
            "We recommend scheduling a professional hearing evaluation to address any specific concerns "
            "and discuss potential strategies to enhance your hearing experience in challenging situations."
        )
    elif hearing_status in ["Slightly Below Average Hearing", "Average Hearing"]:
        return (
            "Your hearing is within the normal range, but there might be opportunities to optimize your hearing experience. "
            "We recommend annual hearing check-ups and taking preventive measures to protect your hearing. "
            "If you experience any changes or difficulties in specific situations, consider consulting a hearing professional."
        )
    else:
        return (
            "Your hearing appears to be in good to excellent condition. To maintain your hearing health, we recommend annual check-ups "
            "and protecting your ears from loud noises. Stay aware of your hearing health and don't hesitate to consult a professional "
            "if you notice any changes in your hearing ability."
        )
