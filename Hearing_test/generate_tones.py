import numpy as np
from scipy.io.wavfile import write
import os

# Directory to store generated sound files
os.makedirs("tones", exist_ok=True)

def generate_tone(frequency, duration, sample_rate=44100, amplitude=0.5):
    """Generates a sine wave tone at a given frequency."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False) 
    audio = amplitude * np.sin(2 * np.pi * frequency * t) 
    return audio

def save_tone(frequency, duration=60, ear='both'):
    """Generates and saves a tone for a specific frequency and ear."""
    sample_rate = 44100 
    audio = generate_tone(frequency, duration, sample_rate)

    if ear == 'right':
      
        audio_stereo = np.zeros((len(audio), 2))
        audio_stereo[:, 1] = audio  
    elif ear == 'left':
        
        audio_stereo = np.zeros((len(audio), 2))
        audio_stereo[:, 0] = audio  
    else:
       
        audio_stereo = np.column_stack((audio, audio))

    
    filename = f"tones/{frequency}Hz_{ear}.wav"
    write(filename, sample_rate, audio_stereo.astype(np.float32))
    print(f"Generated {filename}")


frequencies = [1000, 2000, 4000, 6000]  
ears = ['left', 'right']  # Ear selection

for freq in frequencies:
    for ear in ears:
        save_tone(freq, ear=ear)  
