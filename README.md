# Irish Government Voice Agent Pipeline

This project implements a voice agent pipeline that processes audio input, transcribes it using Groq, searches the Irish government website for relevant information, generates responses, and converts text to speech via ElevenLabs.

## Features

- Transcription of voice input using Groq's Whisper-large-v3 model
- Search term generation for Irish government website queries
- Web scraping of relevant content from gov.ie
- Response generation using Groq's Llama 3 model
- Text-to-speech conversion using ElevenLabs

## Local Installation and Setup

### Prerequisites

- Python 3.11 or higher
- Groq API key (from [Groq Console](https://console.groq.com))
- ElevenLabs API key (from [ElevenLabs](https://elevenlabs.io/app/speech-synthesis))

### Installation Steps

1. **Clone the repository**

```bash
git clone <repository-url>
cd irish-government-voice-agent
```

2. **Install required packages**

```bash
pip install groq elevenlabs requests beautifulsoup4 trafilatura python-dotenv
```

3. **Set up environment variables**

Create a `.env` file in the root directory with the following content:

```
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

Replace `your_groq_api_key_here` and `your_elevenlabs_api_key_here` with your actual API keys.

### Running the Application

#### Option 1: Voice Agent (Full Pipeline)

This version processes audio files and returns audio responses:

```bash
python voice_agent.py
```

When prompted, enter the path to your audio file containing your question about Irish government services.

#### Option 2: Text-Based Agent (Simplified)

This version accepts text input directly:

```bash
python text_based_agent.py
```

Simply type your question when prompted.

## Usage Examples

### Voice Agent Example

```
$ python voice_agent.py

================================================================================
                           IRISH GOVERNMENT VOICE AGENT                         
================================================================================

This program processes audio files containing questions about Irish government services.
It transcribes your voice, searches for relevant information, and responds with voice.

Type 'quit' to exit the program at any time.
================================================================================


Please provide the path to an audio file containing your question:
> question.wav

[1/5] Transcribing audio to text...
  Transcription: "How do I apply for a passport in Ireland?"

[2/5] Generating search terms...
  Search term: "passport application Ireland"

[3/5] Extracting content from Irish government website...
  Found information from 3 sources

[4/5] Generating response...
  Response: "To apply for an Irish passport, you have several options..."

[5/5] Converting response to speech...
  Audio response saved to: response_1684231456.wav

--------------------------------------------------------------------------------
Process completed successfully. The response is available in the file:
/path/to/response_1684231456.wav
--------------------------------------------------------------------------------
```

### Text-Based Agent Example

```
$ python text_based_agent.py

================================================================================
                           IRISH GOVERNMENT TEXT AGENT                          
================================================================================

This program answers questions about Irish government services.
It searches for relevant information on the official government website and generates responses.

Type 'quit' to exit the program at any time.
================================================================================


Please enter your question about Irish government services:
> How do I file for a visa?

[1/3] Generating search terms...
  Search term: "visa application Ireland"

[2/3] Extracting content from Irish government website...
  Found information from 2 sources

[3/3] Generating response...

--------------------------------------------------------------------------------
RESPONSE:
--------------------------------------------------------------------------------
To apply for a visa for Ireland, you need to follow these steps:

1. Determine the type of visa you need (tourist, work, study, etc.)
2. Complete the online application form
3. Pay the visa application fee
4. Submit supporting documentation
5. Attend a visa application center for biometrics if required

For detailed information on specific visa types and application procedures, visit the Irish Immigration Service website at https://www.irishimmigration.ie/
--------------------------------------------------------------------------------
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Make sure your API keys are correctly set in the `.env` file
   - Verify your API keys are valid and have sufficient credits

2. **Audio File Issues**
   - Ensure audio files are in a supported format (WAV, MP3, M4A)
   - Check that the path to the audio file is correct
   - Make sure the audio is clear and contains a distinguishable question

3. **Model Not Found Error**
   - If you get a model not found error, check the Groq documentation for currently available models
   - The code currently uses "llama3-70b-8192", which might need to be updated if Groq changes their model naming

4. **ElevenLabs Voice Issues**
   - The code is designed to automatically use the first available voice in your ElevenLabs account
   - Make sure you have at least one voice available in your account
   - If you want to use a specific voice, you can modify the code in `utils/tts.py` or `voice_agent.py`

## Additional Resources

- [Groq API Documentation](https://console.groq.com/docs/quickstart)
- [ElevenLabs API Documentation](https://docs.elevenlabs.io/api-reference/quick-start/introduction)
- [Irish Government Website](https://www.gov.ie)

## License

This project is available for educational and personal use.

## Detailed Documentation

For a detailed explanation of how the pipeline works, see [DOCUMENTATION.md](DOCUMENTATION.md).