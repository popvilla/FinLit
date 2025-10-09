import os
from openai import OpenAI
from uuid import UUID
from typing import List, Dict

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chatbot_response(query: str, user_id: UUID, conversation_history: List[Dict] = None) -> str:
    """Generates a response from the AI chatbot."""
    if conversation_history is None:
        conversation_history = []

    # Add system message to set the context for the chatbot
    messages = [
        {"role": "system", "content": "You are FinLit, a friendly and knowledgeable financial literacy assistant. Provide helpful, educational, and neutral financial information. Do not give direct investment advice."},
    ]

    # Add previous conversation history
    messages.extend(conversation_history)
    
    # Add the current user query
    messages.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or gpt-4, depending on availability and cost
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."

# Example usage (for testing)
if __name__ == "__main__":
    sample_user_id = UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef') # Replace with a real UUID
    print("Chatbot response:", get_chatbot_response("What is diversification?", sample_user_id))
    print("Chatbot response:", get_chatbot_response("Explain compound interest.", sample_user_id))
