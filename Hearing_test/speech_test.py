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
             (round_number, conversation_number, words, audio_data) tuples
    """
    return {
        'left': get_speech_test('left'),
        'right': get_speech_test('right')
    }