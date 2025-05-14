# Irish Government Voice Agent Pipeline

This project implements a voice agent pipeline that processes audio input, transcribes it using Groq, searches the Irish government website for relevant information, generates responses, and converts text to speech via ElevenLabs.

## Features

- Transcription of voice input using Groq's Whisper-large-v3 model
- Search term generation for Irish government website queries
- Web scraping of relevant content from gov.ie
- Response generation using Groq's Llama 3 model
- Text-to-speech conversion using ElevenLabs

## Requirements

- Python 3.11+
- Groq API key
- ElevenLabs API key
- Required Python packages: groq, elevenlabs, requests, beautifulsoup4, trafilatura, dotenv

## Two Versions Available

### 1. Voice Agent (Full Pipeline)

This version follows the complete pipeline:
1. Receives audio file input
2. Transcribes audio to text 
3. Generates search terms
4. Extracts content from Irish government website
5. Generates a response
6. Converts response to speech

Usage:
```
python voice_agent.py
```

Follow the prompts to provide the path to your audio file. The script will process it and generate an audio response.

### 2. Text-Based Agent (Simplified)

This version skips the audio processing steps and works with text input directly:
1. Takes text question as input
2. Generates search terms
3. Extracts content from Irish government website
4. Generates a text response

Usage:
```
python text_based_agent.py
```

Simply type your question when prompted, and the agent will search for information and respond with text.

## Environment Variables

Both scripts require the following environment variables:
- `GROQ_API_KEY`: Your Groq API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key (only needed for voice_agent.py)

## Note on Audio Files

The voice agent requires audio files as input. It supports various audio formats including WAV, MP3, and M4A. The audio should contain a clear question or request about Irish government services.

## Conversation History

Both agents maintain conversation history during a session, allowing for contextual follow-up questions. To start a new conversation, simply restart the script.