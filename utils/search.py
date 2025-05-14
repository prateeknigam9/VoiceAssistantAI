import logging
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GovernmentTerm(str):
    """
    A string type representing an official government search term.
    """
    pass

def generate_search_terms(query: str, client) -> str:
    """
    Generates an official government search term from the user's query using Groq's LLM.
    
    Args:
        query: The user's query text
        client: Initialized Groq client
        
    Returns:
        A string representing the government search term
    """
    logger.debug(f"Generating search term for query: {query}")
    
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
        response = client.chat.completions.create(
            model="llama-3.3-70b",
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
        
        logger.debug(f"Generated search term: {search_term}")
        return search_term
    
    except Exception as e:
        logger.error(f"Error generating search term: {str(e)}")
        # Fallback to a simpler approach if the LLM call fails
        words = query.split()
        important_words = [word for word in words if len(word) > 3]
        fallback_term = " ".join(important_words[:3]) if important_words else query
        
        logger.debug(f"Using fallback search term: {fallback_term}")
        return fallback_term
