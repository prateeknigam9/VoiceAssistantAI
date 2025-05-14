# Irish Government Voice Agent Pipeline: Technical Documentation

This documentation provides a detailed explanation of how the Irish Government Voice Agent Pipeline works, breaking down each function and process step-by-step.

## Table of Contents

1. [Overall Architecture](#overall-architecture)
2. [Voice Processing Pipeline](#voice-processing-pipeline)
3. [Core Functions Explained](#core-functions-explained)
4. [Data Flow and Session Management](#data-flow-and-session-management)
5. [Error Handling](#error-handling)
6. [API Integration Details](#api-integration-details)

## Overall Architecture

The system implements a pipeline architecture that:
1. Takes user input (voice or text)
2. Processes the input to extract search query terms
3. Searches the Irish government website for relevant information
4. Generates a response using Groq's LLM (Large Language Model)
5. Optionally converts the response to speech

The system is implemented in two versions:
- `voice_agent.py`: Terminal-based application that processes audio files
- `text_based_agent.py`: Terminal-based application that processes text input directly

Both versions share core functionality in the middle layers of the pipeline.

## Voice Processing Pipeline

### Full Pipeline Process Flow (voice_agent.py)

1. **Initialization**
   - Load environment variables (API keys)
   - Initialize API clients (Groq, ElevenLabs)
   - Create conversation history data structure

2. **Audio Input**
   - User provides the path to an audio file
   - System validates the file exists

3. **Voice-to-Text Transcription**
   - Audio file is sent to Groq's Whisper-large-v3 model
   - Transcribed text is returned and added to conversation history

4. **Search Term Generation**
   - Transcribed text is analyzed by Groq's LLM to extract key search terms
   - Search terms are optimized for the Irish government website

5. **Web Content Extraction**
   - System searches the Irish government website using the generated terms
   - Top results are scraped and their content is extracted and cleaned

6. **Response Generation**
   - Extracted content is sent to Groq's LLM along with conversation history
   - LLM generates a contextually appropriate response

7. **Text-to-Speech Conversion** 
   - Response text is sent to ElevenLabs
   - Audio response is generated and saved to a file

8. **Output**
   - The system returns the path to the generated audio file
   - The conversation history is updated with the response

9. **Loop**
   - The system waits for the next user input or exits if requested

### Simplified Pipeline Process Flow (text_based_agent.py)

This version follows steps 1, 4-6, and 8-9 from above, skipping the audio processing steps.

## Core Functions Explained

### 1. `initialize_clients()`

```python
def initialize_clients():
    """Initialize the API clients with their respective API keys."""
    global groq_client, elevenlabs_client
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
    
    groq_client = Groq(api_key=GROQ_API_KEY)
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    logger.info("API clients initialized successfully")
```

**Purpose:** Sets up the necessary API clients for Groq (for LLM and transcription) and ElevenLabs (for text-to-speech).
**Input:** Environment variables containing API keys
**Output:** Initialized global client objects
**Error Handling:** Validates API keys exist before attempting to create clients

### 2. `voice_to_text(file_name: str)`

```python
def voice_to_text(file_name: str) -> str:
    """
    Transcribes the audio file to text using Groq's Whisper-large-v3 model.
    
    Args:
        file_name: Path to the audio file
        
    Returns:
        Transcribed text from the audio file
    """
```

**Purpose:** Converts spoken audio into text using Groq's AI transcription service
**Input:** Path to an audio file
**Processing:** 
   - Validates file exists
   - Opens the file and sends to Groq's Whisper-large-v3 model
   - Processes the response
**Output:** Transcribed text string
**Error Handling:** Checks for file existence and handles API errors

### 3. `generate_search_terms(query: str)`

```python
def generate_search_terms(query: str) -> GovernmentTerm:
    """
    Generates an official government search term from the user's query using Groq's LLM.
    
    Args:
        query: The user's query text
        
    Returns:
        A string representing the government search term
    """
```

**Purpose:** Processes user input to extract optimal search terms for the government website
**Input:** User query text (either transcribed from audio or direct text input)
**Processing:**
   - Constructs a prompt for the LLM that asks it to extract relevant search terms
   - Sends the prompt to Groq's LLama-based model
   - Extracts and cleans the response
**Output:** Optimized search terms for the Irish government website
**Error Handling:** Has a fallback mechanism that extracts important words if the API call fails

### 4. `extract_content_from_links(query_word: str)`

```python
def extract_content_from_links(query_word: str) -> str:
    """
    Extracts content from relevant links on the Irish government website based on the search term.
    
    Args:
        query_word: The search term to use for finding relevant content
        
    Returns:
        A string containing the extracted content from relevant pages
    """
```

**Purpose:** Scrapes the Irish government website for information relevant to the search terms
**Input:** Search term(s) to query the website
**Processing:**
   - Constructs a search URL for the Irish government website
   - Sends a request and parses the results using BeautifulSoup
   - Extracts links from the top search results
   - For each link, uses Trafilatura to extract clean text content
   - Combines the content from multiple sources
**Output:** Cleaned and formatted content from relevant government pages
**Error Handling:** Handles cases where no results are found or content can't be extracted

### 5. `generate_response(conversation_history, extracted_content)`

```python
def generate_response(conversation_history: List[Dict[str, Any]], extracted_content: str) -> str:
    """
    Generates a response using Groq's LLM, considering the conversation history and extracted content.
    
    Args:
        conversation_history: List of conversation messages with 'role' and 'content' fields
        extracted_content: Content extracted from the Irish government website
        
    Returns:
        Generated response text
    """
```

**Purpose:** Uses AI to generate a contextually appropriate response based on the extracted content and conversation history
**Input:** 
   - Conversation history (list of previous messages)
   - Extracted content from the government website
**Processing:**
   - Constructs a detailed prompt with system instructions, conversation history, and extracted content
   - Sends the prompt to Groq's LLM (llama3-70b-8192 model)
   - Retrieves and processes the generated response
**Output:** AI-generated response text
**Error Handling:** Error handling for API calls and response processing

### 6. `text_to_voice(speech_file_path: str, text_to_convert: str)`

```python
def text_to_voice(speech_file_path: str, text_to_convert: str) -> str:
    """
    Converts the text to speech using ElevenLabs and saves it to the specified file path.
    
    Args:
        speech_file_path: Path where the generated audio will be saved
        text_to_convert: Text content to convert to speech
        
    Returns:
        Path to the generated audio file
    """
```

**Purpose:** Converts text responses to natural-sounding speech
**Input:**
   - Output path for the audio file
   - Text to convert to speech
**Processing:**
   - Sends the text to ElevenLabs API using the eleven_flash_v2_5 voice model
   - Receives audio data
   - Saves the audio data to the specified file
**Output:** Path to the saved audio file
**Error Handling:** Error handling for API calls and file writing operations

## Data Flow and Session Management

### Conversation History Structure

The conversation history is maintained as a list of dictionaries with the following structure:

```python
conversation_history = [
    {"role": "user", "content": "How do I apply for a passport?"},
    {"role": "assistant", "content": "To apply for an Irish passport, you need to..."}
]
```

This structure allows the system to:
1. Maintain context between multiple interactions
2. Send the full conversation history to the LLM for contextual responses
3. Support follow-up questions without repeating information

### Session Persistence

In the terminal-based applications, the conversation history exists for the duration of the program execution. When the program is restarted, a new conversation begins.

## Error Handling

The system implements comprehensive error handling at multiple levels:

1. **Input Validation**
   - Checks for valid audio file paths
   - Validates API keys exist before making calls

2. **API Error Handling**
   - Catches and logs specific API errors
   - Provides meaningful error messages to the user
   - Implements fallbacks where possible (e.g., for search term generation)

3. **Content Extraction Fallbacks**
   - Handles cases where website content cannot be scraped
   - Provides informative messages when no relevant content is found

4. **Graceful Error Reporting**
   - Logs detailed error information for debugging
   - Presents user-friendly error messages

## API Integration Details

### Groq API

The system integrates with two core capabilities of the Groq API:

1. **Audio Transcription**
   - Model: whisper-large-v3
   - Purpose: Convert audio to text
   - Implementation: `voice_to_text()` function

2. **Language Model**
   - Model: llama3-70b-8192
   - Purposes:
     - Generate search terms
     - Generate responses
   - Implementations: `generate_search_terms()` and `generate_response()` functions

### ElevenLabs API

The system uses ElevenLabs for text-to-speech conversion:

1. **Text-to-Speech**
   - Voice: Automatically selects the first available voice in your ElevenLabs account
   - Model: eleven_flash_v2
   - Purpose: Convert text responses to natural-sounding speech
   - Implementation: `text_to_voice()` function

## Sample Prompting Strategies

### Search Term Generation Prompt

```
Given the following user query, extract or generate 1-3 search keywords that would 
be most effective for searching the Irish government website (gov.ie). 

Focus on official terminology and specific services/departments that might be relevant.

User query: "{query}"

Return ONLY the keywords without any explanation, separated by commas if there are multiple.
```

### Response Generation System Prompt

```
You are an AI assistant specializing in providing information about Irish government services.
Your role is to provide helpful, accurate, and concise information based on the content extracted
from the official Irish government website (gov.ie).

When responding:
1. Base your answers on the extracted content provided
2. Be concise but thorough in your explanations
3. If the extracted content doesn't contain relevant information, be honest about the limitations
4. Maintain a helpful and professional tone throughout
5. Do not make up information - if something isn't in the extracted content, say so
6. Format your responses for clarity, using bullet points when appropriate

Remember: You're representing information from the Irish government website.
```

These carefully crafted prompts ensure the system generates appropriate and helpful responses based on authentic government information.