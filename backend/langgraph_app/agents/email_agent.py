import os
import smtplib
from email.message import EmailMessage
from xhtml2pdf import pisa
from io import BytesIO
import markdown

from langgraph_app.state import TripState

def email_node(state: TripState) -> TripState:
    email_address = state.get("email")
    if not email_address:
        return {"assistant_response": "I'm sorry, I don't have your registered email address.", "email_sent": False}

    itinerary_text = state.get("itinerary_message") or state.get("itinerary") or "No itinerary available."
    html_itinerary = markdown.markdown(itinerary_text)
    
    weather_text = state.get("weather_message", "")
    routes_text = state.get("routes_message", "")
    activities_text = state.get("activities_message", "")
    accommodation_text = state.get("accommodation_message", "")
    
    extra_content = ""
    if weather_text:
        extra_content += "<h2 class='section-title'>Weather Forecast</h2>" + markdown.markdown(weather_text)
    if routes_text:
        extra_content += "<h2 class='section-title'>Transport & Routes</h2>" + markdown.markdown(routes_text)
    if accommodation_text:
        extra_content += "<h2 class='section-title'>Accommodation Options</h2>" + markdown.markdown(accommodation_text)
    if activities_text:
        extra_content += "<h2 class='section-title'>Activities & Sightseeing</h2>" + markdown.markdown(activities_text)
    
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: a4 portrait;
                margin: 2cm;
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333333;
                line-height: 1.6;
                font-size: 13px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 26px;
                margin: 0;
            }}
            h2 {{
                color: #2980b9;
                font-size: 18px;
                border-bottom: 1px solid #ecf0f1;
                padding-bottom: 5px;
                margin-top: 25px;
                margin-bottom: 10px;
            }}
            .section-title {{
                color: #e67e22; /* different color for research sections */
            }}
            h3 {{
                color: #34495e;
                font-size: 15px;
                margin-top: 15px;
                margin-bottom: 5px;
            }}
            .summary-box {{
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin-bottom: 25px;
            }}
            .summary-box p {{
                margin: 5px 0;
                font-size: 14px;
            }}
            .content, .extra-content {{
                margin-top: 10px;
            }}
            ul, ol {{
                margin-top: 5px;
                margin-bottom: 15px;
                padding-left: 25px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            strong {{
                color: #2c3e50;
            }}
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Your Trip Itinerary</h1>
        </div>
        
        <div class="summary-box">
            <p><strong>From:</strong> {state.get("source", "N/A")}</p>
            <p><strong>To:</strong> {state.get("destination", "N/A")}</p>
            <p><strong>Dates:</strong> {state.get("start_date", "N/A")} to {state.get("end_date", "N/A")}</p>
        </div>
        
        <div class="content">
            {html_itinerary}
        </div>
        
        <!-- Only add a page break if there is extra content -->
        {'<div class="page-break"></div>' if extra_content else ''}
        
        <div class="extra-content">
            {extra_content}
        </div>
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if pisa_status.err:
        return {"assistant_response": "I encountered an error while generating the PDF.", "email_sent": False}

    pdf_data = pdf_buffer.getvalue()

    try:
        from dotenv import load_dotenv
        import pathlib
        
        env_path = pathlib.Path(__file__).parent.parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        sender_email = os.getenv("SMTP_EMAIL")
        sender_password = os.getenv("SMTP_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if not sender_email or not sender_password:
            return {"assistant_response": "Email credentials are not configured on the server.", "email_sent": False}

        msg = EmailMessage()
        msg['Subject'] = f"Your Trip Itinerary to {state.get('destination', 'Unknown')}"
        msg['From'] = sender_email
        msg['To'] = email_address
        msg.set_content("Hello! Attached is your generated trip itinerary PDF.")

        msg.add_attachment(
            pdf_data,
            maintype='application',
            subtype='pdf',
            filename='itinerary.pdf'
        )

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return {"email_sent": True}

    except Exception as e:
        print("Email error:", e)
        return {"assistant_response": "I encountered an error while trying to send the email.", "email_sent": False}
