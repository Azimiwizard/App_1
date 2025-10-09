from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import openai
import requests

app = Flask(__name__)

# Twilio credentials (set as environment variables)
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token)

# OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# n8n webhook URL
n8n_webhook_url = os.environ.get('N8N_WEBHOOK_URL')


@app.route('/twilio/voice', methods=['POST'])
def twilio_voice():
    response = VoiceResponse()
    # Basic voice response, can be extended with AI integration
    response.say(
        "Hello, thank you for calling Stitch Menu. How can I assist you today?")
    return str(response)


@app.route('/twilio/voice/webhook', methods=['POST'])
def twilio_voice_webhook():
    # Webhook to receive call status and events from Twilio Programmable Voice
    call_sid = request.values.get('CallSid')
    call_status = request.values.get('CallStatus')
    # Process call events here or forward to n8n webhook
    print(f"Call SID: {call_sid}, Status: {call_status}")
    return ('', 204)


@app.route('/twilio/whatsapp', methods=['POST'])
def twilio_whatsapp():
    incoming_msg = request.values.get('Body', '').lower()
    response = MessagingResponse()
    msg = response.message()
    msg.body("Hello from Stitch Menu WhatsApp bot! How can I help you?")
    # Further WhatsApp chat logic with AI integration to be added
    return str(response)


@app.route('/twilio/whatsapp/webhook', methods=['POST'])
def twilio_whatsapp_webhook():
    # Webhook to receive WhatsApp message status and events
    message_sid = request.values.get('MessageSid')
    message_status = request.values.get('MessageStatus')
    # Process message events here or forward to n8n webhook
    print(f"Message SID: {message_sid}, Status: {message_status}")
    return ('', 204)


@app.route('/twilio/whatsapp/ai', methods=['POST'])
def twilio_whatsapp_ai():
    incoming_msg = request.values.get('Body', '')
    from_number = request.values.get('From', '')

    # Use OpenAI to process the message and generate a response
    try:
        ai_response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Customer message: {incoming_msg}\n\nRespond as a helpful restaurant assistant for Stitch Menu:",
            max_tokens=150,
            temperature=0.7
        )
        response_text = ai_response.choices[0].text.strip()
    except Exception as e:
        response_text = "I'm sorry, I'm having trouble processing your request. Please try again later."

    # Send response via WhatsApp
    twilio_client.messages.create(
        body=response_text,
        from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
        to=from_number
    )

    # Forward order data to n8n if it's an order
    if 'order' in incoming_msg.lower():
        order_data = {
            'customer_number': from_number,
            'message': incoming_msg,
            'ai_response': response_text
        }
        try:
            requests.post(n8n_webhook_url, json=order_data)
        except Exception as e:
            print(f"Failed to send to n8n: {e}")

    return ('', 204)


if __name__ == '__main__':
    app.run(port=5001)
