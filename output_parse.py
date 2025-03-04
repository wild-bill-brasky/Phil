from datetime import datetime
from os import getcwd
import socket, time
from jinja2 import Template

class mail_list():
    mail_list = []

def build_article(p_type, send_mail, ip, port):
    flat_string = []
    with open(f'{getcwd()}/misc/template.html') as f:
        t = Template(f.read())

    with open(f'{getcwd()}/misc/ai_article.txt', 'r') as file:
        report = file.readlines()
        for line in report:
            line = line.replace('_', '')
            if line == '\n' or '--' in line:
                continue
            elif '* **' in line:
                line = line.replace('* **', '').replace('**', '')
            elif '**' in line:
                line = line.replace('**', '')
                line = f'<b><u>{line}</u></b>'
            elif '*' in line:
                line = line.replace('*', '')
            line = f'<br>{line}</br>'
            flat_string.append(line)
    flat_string = ''.join(flat_string)
    vals = {'replace_me': flat_string}

    with open(f'{getcwd()}/reports/{get_time()}_{p_type}_report.html', 'w') as f:
        f.write(t.render(vals))
    print(f'Report written to /reports/{get_time()}_{p_type}_report.html\n')
    send_connect(f'{get_time()}_{p_type}_report.html', send_mail, ip, port)
    return

def send_connect(file, send_mail, ip, port):
    if 'on' in send_mail:
        read_contacts()
        tcp_connect = socket.create_connection((ip, port))
        tcp_connect.sendall(file.encode())
        time.sleep(.1)
        
        tcp_connect.sendall(str(mail_list.mail_list).encode())
        time.sleep(.1)

        with open(f'{getcwd()}/reports/{file}', 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(.1)
                    tcp_connect.sendall(':EOF:'.encode())
                    break
                tcp_connect.sendall(data)
        print(f'File {file} sent to mail server...\n')
        time.sleep(.2)

        with open(f'{getcwd()}/misc/last_email.txt', 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                tcp_connect.sendall(data)
        tcp_connect.close()
    else:
        print('Email forwarding turned off, report only saved to local directory.\n')
        quit()
    return

def read_contacts():
    mail_list.mail_list.clear()
    with open(f'{getcwd()}/config/mail_list.config', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if '#' in line or line == '' or line == ' ':
                continue
            else:
                mail_list.mail_list.append(line.strip())
    return

def get_time():
    return datetime.today().strftime('%Y-%m-%d')

def get_cwd():
    return getcwd()
