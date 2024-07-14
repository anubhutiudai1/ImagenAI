from flask import Flask, render_template, request, jsonify
import google.auth
from google.auth import compute_engine
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import google.generativeai as genai
import os 
import requests
import json

#@title Authenticate with Google Cloud and your project ID

import vertexai
from vertexai.preview.vision_models import Image, ImageGenerationModel
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./credentials.json"
app = Flask(__name__)

# Load service account credentials
credentials = google.auth.load_credentials_from_file("credentials.json")
scoped_credentials = compute_engine.Credentials(credentials)

@app.route("/", methods=["GET", "POST"])
def index():
    images = None
    if request.method == "POST":
        description = request.form.get("description")

        if description:
            
            images = generate_image_with_gemini()

    return render_template("index.html", images=images)

@app.route("/generate", methods=["POST"])
def generate_image_with_gemini():
    vertexai.init(project="lively-nimbus-427218-d4", location="us-central1")
    # @title Use Gemini to generate an image prompt for your item

    data = request.get_json()
    description = data['description']
    item_selling = description

    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])

    prompttext = f"""
    I need to generate an image of {item_selling}. 
    I need the image to be compelling and interesting.
    Can you create a prompt I can use to generate an image of {item_selling} with Vertex?
    Respond with only the prompt, no other text. Be as verbose as possible.
    """

    response = chat.send_message(prompttext)
    #@title Use Vertex to generate an image

    from IPython.display import Image

    model = ImageGenerationModel.from_pretrained("imagegeneration@005")
    images = model.generate_images(prompt=response.text)

    images[0].save(location="static/gen-img1.png", include_generation_parameters=True)

    return json.dumps('static/gen-img1.png')

if __name__ == "__main__":
    app.run(debug=True)