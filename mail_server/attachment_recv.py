"""
DEV NOTES: Fix the socket closing after one round of sending. It's embarrassing. 
"""
import socket, time, report_mailer

class bin_data:
    data_stream = []
    mail_body = []
    mail_list = []

def sock(): # Creates a socket and binds it to all available interfaces on the device and to port 1234
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows for immediate reuse of socket
    sock = ("0.0.0.0", 1234)
    s.bind(sock)
    s.listen(1) # Listens for incoming connection. Max set to 1 connection at a time.
    connect()

def connect():
    global soc, clientip
    print("\nWaiting for incoming files...\n")
    soc, client = s.accept() # Accepts incoming TCP connections
    clientip = client[0]
    print(f"\nConnection received from {clientip}")
    rec_data()


def rec_data():
    print(f'\nRecieving file from {clientip}\n')
    filename = soc.recv(1024).decode().strip()
    print(f'{filename}\n')
    time.sleep(.1)

    bin_data.mail_list = eval(soc.recv(1024).decode()) # Causes error if there is only one email in the list
    print(bin_data.mail_list)
    print(f'{filename}\n')
    time.sleep(.1)

    while True:
        data = soc.recv(1024)
        if ':EOF:' in data.decode():
            print(f"File {filename} Received\n")
            break
        bin_data.data_stream.append(data.decode())

    while True:
        data = soc.recv(1024)
        if not data:
            print(f"Email body Received\n")
            break
        bin_data.mail_body.append(data.decode())

    to_mailer(filename)
    return

def to_mailer(filename):

    binary_payload = ''.join(bin_data.data_stream).encode()
    email_message = ' '.join(bin_data.mail_body)
    report_mailer.email_body(filename, binary_payload, bin_data.mail_list, email_message)
    bin_data.data_stream.clear()
    bin_data.mail_body.clear()
    bin_data.mail_list.clear()
    connect()
    return

sock()
