Python WhatsApp Chatbot with Dynamic PDFs
A sophisticated, interactive WhatsApp chatbot built with Python and the Flask Framework, designed for businesses to automate customer interactions and deliver personalized marketing materials directly through the Meta (Facebook) Graph API.

The standout feature of this bot is its ability to dynamically generate personalized PDF documents on the fly, stamping the user's name and phone number onto a template before sending it.

Live Demo
(This is a great place to add a GIF or short video of your chatbot in action!)

Key Features
Interactive UI: Utilizes WhatsApp's native List Messages for a clean, user-friendly, multi-step conversation flow.

Dynamic PDF Personalization: On request, the bot merges a user's details (name and phone number) onto a master PDF template, creating a personalized copy for each lead.

Multi-Media Support: Seamlessly sends various media types, including documents (PDFs) and links to videos.

Asynchronous File Handling: Employs background threading to manage time-consuming tasks like uploading and sending multiple files. This ensures the main server responds instantly to Meta's webhooks, preventing timeouts and repeated actions.

Lead Generation Funnel: Includes a "Chat with Assistant" option to capture user interest and provide a clear handoff point from the bot to a human agent.

Scalable Content Structure: Project assets (links, filenames) are organized in a Python dictionary, making it easy to add or update content for new products or properties without changing the core logic.

Technical Stack
Backend: Python with the Flask Framework

WhatsApp Integration: Meta (Facebook) Graph API

PDF Manipulation: PyPDF2 (for merging) and ReportLab (for creating the text layer)

Local Development Tunneling: ngrok

Workflow
The chatbot operates on a webhook-based architecture. The flow of information is as follows:

User -> WhatsApp: The user sends a message to the bot's number.

WhatsApp -> Meta API: WhatsApp routes the message to the Meta servers.

Meta API -> ngrok -> Flask Server: Meta sends a JSON payload to the registered public webhook URL (provided by ngrok), which securely tunnels the request to the local Flask server.

Flask Server (app.py): The Python application parses the JSON payload, understands the user's intent (e.g., selected "Project 1"), and executes the corresponding logic.

Flask Server -> Meta API: The bot makes a POST request back to the Meta Graph API, instructing it to send a reply (text, interactive list, or media).

Meta API -> WhatsApp -> User: Meta delivers the bot's message back to the user on WhatsApp.

Setup and Configuration
Clone the Repository:

git clone [https://github.com/deveshgawandi/interactive-whatsapp-chatbot.git](https://github.com/deveshgawandi/interactive-whatsapp-chatbot.git)
cd interactive-whatsapp-chatbot

Create and Activate a Virtual Environment:

python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

Install Dependencies:

pip install -r requirements.txt

Set Up Environment Variables (Crucial for Security):
This project requires three secret keys from your Meta Developer App Dashboard. Never hardcode them in your code. Set them as environment variables in your terminal before running the app.

On Windows (PowerShell):

$env:ACCESS_TOKEN="YOUR_WHATSAPP_ACCESS_TOKEN"
$env:PHONE_NUMBER_ID="YOUR_WHATSAPP_PHONE_NUMBER_ID"
$env:VERIFY_TOKEN="YOUR_CHOSEN_VERIFY_TOKEN"

Add Your Brochure Template:
Place your master brochure file inside the /templates folder and ensure it is named brochure_template.pdf.

Run the Flask Application:

python app.py

Expose Your Local Server with ngrok:
In a separate terminal, run:

ngrok http 5000
