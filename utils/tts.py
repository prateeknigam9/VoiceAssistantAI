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
        # First, get available voices and use the first one in the list
        voices = client.voices.get_all()
        if not voices or not voices.voices:
            raise Exception("No voices available with your ElevenLabs account")
            
        # Get the voice ID of the first voice (using ID is more reliable)
        default_voice_id = voices.voices[0].voice_id
        default_voice_name = voices.voices[0].name
        logger.debug(f"Using voice: {default_voice_name} (ID: {default_voice_id})")
        
        # Make sure the output file has .mp3 extension since that's what ElevenLabs returns
        if not speech_file_path.endswith('.mp3'):
            speech_file_path = speech_file_path.rsplit('.', 1)[0] + '.mp3'
        
        audio = client.generate(
            text=text_to_convert,
            voice=default_voice_id,  # Use the voice ID instead of name
            model="eleven_flash_v2",
            output_format="mp3_44100_128"  # Using a specific supported format
        )
        
        # Save the audio to a file
        with open(speech_file_path, "wb") as f:
            # Check if audio is a generator or iterator, and consume it if needed
            if hasattr(audio, '__iter__') and not isinstance(audio, bytes):
                for chunk in audio:
                    f.write(chunk)
            else:
                # If it's already bytes, write it directly
                f.write(audio)
        
        return speech_file_path
    
    except Exception as e:
        logger.error(f"Error during text-to-speech conversion: {str(e)}")
        raise Exception(f"Text-to-speech conversion failed: {str(e)}")
