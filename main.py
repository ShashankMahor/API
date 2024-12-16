from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os

app = Flask(__name__)

# Sender Mail Credentials (Primary email for SMTP authentication)
EMAIL_ADDRESS = "sam.daniels@ontimehire.com"
EMAIL_PASSWORD = "ceeoxqobqxvampoj"

# Alias email address (already configured in Gmail account)
ALIAS_EMAIL = "Sam.daniels@qualitytalentgroup.com"

# Root endpoint
@app.route('/', methods=['POST'])
def home():
    return "POST request received at the root endpoint."

@app.route('/send-email', methods=['POST'])
def send_email():
    print("POST request received at /send-email")
    try:
        # Parse JSON data from the request
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON payload."}), 401

        # Extract email details from the payload
        receiver_email = data.get('receiver_email')
        subject = data.get('subject')
        body = data.get('body')

        # Validate required fields
        if not receiver_email or not subject or not body:
            return jsonify({"error": "Missing required fields: receiver_email, subject, or body."}), 402

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, receiver_email):
            return jsonify({"error": "Invalid email format."}), 403

        # Setup the email message
        message = MIMEMultipart()
        # Use alias email as the sender
        message['From'] = ALIAS_EMAIL
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Connecting with the email server (To send the Mail)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Authenticate using primary credentials
            server.send_message(message)  # Send message with alias as 'From'

        return jsonify({"message": "Email sent successfully using alias!"}), 200

    except smtplib.SMTPAuthenticationError:
        return jsonify({"error": "Failed to authenticate with the SMTP server."}), 300
    except smtplib.SMTPConnectError:
        return jsonify({"error": "Failed to connect to the SMTP server."}), 350
    except smtplib.SMTPRecipientsRefused:
        return jsonify({"error": "Recipient email address was refused."}), 400
    except smtplib.SMTPException as e:
        return jsonify({"error": f"SMTP error occurred: {str(e)}"}), 450
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
