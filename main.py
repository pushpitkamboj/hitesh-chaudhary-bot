from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from openai import OpenAI
from dotenv import load_dotenv
import os
import random
import sys

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Twilio client
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Hitesh catchphrases for added authenticity
def get_hitesh_catchphrase():
    catchphrases = [
        "Chai aur code!",
        "Toh chaliye shuru karte hain",
        "Toh simple hai",
        "Bahut badhiya!",
        "Thoda sa time lagega, but ho jayega",
        "Seedhi baat, no bakwaas!",
        "Aap logon ka support chahiye!",
        "Bilkul simple hai",
        "Haanji"
    ]
    return random.choice(catchphrases)

def chat_with_gpt(user_question, system_prompt, model="gpt-4o"):
    messages = []
    
    # Add system prompt if provided
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Add user message
    messages.append({"role": "user", "content": user_question})
    
    # Call the API
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )
    
    return completion.choices[0].message.content

# Define a system prompt to mimic Hitesh Choudhary's style
system_prompt = """You are Hitesh Choudhary, a popular Indian coding instructor, YouTuber, and tech entrepreneur.
Respond exactly as Hitesh would, using his unique teaching style and personality.

PERSONALITY TRAITS TO INCORPORATE:
1. Friendly and approachable - use phrases like "Haanji" and "bilkul simple hai"
2. Straightforward - "ye toh chai peete peete ho jaega"
3. Encouraging - focus on building confidence in beginners
4. Practical - emphasize real-world applications over theory
5. Code-focused - always try to explain with code examples when relevant
6. Mix Hindi and English words naturally (Hinglish)

SPEAKING STYLE:
1. Use short, direct sentences
2. Occasionally use Hindi expressions like "chaliye shuru karte hain" or "bilkul simple hai"
3. Address the user as if speaking to them in a YouTube video
4. Start or end responses occasionally with catchphrases like "chai peete rhiye aur code krte rhiye" or "toh kaise ho"
5. Be enthusiastic about technology, especially JavaScript, web development, and blockchain
6. speak 70%hindi and 30% english
7. Use emojis to make it more engaging

KNOWLEDGE AREAS:
- JavaScript, TypeScript, and modern web frameworks
- Full-stack development (MERN stack)
- Python programming
- App development
- Blockchain technology
- Career advice for developers
- Tech industry trends

Keep explanations practical, code-focused, and beginner-friendly, just like Hitesh does in his videos.
IMPORTANT: Keep responses short and concise for WhatsApp format.
"""

@app.route("/", methods=['GET'])
def home():
    return "Hitesh Choudhary WhatsApp Bot is running! 🚀 Webhook is at /webhook"

@app.route("/webhook", methods=['POST'])
def webhook():
    # Get the message the user sent to our WhatsApp number
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    # Create a response object
    resp = MessagingResponse()
    msg = resp.message()
    
    # Check if it's a first-time user (the message contains "join")
    if "join" in incoming_msg.lower():
        welcome_message = "🎉 Aur bhai log! Welcome to Hitesh Choudhary's WhatsApp bot! 🚀\n\nAap kuch bhi puch sakte hai coding, programming, ya career advice ke baare mein. Main aapki help karunga, bilkul Hitesh bhai jaise! 😊\n\nChalo shuru karte hai! ☕"
        msg.body(welcome_message)
        return str(resp)
    
    # Generate a response using our Hitesh chatbot
    response = chat_with_gpt(incoming_msg, system_prompt)
    
    # Add a catchphrase occasionally (30% chance)
    if random.random() < 0.3:
        response = response + "\n\n" + get_hitesh_catchphrase()
      # Send the response back to the user
    msg.body(response)
    
    return str(resp)

if __name__ == "__main__":
    # Check if we're running on Render or locally
    is_render = "RENDER" in os.environ
    
    if not is_render:
        # Running locally - use ngrok
        try:
            from pyngrok import ngrok
            
            # Configure ngrok
            ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
            if ngrok_auth_token:
                ngrok.set_auth_token(ngrok_auth_token)
            
            # Start ngrok tunnel
            public_url = ngrok.connect(5000).public_url
            print(f"Ngrok tunnel established at: {public_url}")
              
            # Instructions for setting up WhatsApp Sandbox
            if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
                try:
                    print("\n=== WhatsApp Sandbox Setup Instructions ===")
                    print("1. Go to https://console.twilio.com/")
                    print("2. Navigate to 'Messaging' → 'Try it out' → 'Send a WhatsApp message'")
                    print("3. In the WhatsApp Sandbox settings, set the following:")
                    print(f"   - WHEN A MESSAGE COMES IN: {public_url}/webhook")
                    print("   - Make sure HTTP POST is selected")
                    print("4. Send the join code from Twilio to the WhatsApp sandbox number")
                    print("   (Usually something like 'join <two-words>')")
                    print("5. Once connected, any message you send will be processed by your Hitesh Choudhary AI")
                    print(f"\nYour webhook URL is ready: {public_url}/webhook")
                except Exception as e:
                    print(f"Error: {e}")
                    print(f"Please manually update your Twilio WhatsApp Sandbox webhook URL to: {public_url}/webhook")
            else:
                print("Twilio credentials not found in .env file.")
                print(f"Please manually update your Twilio webhook URL to: {public_url}/webhook")
        except ImportError:
            print("Ngrok not installed. Running in local mode only.")
            print("Install pyngrok for public URL tunneling: pip install pyngrok")
    else:
        # Running on Render - show deployment info
        render_url = os.environ.get("RENDER_EXTERNAL_URL", "your-render-url")
        print(f"Running on Render at {render_url}")
        print(f"Set your Twilio webhook to {render_url}/webhook")
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=port)
