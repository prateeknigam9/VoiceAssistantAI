import os
import logging

logger = logging.getLogger(__name__)

def voice_to_text(file_name: str, client) -> str:
    """
    Transcribes the audio file to text using Groq's Whisper-large-v3 model.
    
    Args:
        file_name: Path to the audio file
        client: Initialized Groq client
        
    Returns:
        Transcribed text from the audio file
    """
    logger.debug(f"Transcribing audio file: {file_name}")
    
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"Audio file not found: {file_name}")
    
    try:
        with open(file_name, "rb") as audio_file:
            # Use Groq's Whisper large v3 model for transcription
            response = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3"
            )
            
            if hasattr(response, "text"):
                return response.text
            else:
                logger.error(f"Unexpected response format: {response}")
                raise ValueError("Transcription response missing text field")
    
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise Exception(f"Transcription failed: {str(e)}")
