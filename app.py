import os
import logging
import tempfile
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, send_file
from dotenv import load_dotenv
from groq import Groq
from elevenlabs import ElevenLabs

from utils.transcription import voice_to_text
from utils.tts import text_to_voice
from utils.search import generate_search_terms
from utils.web_scraper import extract_content_from_links
from utils.llm import generate_response

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize API clients
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "voice_agent_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

RESPONSE_FOLDER = os.path.join(tempfile.gettempdir(), "voice_agent_responses")
os.makedirs(RESPONSE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Initialize session if needed
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    return render_template('index.html', conversation_history=session['conversation_history'])

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        # Check if file is present in request
        if 'audio_file' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio_file']
        if audio_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Save uploaded file
        unique_filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        audio_file.save(audio_path)
        logger.debug(f"Saved audio file to {audio_path}")
        
        # Step 1: Transcribe audio to text
        try:
            transcribed_text = voice_to_text(audio_path, groq_client)
            logger.debug(f"Transcribed text: {transcribed_text}")
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
        
        # Get or initialize conversation history
        conversation_history = session.get('conversation_history', [])
        
        # Add user message to conversation history
        conversation_history.append({
            "role": "user", 
            "content": transcribed_text,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Step 2: Generate search terms
        try:
            search_term = generate_search_terms(transcribed_text, groq_client)
            logger.debug(f"Generated search term: {search_term}")
        except Exception as e:
            logger.error(f"Search term generation error: {str(e)}")
            return jsonify({"error": f"Search term generation failed: {str(e)}"}), 500
        
        # Step 3: Extract content from Irish government website
        try:
            extracted_content = extract_content_from_links(search_term)
            logger.debug(f"Extracted content: {extracted_content[:100]}...")
        except Exception as e:
            logger.error(f"Content extraction error: {str(e)}")
            extracted_content = "Unable to extract relevant content. Providing general information instead."
        
        # Step 4: Generate response using LLM
        try:
            response_text = generate_response(conversation_history, extracted_content, groq_client)
            logger.debug(f"Generated response: {response_text[:100]}...")
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return jsonify({"error": f"Response generation failed: {str(e)}"}), 500
        
        # Add assistant response to conversation history
        conversation_history.append({
            "role": "assistant", 
            "content": response_text,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Update session
        session['conversation_history'] = conversation_history
        
        # Step 5: Convert response to speech
        try:
            response_audio_path = os.path.join(RESPONSE_FOLDER, f"response_{uuid.uuid4()}.wav")
            text_to_voice(response_audio_path, response_text, elevenlabs_client)
            logger.debug(f"Generated audio response at {response_audio_path}")
        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            return jsonify({
                "transcribed_text": transcribed_text,
                "response_text": response_text,
                "error": f"Text-to-speech conversion failed: {str(e)}"
            }), 500
        
        # Return response with both text and audio
        return jsonify({
            "transcribed_text": transcribed_text,
            "response_text": response_text,
            "audio_path": response_audio_path,
            "conversation_history": conversation_history
        })
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['conversation_history'] = []
    return jsonify({"status": "success"})

@app.route('/get_audio/<path:filename>')
def get_audio(filename):
    # Security check to prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        return jsonify({"error": "Invalid filename"}), 400
    
    # Return the audio file
    full_path = os.path.join(RESPONSE_FOLDER, os.path.basename(filename))
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404
    
    # Check the file extension and set appropriate mimetype
    if filename.endswith('.mp3'):
        mimetype = 'audio/mp3'
    else:
        mimetype = 'audio/mpeg'  # More generic audio mimetype
        
    return send_file(full_path, mimetype=mimetype)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
