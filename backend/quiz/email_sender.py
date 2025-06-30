import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = "sathya.s.ihub@snsgroups.com"
SENDER_PASSWORD = "nakb gete imyy ytlp"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_quiz_email(recipient_email, quiz_link):
    subject = "🧪 Your AI-Generated Quiz Link"
    body = f"""
    Dear Student,

    Greetings!

    We hope you're progressing well in your learning journey.

    As part of your ongoing coursework, the AI Quiz Planner has generated a personalized quiz tailored to your recent data and activity. This quiz is designed to help reinforce your understanding and assess your current knowledge level.

    👉Quiz Link: {quiz_link}

    Please ensure you:
    - Attempt the quiz sincerely and independently.
    - Complete it before the assigned deadline.
    - Reach out if you face any technical issues or have questions.

    Your responses will be used to provide targeted feedback and improve future lessons.

    Wishing you all the best!

    Best regards,  
    Quiz Agent
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
