import socket, time, smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class SocketHandler:
    def __init__(self, host='0.0.0.0', port=1234):
        self.host = host
        self.port = port
        self.socket = None
        self.client_socket = None
        self.client_ip = None
        
        # Create a socket and set options
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def bind_and_listen(self):
        try:
            sock_address = (self.host, self.port)
            self.socket.bind(sock_address)
            self.socket.listen(1)  # Listens for incoming connection. Max set to 1 connection at a time.
            logging(f"Socket created on {self.host} on port {self.port}")
            self.accept_connection()
        except Exception as e:
            logging(f'ERROR: Failed to bind socket {e}')

    def accept_connection(self):
        try:
            logging('Waiting for incoming files')
            self.client_socket, client = self.socket.accept()
            self.client_ip = client[0]
            logging(f"Connection received from {self.client_ip}")
            data_handle.rec_data()
        except Exception as e:
            logging(f'ERROR: Connection attempt failed: {e}')

class DataHandler:
    def __init__(self):
        self.data_stream = []
        self.mail_body = []
        self.mail_list = []

    def rec_data(self):
        try:
            logging(f'Recieving file from {handler.client_ip}')
            filename = handler.client_socket.recv(1024).decode().strip()
            logging(f'Filename: {filename}')
            time.sleep(.1)
            self.list_parse(handler.client_socket.recv(1024).decode()) # Causes error if there is only one email in the list
            time.sleep(.1)

            while True:
                data = handler.client_socket.recv(1024)
                if ':EOF:' in data.decode():
                    logging(f"File {filename} Received")
                    break
                self.data_stream.append(data.decode())

            while True:
                data = handler.client_socket.recv(1024)
                if not data:
                    logging(f"Email body Received")
                    break
                self.mail_body.append(data.decode())
            self.to_mailer(filename)
        except Exception as e:
            logging(f"ERROR: Error receiving data from AI instance: {e}")
        return

    def list_parse(self, mail_list):
        mail_list = mail_list.split(',')
        for i in mail_list:
            i = i.replace("'", '').replace('[', '').replace(']', '').strip()
            self.mail_list.append(i)
        logging(f'Mail list received: {self.mail_list}')
        return

    def to_mailer(self, filename):
        try:
            binary_payload = ''.join(self.data_stream).encode()
            email_message = ' '.join(self.mail_body)
            build_message.email_body(filename, binary_payload, self.mail_list, email_message)
            self.data_stream.clear()
            self.mail_body.clear()
            self.mail_list.clear()
            handler.accept_connection()
        except Exception as e:
            logging(f'ERROR: problem with building message: {e}')
        return
    
class BuildMessage:
    def __init__(self, svc_email = 'pphilson@proton.me', svc_pass = 'y3wiw0rXO92DdXazv8Udxw', smtp_server = 'localhost', smtp_port = 1025):
        self.svc_email = svc_email
        self.svc_pass = svc_pass
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def email_body(self, filename, binary, mail_list, email_message):
        try:
            logging('Successfully called BuildMessage class and transferred message data')
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

            message = MIMEMultipart()
            message["From"] = self.svc_email
            message['To'] = ','.join(mail_list)
            message["Subject"] = subject
            logging('Finished building message')
            message.attach(MIMEText(email_message, "plain"))
            self.email_attach(message, filename, binary)
        except Exception as e:
            logging(f'ERROR: Failed to set message parameters: {e}')
        return

    def email_attach(self, message, filename, binary):
        try:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(binary)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            message.attach(part)
            logging('File successfully attached to email message')
            self.email_send(message)
        except Exception as e:
            logging(f'ERROR: Failed to attach file: {e}')
        return

    def email_send(self, message):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.svc_email, self.svc_pass)
                server.send_message(message)
            logging('Message and attachments sent to email server')
        except Exception as e:
            logging(f'ERROR: Failed send email: {e}')
        return

    def get_time():
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

def logging(log):
    log_time = BuildMessage.get_time()
    with open('report-mailer.log', 'a') as alert_file:
        alert_file.write(f'{log_time}:{log}\n')
    return

if __name__ == "__main__":
    handler = SocketHandler()
    data_handle = DataHandler()
    build_message = BuildMessage()
    handler.bind_and_listen()