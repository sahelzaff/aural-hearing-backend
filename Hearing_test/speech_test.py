import random
from pydub import AudioSegment
import io
import os

# Define the conversations
CONVERSATIONS = {
    1: ["King", "Baby", "Book"],
    2: ["Cat", "Dog", "Bird"],
    3: ["Car", "Bike", "Boat"],
    4: ["Apple", "Banana", "Orange"]
}

BACKGROUND_LEVELS = ["Mid_Bg", "High_Bg"]  # Removed "High_Bg" as we now have only 2 rounds

def get_speech_test(ear):
    """
    Get speech test for a specific ear.
    
    :param ear: 'left' or 'right'
    :return: list of tuples, each containing (round_number, conversation_number, words, audio_data)
    """
    results = []
    available_conversations = list(CONVERSATIONS.keys())
    random.shuffle(available_conversations)  # Shuffle the conversation order

    for round_number in range(1, 3):  # Changed to 2 rounds
        # Randomly select a conversation that hasn't been used yet
        conversation_number = available_conversations.pop()
        words = CONVERSATIONS[conversation_number]
        
        # Select the appropriate background level for this round
        bg_level = BACKGROUND_LEVELS[round_number - 1]
        
        # Load the audio file for the selected conversation and background level
        audio_file = f"speech_audio/{bg_level}/conversation_{conversation_number}.wav"
        
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file {audio_file} not found.")
        
        audio = AudioSegment.from_wav(audio_file)
        
        # If it's for the left ear, set the right channel to silent, and vice versa
        if ear == 'left':
            audio = audio.pan(-1)
        elif ear == 'right':
            audio = audio.pan(1)
        
        # Export the audio to a byte stream
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        audio_data = buffer.getvalue()
        
        results.append((round_number, conversation_number, words, audio_data))
    
    return results

def get_speech_tests():
    """
    Get speech tests for both ears.
    
    :return: dictionary with 'left' and 'right' keys, each containing a list of 
             (round_number, conversation_number, words, audio_file_path) tuples
    """
    # Define the path to your audio files
    audio_path = os.path.join(os.path.dirname(__file__), 'speech_audio')
    
    speech_tests = {
        'left': [
            (1, 1, ["Boat", "Cat", "Dog"], os.path.join(audio_path, 'Mid_Bg/conversation_1.wav')),
            (2, 2, ["Fish", "Bird", "Car"], os.path.join(audio_path, 'High_Bg/conversation_2.wav')),
        ],
        'right': [
            (1, 1, ["Tree", "Book", "House"], os.path.join(audio_path, 'Mid_Bg/conversation_3.wav')),
            (2, 2, ["Ball", "Sun", "Moon"], os.path.join(audio_path, 'High_Bg/conversation_1.wav')),
        ]
    }
    return speech_tests

def pan_audio(audio_file_path, ear):
    """
    Pan the audio to the specified ear.
    
    :param audio_file_path: Path to the audio file
    :param ear: 'left' or 'right'
    :return: Panned audio as bytes
    """
    audio = AudioSegment.from_wav(audio_file_path)
    if ear == 'left':
        panned_audio = audio.pan(-1)
    elif ear == 'right':
        panned_audio = audio.pan(1)
    else:
        raise ValueError("Invalid ear specified. Must be 'left' or 'right'.")
    
    buffer = io.BytesIO()
    panned_audio.export(buffer, format="wav")
    return buffer.getvalue()
