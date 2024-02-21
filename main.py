# combined_linebot.py
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage,
)
from line_bot_base import LineBot  # Assuming you have a file named line_bot_base.py
import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables from .env file
script_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_directory, '.env')
load_dotenv(dotenv_path)

# Load LINE Bot credentials from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')
modelv = genai.GenerativeModel('gemini-pro-vision')

class CombinedLineBot(LineBot):
    def handle_text_message(self, event):
        user_message = "(zh-tw) {}".format(event.message.text)
        response = model.start_chat().send_message(user_message)
        reply_text = response.text

        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text),
        )

    def handle_image_message(self, event):
        message_content = self.line_bot_api.get_message_content(event.message.id)
        image_data = message_content.content
        try:
            img = Image.open(BytesIO(image_data))
        except Exception as e:
            print(f"Error processing image: {e}")
        response = modelv.generate_content(["Use traditional Chinese to describe the content based on this image", img], stream=True)
        response.resolve()            
        reply_text = response.text

        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text),
        )

if __name__ == "__main__":
    bot = CombinedLineBot(ACCESS_TOKEN, CHANNEL_SECRET)
    app = bot.create_app()
    app.run()
