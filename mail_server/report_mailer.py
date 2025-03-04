import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class svc_data:
    svc_email = ''
    svc_pass = ''
    smpt_server = 'localhost'
    smtp_port = 1025

def email_body(filename, binary, mail_list, email_message):

    if 'cyber' in filename:
        rep_type = 'Cyber'
    elif 'defense' in filename:
        rep_type = 'Defense'
    elif 'finance' in filename:
        rep_type = 'Financial'
    elif 'russian' in filename:
        rep_type = 'Russian'
    elif 'aerospace' in filename:
        rep_type = 'Aerospace'
    elif 'aerospace' in filename:
        rep_type = 'Aerospace'
    elif 'cve' in filename:
        rep_type = 'CVE'
    else:
        rep_type = ''

    subject = f'{rep_type} Intel Report - Phil'
    #body = f'Greetings,\n\nPlease find attached {rep_type} Intelligence report for {get_time()}.\n\nBest regards,\n\nPhil'

    message = MIMEMultipart()
    message["From"] = svc_data.svc_email
    message['To'] = ','.join(mail_list)
    message["Subject"] = subject
    message.attach(MIMEText(email_message, "plain"))
    email_attach(message, filename, binary)
    return

def email_attach(message, filename, binary):

    part = MIMEBase("application", "octet-stream")
    part.set_payload(binary)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")
    message.attach(part)
    email_send(message)
    return

def email_send(message):
    with smtplib.SMTP(svc_data.smpt_server, svc_data.smtp_port) as server:
        server.starttls()
        server.login(svc_data.svc_email, svc_data.svc_pass)
        server.send_message(message)
    return

def get_time():
    return datetime.today().strftime('%Y-%m-%d')
