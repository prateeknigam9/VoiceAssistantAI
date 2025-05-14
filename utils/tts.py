import os
import logging

logger = logging.getLogger(__name__)

def text_to_voice(speech_file_path: str, text_to_convert: str, client) -> str:
    """
    Converts the text to speech using ElevenLabs and saves it to the specified file path.
    
    Args:
        speech_file_path: Path where the generated audio will be saved
        text_to_convert: Text content to convert to speech
        client: Initialized ElevenLabs client
        
    Returns:
        Path to the generated audio file
    """
    logger.debug(f"Converting text to speech using ElevenLabs: {speech_file_path}")
    
    try:
        # Generate audio using ElevenLabs
        audio = client.generate(
            text=text_to_convert,
            voice="eleven_flash_v2_5",
            model="eleven_flash_v2"
        )
        
        # Save the audio to a file
        with open(speech_file_path, "wb") as f:
            f.write(audio)
        
        return speech_file_path
    
    except Exception as e:
        logger.error(f"Error during text-to-speech conversion: {str(e)}")
        raise Exception(f"Text-to-speech conversion failed: {str(e)}")
