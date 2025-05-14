#!/usr/bin/env python3
"""
Irish Government Text-Based Agent

This script implements a text-based version of the voice agent pipeline that:
1. Takes a text question instead of audio
2. Generates search terms for the Irish government website
3. Extracts relevant content from the website
4. Generates a response using Groq's LLM
5. Outputs the text response (skips the text-to-speech conversion)
"""

import os
import logging
from typing import List, Dict, Any
import time
from dotenv import load_dotenv
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API credentials
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize clients
groq_client = None


def initialize_clients():
    """Initialize the API clients with their respective API keys."""
    global groq_client
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("API clients initialized successfully")


class GovernmentTerm(str):
    """A string type representing an official government search term."""
    pass


def generate_search_terms(query: str) -> GovernmentTerm:
    """
    Generates an official government search term from the user's query using Groq's LLM.
    
    Args:
        query: The user's query text
        
    Returns:
        A string representing the government search term
    """
    logger.info(f"Generating search term for query: {query}")
    
    try:
        # Construct the prompt for the LLM
        prompt = f"""
        Given the following user query, extract or generate 1-3 search keywords that would 
        be most effective for searching the Irish government website (gov.ie). 
        
        Focus on official terminology and specific services/departments that might be relevant.
        
        User query: "{query}"
        
        Return ONLY the keywords without any explanation, separated by commas if there are multiple.
        """
        
        # Call the LLM to generate search terms
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts relevant government search terms from user queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=50
        )
        
        # Extract the search term from the response
        search_term = response.choices[0].message.content.strip()
        
        # Clean up the response to ensure it's just the search terms
        search_term = search_term.replace(".", "").replace("\"", "").strip()
        
        logger.info(f"Generated search term: {search_term}")
        return search_term
    
    except Exception as e:
        logger.error(f"Error generating search term: {str(e)}")
        # Fallback to a simpler approach if the LLM call fails
        words = query.split()
        important_words = [word for word in words if len(word) > 3]
        fallback_term = " ".join(important_words[:3]) if important_words else query
        
        logger.info(f"Using fallback search term: {fallback_term}")
        return fallback_term


def extract_content_from_links(query_word: str) -> str:
    """
    Extracts content from relevant links on the Irish government website based on the search term.
    
    Args:
        query_word: The search term to use for finding relevant content
        
    Returns:
        A string containing the extracted content from relevant pages
    """
    import requests
    from urllib.parse import urljoin
    from bs4 import BeautifulSoup
    import trafilatura
    
    logger.info(f"Extracting content for search term: {query_word}")
    
    BASE_URL = "https://www.gov.ie"
    SEARCH_URL = f"{BASE_URL}/search/?term={query_word}"
    
    try:
        # Send a request to the search page
        response = requests.get(SEARCH_URL)
        response.raise_for_status()
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all search result links
        search_results = soup.select('.search-results-item a')
        
        if not search_results:
            logger.warning(f"No search results found for term: {query_word}")
            return f"No relevant information found on the Irish government website for '{query_word}'."
        
        # Get the URLs of the top 3 results (or fewer if there are less than 3)
        top_result_urls = [urljoin(BASE_URL, link.get('href')) for link in search_results[:3]]
        logger.info(f"Top result URLs: {top_result_urls}")
        
        # Extract content from each URL
        all_content = []
        for url in top_result_urls:
            try:
                # Use trafilatura to extract clean text from the webpage
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    text = trafilatura.extract(downloaded)
                    if text:
                        # Add source URL reference and the extracted text
                        all_content.append(f"Source: {url}\n\n{text}")
            except Exception as e:
                logger.error(f"Error extracting content from {url}: {str(e)}")
        
        if not all_content:
            return f"Found links related to '{query_word}' on the Irish government website, but could not extract readable content."
        
        # Combine all extracted content
        combined_content = "\n\n---\n\n".join(all_content)
        
        # Truncate if too long (to avoid exceeding token limits)
        if len(combined_content) > 10000:
            combined_content = combined_content[:10000] + "...(content truncated)"
        
        return combined_content
    
    except requests.RequestException as e:
        logger.error(f"Request error when accessing {SEARCH_URL}: {str(e)}")
        return f"Could not access the Irish government website to search for '{query_word}'. Error: {str(e)}"
    
    except Exception as e:
        logger.error(f"Unexpected error in extract_content_from_links: {str(e)}")
        return f"An error occurred while trying to extract information about '{query_word}' from the Irish government website."


def generate_response(conversation_history: List[Dict[str, Any]], extracted_content: str) -> str:
    """
    Generates a response using Groq's LLM, considering the conversation history and extracted content.
    
    Args:
        conversation_history: List of conversation messages with 'role' and 'content' fields
        extracted_content: Content extracted from the Irish government website
        
    Returns:
        Generated response text
    """
    logger.info("Generating response from LLM")
    
    try:
        # Prepare conversation history in the format expected by the API
        messages = []
        
        # Add system message with context and instructions
        system_message = """
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
        """
        
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        for message in conversation_history:
            if message.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        # Add the extracted content as a system message before the final response
        if extracted_content:
            content_message = f"""
            Based on the user's query, I've extracted the following information from the Irish government website:
            
            {extracted_content}
            
            Please use this information to answer the user's latest question. If the information doesn't fully address their query, acknowledge the limitations while being as helpful as possible.
            """
            
            messages.append({"role": "system", "content": content_message})
        
        # Generate response using Groq's LLM
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the generated text from the response
        generated_text = response.choices[0].message.content
        
        return generated_text
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise Exception(f"Response generation failed: {str(e)}")


def main():
    """Main function to run the text-based agent."""
    try:
        # Initialize API clients
        initialize_clients()
        
        # Initialize conversation history
        conversation_history = []
        
        print("\n" + "="*80)
        print("  IRISH GOVERNMENT TEXT AGENT".center(80))
        print("="*80)
        print("\nThis program answers questions about Irish government services.")
        print("It searches for relevant information on the official government website and generates responses.")
        print("\nType 'quit' to exit the program at any time.")
        print("="*80 + "\n")
        
        # Main loop
        while True:
            # Get user input
            print("\nPlease enter your question about Irish government services:")
            user_query = input("> ").strip()
            
            # Check if user wants to quit
            if user_query.lower() == 'quit':
                print("\nThank you for using the Irish Government Text Agent. Goodbye!")
                break
            
            # Processing stages with progress indicators
            try:
                # Add user message to conversation history
                conversation_history.append({
                    "role": "user", 
                    "content": user_query
                })
                
                print("\n[1/3] Generating search terms...")
                search_term = generate_search_terms(user_query)
                print(f"  Search term: \"{search_term}\"")
                
                print("\n[2/3] Extracting content from Irish government website...")
                extracted_content = extract_content_from_links(search_term)
                print(f"  Found information from {extracted_content.count('Source:') or 0} sources")
                
                print("\n[3/3] Generating response...")
                response_text = generate_response(conversation_history, extracted_content)
                
                # Add assistant response to conversation history
                conversation_history.append({
                    "role": "assistant", 
                    "content": response_text
                })
                
                print("\n" + "-"*80)
                print("RESPONSE:")
                print("-"*80)
                print(response_text)
                print("-"*80)
                
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again with another question or check your API keys.")
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")


if __name__ == "__main__":
    main()