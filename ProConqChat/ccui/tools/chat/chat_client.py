import socket
import threading
import ast

from rich import print as rprint

import ccui.utils.util
from ccui.setup_logging import setup_logging
from ccui.utils.cryptography import (
    AESCipher,
    RSACipher
)


class ChatClient(metaclass=ccui.utils.util.Singleton):
    def __init__(self):
        self.logger = setup_logging(__name__)
        
        self.is_connected: bool = False

        self.ip: str = None
        self.port: int = None
        
        self.sock: socket.socket = None
        self.receive_thread: threading.Thread = None
        self.lock = threading.Lock()

        self.aescipher = AESCipher()
        self.rsacipher = RSACipher()

        self.mail: list[str] = []

    def add_mail(self, mail: str) -> None:
        with self.lock:
            self.mail.append(mail)
            self.logger.debug(f'Added mail: {mail}')
    
    def pubkey(self, rsakey: bytes) -> None:
        """
        Receives the public RSA key of the server.
        Proceeds the hybrid encryption to inform the server about AES.
        """
        message = f'{self.aescipher.key}###{self.aescipher.iv}'
        self.logger.debug(f'PUBKEY message: {message}')
        
        rsakey = ast.literal_eval(rsakey.decode())

        self.logger.debug(f'Setting RSA key: {rsakey}')
        self.rsacipher.set_public_key(rsakey)

        self.logger.debug('Attempting to build AESKEY request...')
        request = self.build_request('AESKEY', message)
        self.send_request(request, False)

    def aesconf(self, data: bytes = None) -> None:
        """
        Receives the server's confirmation for AES.
        """
        self.logger.debug('Received AES confirmation.')

    def decrypt_message(self, message: bytes) -> bytes:
        if message.startswith(b'#PUBKEY'):
            self.logger.debug('RSA Key Received.')
            return message
        dec_message = self.aescipher.decrypt(message)
        self.logger.debug(f'Decrypted data: {dec_message}')
        return dec_message

    def encrypt_message(self, message: bytes, use_rsa: bool) -> bytes:
        if use_rsa:
            return self.rsacipher.encrypt(message)  
        return self.aescipher.encrypt(message)

    def build_request(self, message_code: str, data: str = None) -> bytes:
        """
        Combines message code and data, separates by #
        Encrypts with the AES or RSA
        Attaches its size to it
        """
        if data:
            message = f'#{message_code}#{data}'.encode()
        else:
            message = f'#{message_code}'.encode()

        if message_code == 'AESKEY':
            use_rsa = True
        else:
            use_rsa = False

        self.logger.debug(f'Encrypting message: {message}')
        message = self.encrypt_message(message, use_rsa)

        size = str(len(message)).zfill(4).encode()
        self.logger.debug(f'Built request: {size + message}')
        return size + message

    def send_request(self, request: bytes, verbose: bool = True) -> None:
        """
        Send a request to the server.
        """
        self.logger.debug(f'Sending request: {request}')
        if not self.is_connected:
            if verbose:
                output = "[#E74856]ERROR: Client is not connected to any server."
                self.logger.debug(output)
                rprint(output)
            return
        try:
            self.sock.sendall(request)
        except (ConnectionResetError, ConnectionAbortedError):
            if verbose:
                output = "[#E74856]ERROR: Client is not connected to any server (server probably crashed)."
                self.logger.debug(output)
                rprint(output)
            self.is_connected = False
            return
        if verbose:
            output = "[#16C60C]Request sent.[/#16C60C]"
            self.logger.debug(output)
            rprint(output)

    def receive_loop(self):
        while self.is_connected:
            try:
                data = self.sock.recv(4).decode()
                size = int(data)
                self.logger.debug(f'Received size: {size}')
                data = self.sock.recv(size)
                self.logger.debug(f'Received data: {data}')
                data = self.decrypt_message(data)
                message_code = data.split(b'#')[1].decode()
                self.logger.debug(f'Message Code: {message_code}')
                data = data[len(message_code) + 2:]
                self.logger.debug(f'Data: {data}')
                getattr(self, message_code.lower())(data)
            except OSError:
                break
            except ValueError:
                break

    def connect(self, ip: str, port: int) -> None:
        if self.is_connected:
            return rprint(f"[#E74856]ERROR: Client is connected already, to ('{ip}', {port})'[/#E74856]")
        
        self.ip = ip
        self.port = port

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
            self.is_connected = True
            rprint(f"[#16C60C]Connected to ('{ip}', {port})[/#16C60C]")

            self.receive_thread = threading.Thread(target=self.receive_loop)
            self.receive_thread.setDaemon(True)
            self.receive_thread.start()
        except ConnectionRefusedError:
            rprint(f"[#E74856]ERROR: Failed to connect to ('{ip}', {port})'[/#E74856]")
    
    def disconnect(self) -> None:
        if self.is_connected:
            self.is_connected = False
            self.sock.close()
            return rprint("[#16C60C]Disconnected.[/#16C60C]")
        rprint("[#E74856]ERROR: Client is not connected to any server.")

    def send_message(self, receiver_id: int, message: str) -> None:
        """
        Sends a message to a user.
        """
        self.send_request(self.build_request('SNDMSG',
                                             f'{receiver_id}#{message}'))

    def get_users(self) -> None:
        """
        Requests users list from server.
        """
        self.send_request(self.build_request('USERS'))

    def login(self, name: str, password: str) -> None:
        """
        Requests login as user to server.
        """
        self.send_request(self.build_request('LOGIN',
                                             f'{name}#{password}'))
        
    def register(self, name: str, password: str) -> None:
        """
        Requests to register as user.
        """
        self.send_request(self.build_request('REGSTR',
                                             f'{name}#{password}'))

    def get_id(self) -> None:
        """
        Requests user id applied by server.
        """
        self.send_request(self.build_request('GETID'))

    def output_mail(self) -> None:
        """
        Outputs all received mail.
        """
        if not self.mail:
            return print('No mail available.')
        for i, message in enumerate(self.mail, 1):
            rprint(f'#{i}: {message}\n')
        self.mail = []

    def database(self) -> None:
        """
        Requests the database.
        """
        request = self.build_request('DATABASE')
        self.send_request(request)

    def deluser(self, name: str) -> None:
        """
        Requests to delete a user from the databse.
        """
        request = self.build_request('DELUSER', name)
        self.send_request(request)

    def buffer(self) -> None:
        """
        Requests buffered messages to resend.
        """
        request = self.build_request('BUFFER')
        self.send_request(request)

    def bufferconf(self, data: bytes) -> None:
        """
        Adds to mail list of buffered messages.
        """
        data = data.decode()

        while data:
            msgsize = int(data[:4])
            target_id = data[5:9]
            message = data[10:10 + msgsize]

            self.add_mail(message)

            data = data[11 + msgsize:]

    def databaseconf(self, data: bytes) -> None:
        """
        Gets the database from the server.
        """
        data = data.decode()

        if data == 'FAILURE':
            return self.add_mail('[#E74856]ERROR: No access.[/#E74856]')
        elif data == 'EMPTY':
            return self.add_mail('Database is empty.')
        
        mail = ''

        while data:
            passsize = int(data[:4])
            name = data.split('#')[1]
            namelen = len(name)
            password = data[6 + namelen:6 + namelen + passsize]
            mail += f'NAME: {name}\n\tENCRYPTED PASSWORD: {password}\n'
            data = data[6 + namelen + passsize:]

        self.add_mail(mail)

    def deluserconf(self, data: bytes) -> None:
        """
        Gets confirmation of user deletion.
        """
        data = data.decode().split('#')
        status = data[0]
        name = data[1]

        if status == '0':
            status = '[#E74856]FAILED[/#E74856]'
        else:
            status = '[#16C60C]SUCCESS[/#16C60C]'

        mail = f'Deletion Status: {status}\n\tNAME: [#B4009E]{name}[/#B4009E]'

        self.add_mail(mail)

    def usersconf(self, users: bytes) -> None:
        """
        Adds to mail list of online users available received by server.
        """
        users = users.decode()
        self.add_mail(f'[#B4009E]{users}[/#B4009E]')

    def loginconf(self, status: bytes) -> None:
        """
        Adds to mail whether user login attempt was successful or not.
        """
        status = status.decode()
        if status == '1':
            self.add_mail('[#16C60C]Successfully logged in as user.[/#16C60C]')
        else:
            self.add_mail('[#E74856]Failed to log in as a user.[/#E74856]')

    def regstrconf(self, status: bytes) -> None:
        """
        Adds to mail whether user register attempt was successful or not.
        """
        status = status.decode()
        if status == '1':
            self.add_mail('[#16C60C]Successfully registerd a user.[/#16C60C]')
        else:
            self.add_mail('[#E74856]Failed to regsiter a user.[/#E74856]')

    def getidconf(self, user_id: bytes) -> None:
        """
        Adds to mail the ID assigned by the Server.
        """
        user_id = user_id.decode()
        self.add_mail(f'[#16C60C]ID Assigned: {user_id}')

    def sndmsgconf(self, status: bytes) -> None:
        """
        Adds to mail confirmation status of sending a message.
        """
        status = status.decode()
        target_id = status[2:]
        if status[0] == '1':
            self.add_mail(f'[#16C60C]Successfully sent message to #{target_id}.[/#16C60C]')
        else:
            self.add_mail(f'[#E74856]Failed to send message to #{target_id}.[/#E74856]')

    def rcvdmsg(self, content: bytes) -> None:
        """
        Adds to mail a message received from a user.
        """
        self.logger.debug(f'Received Message: {content}')
        content = content.decode()
        sender_id = content.split('#')[0]
        message = content[5:]
        self.add_mail(f'#{sender_id} sent you: {message}')

        request = self.build_request('RCVDMSGCONF', f'{sender_id}#{message}')
        self.send_request(request, False)

    def loggedout(self, data: bytes = None) -> None:
        """
        Gets notified by the server of a forced logout.
        """
        self.add_mail('Forced logout. Back to GUEST')
