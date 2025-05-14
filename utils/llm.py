import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def generate_response(conversation_history: List[Dict[str, Any]], extracted_content: str, client) -> str:
    """
    Generates a response using Groq's LLM, considering the conversation history and extracted content.
    
    Args:
        conversation_history: List of conversation messages with 'role' and 'content' fields
        extracted_content: Content extracted from the Irish government website
        client: Initialized Groq client
        
    Returns:
        Generated response text
    """
    logger.debug("Generating response from LLM")
    
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
        
        # Add conversation history (exclude timestamps if present)
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
        response = client.chat.completions.create(
            model="llama-3.3-70b",
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
