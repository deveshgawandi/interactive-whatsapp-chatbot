import requests
import json
import os
import mimetypes
import time
import threading
import io
from flask import Flask, request, jsonify
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors # Import the colors module

app = Flask(__name__)

# === Important: Replace these with your temporary values ===
ACCESS_TOKEN = "EAAYV8M0CTbABPqaWjgPYhu3k2GPXJ2vaNqbQOLPTZCQKW9K5F3UwllnTdUCZA6HkwbPPNhoex8Yd9ZBKqxK7XzmkUUpal68fYwi6peTpq4F6ezQFqYJMwEKrcJymsZBFgBpX2TGZBT7ZAxWDptsBWEGbBGmOnVmFqLOTTZAHr4jQpH2dDKdx6nvKNzvjuMijjWR2Yz6ducnoPBy0ZCSecNC6eVPdHWAsPAT9fKrfGl5A3MDHQAZDZD"
PHONE_NUMBER_ID = "734277263113504"
VERIFY_TOKEN = "my_secret_token"

# === IMPORTANT: Your public URLs and local templates are now organized here ===
PROJECT_DATA = {
    # We now point to the local template file for the brochure
    "brochure": "templates/brochure_template.pdf",
    "video": "https://youtu.be/tDhTko7x9V4",
    "floorplan": [
        "https://drive.google.com/uc?export=download&id=1W7kT9IhNb74-Dv-vNnFTlq_0uhTv839S",
        "https://drive.google.com/uc?export=download&id=1rfXWDW1r-JLaY5KRnmKErrAaU2HX66f",
        "https://drive.google.com/uc?export=download&id=1VfpoZxvSk5k8lfJW2dFzAwPGfkQzFtxL"
    ],
    "photos": [
        "https://drive.google.com/uc?export=download&id=1KMY7cky8iVjEmlM2-VakqGnembJc2ry0",
        "https://drive.google.com/uc?export=download&id=1-LM2AQLNEITdlum4OP6e9cGaznU48sIE",
        "https://drive.google.com/uc?export=download&id=1VN4Gs6j9F5sTKvCVmgQE6oV9pJqLqURB"
    ]
}

PROJECT_ASSETS = {
    "project_1": PROJECT_DATA, "project_2": PROJECT_DATA, "project_3": PROJECT_DATA,
    "project_4": PROJECT_DATA, "project_5": PROJECT_DATA,
}

def create_personalized_pdf(template_path, user_name, user_phone):
    """Creates a personalized PDF by stamping user details onto a template."""
    try:
        # Create a new PDF in memory with the user's details (the "watermark")
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # --- EDITED SECTION: Font, Size, Color, and Position ---
        # Set a new font color, font, and a larger size
        can.setFillColor(colors.darkblue) # Change font color to dark blue
        can.setFont("Helvetica-Bold", 16)
        
        # Center the text horizontally, 0.75 inches from the bottom
        page_width = letter[0]
        can.drawCentredString(page_width / 2, 0.75 * inch, f"Specially Prepared For: {user_name} ({user_phone})")
        # --- END EDITED SECTION ---

        can.save()
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        
        # Read the existing template PDF
        template_pdf = PdfReader(open(template_path, "rb"))
        output = PdfWriter()
        
        # Merge the watermark onto the first page of the template
        first_page = template_pdf.pages[0]
        first_page.merge_page(watermark_pdf.pages[0])
        output.add_page(first_page)
        
        # Add the rest of the pages from the template
        for i in range(1, len(template_pdf.pages)):
            output.add_page(template_pdf.pages[i])
            
        # Create a temporary filename for the output
        output_filename = f"temp_{user_phone}_brochure.pdf"
        with open(output_filename, "wb") as output_stream:
            output.write(output_stream)
            
        print(f"Personalized PDF created: {output_filename}")
        return output_filename
    except Exception as e:
        print(f"Error creating personalized PDF: {e}")
        return None

def send_whatsapp_message(data):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message sent successfully!")
        return response.json()
    else:
        print(f"Error sending message: {response.status_code}")
        print(f"Meta's Error Response: {response.text}")
        return None

def upload_media(file_path_or_url, media_type, is_local=False):
    """Uploads a local file or a file from a URL to get a media ID."""
    try:
        if is_local:
            file_name = os.path.basename(file_path_or_url)
            content_type, _ = mimetypes.guess_type(file_path_or_url)
            if content_type is None:
                content_type = 'application/pdf'
            with open(file_path_or_url, 'rb') as f:
                file_content = f.read()
        else: # Download from URL
            response = requests.get(file_path_or_url, stream=True)
            response.raise_for_status()
            content_type, _ = mimetypes.guess_type(file_path_or_url)
            if content_type is None:
                content_type = 'application/pdf'
            file_name = os.path.basename(file_path_or_url)
            file_content = response.content

        upload_url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/media"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        files = {
            'file': (file_name, file_content, content_type),
            'type': (None, media_type),
            'messaging_product': (None, 'whatsapp'),
        }
        upload_response = requests.post(upload_url, headers=headers, files=files)
        upload_response.raise_for_status()
        media_id = upload_response.json().get('id')
        print(f"File uploaded successfully. Media ID: {media_id}")
        return media_id
    except requests.exceptions.RequestException as e:
        print(f"Error during media upload: {e}")
        if 'upload_response' in locals() and upload_response.text:
            print(f"Meta's Upload Error Response: {upload_response.text}")
        return None

def send_media_message(to, media_id, media_type, caption="", filename=""):
    payload = {"id": media_id, "caption": caption}
    if media_type == "document" and filename:
        payload["filename"] = filename
    data = {"messaging_product": "whatsapp", "to": to, "type": media_type, media_type: payload}
    send_whatsapp_message(data)

def send_files_in_background(from_number, user_name, action, assets_to_send):
    """Runs in a background thread to send files, now with personalization."""
    print(f"BACKGROUND TASK: Starting for action '{action}' for user {user_name}.")
    
    if action == 'brochure':
        # Create the personalized brochure
        personalized_pdf_path = create_personalized_pdf(assets_to_send[0], user_name, from_number)
        if personalized_pdf_path:
            media_id = upload_media(personalized_pdf_path, 'document', is_local=True)
            if media_id:
                send_media_message(from_number, media_id, 'document', filename=f"{user_name}_brochure.pdf")
            os.remove(personalized_pdf_path) # Clean up the temporary file
    else:
        # Handle other files (floorplan, photos) as before
        media_type = 'document'
        for i, url in enumerate(assets_to_send):
            media_id = upload_media(url, media_type, is_local=False)
            if media_id:
                filename = f"{action}_{i+1}.pdf"
                send_media_message(from_number, media_id, media_type, filename=filename)
                time.sleep(2)
    print("BACKGROUND TASK: Finished.")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        else:
            return "Error, wrong validation token", 403

    if request.method == 'POST':
        data = request.get_json()
        
        if (data.get("entry") and data["entry"][0].get("changes") and
                data["entry"][0]["changes"][0].get("value") and
                data["entry"][0]["changes"][0].get("value").get("messages")):
            
            try:
                value = data['entry'][0]['changes'][0]['value']
                message_info = value['messages'][0]
                from_number = message_info['from']
                message_type = message_info.get('type')
                user_name = value.get('contacts', [{}])[0].get('profile', {}).get('name', 'Valued Customer')

                if message_type == 'text':
                    response_data = {
                        "messaging_product": "whatsapp", "to": from_number, "type": "interactive",
                        "interactive": {"type": "list", "body": {"text": "welcome to mybusiness realtors\nPlease select a project from the list below:"},
                            "action": {"button": "Select a Project", "sections": [{"title": "Our Projects", "rows": [
                                            {"id": "project_1", "title": "Project 1"}, {"id": "project_2", "title": "Project 2"},
                                            {"id": "project_3", "title": "Project 3"}, {"id": "project_4", "title": "Project 4"},
                                            {"id": "project_5", "title": "Project 5"}]}]}}}
                    send_whatsapp_message(response_data)

                elif message_type == 'interactive':
                    interactive_data = message_info.get('interactive')
                    if interactive_data.get('type') == 'list_reply':
                        list_reply_id = interactive_data['list_reply']['id']
                        
                        if list_reply_id in PROJECT_ASSETS:
                            project_title = interactive_data['list_reply']['title']
                            response_data = {
                                "messaging_product": "whatsapp", "to": from_number, "type": "interactive",
                                "interactive": {"type": "list", "body": {"text": f"Welcome to {project_title}\n\nYour personalised marketing collaterals are ready. Select from the list below:"},
                                    "action": {"button": "Select an Option", "sections": [{"title": project_title, "rows": [
                                                {"id": f"{list_reply_id}_brochure", "title": "Brochure"},
                                                {"id": f"{list_reply_id}_video", "title": "See your future home"},
                                                {"id": f"{list_reply_id}_floorplan", "title": "Floor Plans"},
                                                {"id": f"{list_reply_id}_photos", "title": "Site Photographs"},
                                                {"id": f"{list_reply_id}_assistant", "title": "Chat with Assistant"}
                                            ]}]}}}
                            send_whatsapp_message(response_data)
                        else: 
                            project_id, action = list_reply_id.rsplit('_', 1)

                            if project_id in PROJECT_ASSETS:
                                if action == 'assistant':
                                    msg_data = {"messaging_product": "whatsapp", "to": from_number, "type": "text", "text": {"body": "Thank you! Our personal assistant has been notified and will contact you on this number shortly."}}
                                    send_whatsapp_message(msg_data)
                                
                                asset_data = PROJECT_ASSETS[project_id].get(action)
                                if not asset_data:
                                    msg_data = {"messaging_product": "whatsapp", "to": from_number, "type": "text", "text": {"body": "Sorry, that asset is not available yet."}}
                                    send_whatsapp_message(msg_data)
                                
                                elif action == 'video':
                                    msg_data = {"messaging_product": "whatsapp", "to": from_number, "type": "text", "text": {"body": f"Here is the link to the video:\n{asset_data}"}}
                                    send_whatsapp_message(msg_data)
                                else: 
                                    assets_to_send = asset_data if isinstance(asset_data, list) else [asset_data]
                                    thread = threading.Thread(target=send_files_in_background, args=(from_number, user_name, action, assets_to_send))
                                    thread.start()

            except (KeyError, IndexError, TypeError) as e:
                print(f"Error parsing user message: {e}")
        else:
            pass
            
        return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

