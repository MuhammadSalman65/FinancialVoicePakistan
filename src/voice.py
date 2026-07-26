import speech_recognition as sr
import subprocess
import imageio_ffmpeg
import io

def convert_audio_to_wav(audio_bytes):
    """
    Direct imageio_ffmpeg binary use karke audio (WebM/Ogg) ko PCM WAV mein convert karta hai.
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    
    cmd = [
        ffmpeg_exe,
        '-i', 'pipe:0',          # stdin se input audio lena
        '-f', 'wav',             # output format wav
        '-acodec', 'pcm_s16le',   # 16-bit PCM audio
        '-ar', '16000',          # 16kHz sample rate
        '-ac', '1',              # Mono channel
        'pipe:1'                 # stdout par wav bytes return karna
    ]
    
    process = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    wav_bytes, stderr = process.communicate(input=audio_bytes)
    
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion error: {stderr.decode('utf-8', errors='ignore')}")
        
    return wav_bytes

def transcribe_audio(audio_bytes, language="ur-PK"):
    """
    Browser audio ko WAV mein convert karke Urdu text mein translate karta hai.
    """
    recognizer = sr.Recognizer()
    
    try:
        # Step 1: WebM audio ko WAV bytes mein convert karna
        wav_bytes = convert_audio_to_wav(audio_bytes)
        wav_stream = io.BytesIO(wav_bytes)
        
        # Step 2: Speech Recognition Engine
        with sr.AudioFile(wav_stream) as source:
            audio_data = recognizer.record(source)
            
        text = recognizer.recognize_google(audio_data, language=language)
        return text, None
        
    except sr.UnknownValueError:
        return None, "Aawaz clear nahi thi, baraye mehrbani dobara saaf aawaz mein bolein."
    except sr.RequestError as e:
        return None, f"Internet / Speech service error: {e}"
    except Exception as e:
        return None, f"Audio process karne mein masla aaya: {e}"