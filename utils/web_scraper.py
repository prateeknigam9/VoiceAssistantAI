import os
import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import trafilatura

logger = logging.getLogger(__name__)

def extract_content_from_links(query_word: str) -> str:
    """
    Extracts content from relevant links on the Irish government website based on the search term.
    
    Args:
        query_word: The search term to use for finding relevant content
        
    Returns:
        A string containing the extracted content from relevant pages
    """
    logger.debug(f"Extracting content for search term: {query_word}")
    
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
        logger.debug(f"Top result URLs: {top_result_urls}")
        
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
