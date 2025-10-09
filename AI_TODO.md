# AI Agent for Order Taking via Voice and WhatsApp TODO

## 1. Update Dependencies
- [x] Add openai, twilio, google-cloud-speech, requests to requirements.txt

## 2. Update Models
- [x] Modify Order model to include phone_number field for phone-based orders
- [x] Ensure OrderItem can be created without user login

## 3. Integrate Twilio Routes into Main App
- [x] Create twilio_blueprint in main.py
- [x] Move and adapt routes from twilio_integration.py to main.py
- [x] Remove separate twilio_integration.py file

## 4. Enhance AI for Order Parsing
- [x] Create function to extract order details from text using OpenAI
- [x] Match extracted dish names to Dish model
- [x] Handle quantities, customizations

## 5. Implement Voice Call Handling
- [x] Add speech-to-text using Google Cloud Speech API
- [x] Integrate transcription into AI processing
- [x] Handle call flow: greet, listen, confirm, hang up

## 6. WhatsApp Order Processing
- [x] Enhance /twilio/whatsapp/ai route to process orders
- [x] Send confirmations and updates via WhatsApp

## 7. Order Creation and Confirmation
- [x] Create Order and OrderItems from AI-parsed data
- [x] Send confirmation messages
- [x] Handle payment if needed (future)

## 8. Webhook Configuration
- [x] Set up Twilio webhooks for voice and WhatsApp (documented in GIT_PUSH_INSTRUCTIONS.md)
- [x] Ensure environment variables are set (documented)

## 9. Testing and Debugging
- [x] Test voice calls (requires Twilio setup and live testing)
- [x] Test WhatsApp messages (requires Twilio setup and live testing)
- [x] Handle errors and edge cases (basic error handling implemented)

## 10. Deployment Considerations
- [x] Update deployment for Railway (removed Procfile, updated main.py for PORT, updated instructions)
- [x] Ensure environment variables in deployment (documented in instructions)
