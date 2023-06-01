import random
import socket
import threading
import logging
import ast

from proconq_chat.setup_logging import setup_logging
from proconq_chat.utils.constants import (
    Paths,
    ServerConstants
)
from proconq_chat.utils.exceptions import NoAvailableIDError
from proconq_chat.utils.cryptography import (
    AESCipher,
    RSACipher
)
from proconq_chat.src.database.user_database import UserDatabase


class ClientHandler:
    def __init__(self, logger: logging.Logger, client_id: int,
                 client: socket.socket, address: tuple):
        # Messages sent that are waiting for confirmation by the client
        self.rcvd_buffer: dict[int, list[str]] = {}

        self.logger = logger
        self.log_message_start = f'Client {client} {address}'

        self.client = client
        self.address = address

        self.client.settimeout(0.1)

        self.logger.debug(f'{self.log_message_start} Handler Initialized')

        self.client_id = client_id
        self.client_name = 'GUEST'

        self.rsa_cipher = RSACipher()
        self.aes_cipher = AESCipher()
        self.aes_key: bytes = None
        self.aes_iv: bytes = None

        self.establish_secure_connection()

    def logout_client(self) -> None:
        self.client_name = 'GUEST'

        request = self.build_request('LOGGEDOUT')
        self.send_request(request)

    def build_request(self, message_code: str, 
                      data: str = None,
                      encrypt: bool = True) -> bytes:
        """
        Combines message code and data, separates by #
        Encrypts result with AES
        Attaches its size to it
        """
        if data:
            message = f'#{message_code}#{data}'.encode()
        else:
            message = f'#{message_code}'.encode()

        if encrypt:
            message = self.aes_cipher.encrypt(message)

        size = str(len(message)).zfill(4).encode()
        self.logger.debug(f'{self.log_message_start} MSG BUILD: {size + message}')
        return size + message
    
    def send_request(self, message: bytes):
        self.logger.debug(f'{self.log_message_start} Sending: {message}')
        self.client.sendall(message)

    def receive_loop(self) -> None:
        try:
            size = int(self.client.recv(4).decode())
        except TimeoutError:
            return
        self.logger.debug(f'{self.log_message_start} Received size: {size}')
        data = self.client.recv(size)
        self.logger.debug(f'{self.log_message_start} Received data: {data}')

        use_rsa = False
        self.logger.debug(f'{self.log_message_start} Using AES to decrypt.')
        if not self.aes_key:
            use_rsa = True
            self.logger.debug(f'{self.log_message_start} Using RSA to decrypt.')
        data = self.decrypt_data(data, use_rsa).decode()
        message_code = data.split('#')[1]
        self.logger.debug(f'Message Code: {message_code}')
        data = data[len(message_code) + 2:]
        getattr(self, message_code.lower())(data)

    def decrypt_data(self, data: bytes, use_rsa: bool) -> bytes:
        if use_rsa:
            dec_data = self.rsa_cipher.decrypt(data)
        else:
            dec_data = self.aes_cipher.decrypt(data)
        self.logger.debug(f'Decrypted data: {dec_data}')
        return dec_data

    def establish_secure_connection(self) -> None:
        request = self.build_request('PUBKEY',
                                     self.rsa_cipher.public_key, False)
        self.send_request(request)

    def aeskey(self, data: str) -> None:
        """
        Modifies the values of aes iv and aes key.
        Confirms the secure connection with the client.
        """
        data = data.split('###')

        data[0] = ast.literal_eval(data[0])
        data[1] = ast.literal_eval(data[1])

        self.aes_key = data[0]
        self.aes_iv = data[1]

        self.aes_cipher.set_key(self.aes_key, self.aes_iv)
        self.logger.debug(f'{self.log_message_start} AES_KEY = {self.aes_key}')
        self.logger.debug(f'{self.log_message_start} AES_IVY = {self.aes_key}')

        request = self.build_request('AESCONF')
        self.send_request(request)

    def users(self, data: str = None) -> None:
        """
        After requested to, send the client list of online users.
        """
        message = ''

        for client_handler in ChatServer.clients.values():
            client_id = client_handler.client_id
            client_name = client_handler.client_name
            message += f'{client_name} #{client_id}\n'

        request = self.build_request('USERSCONF', message)
        self.send_request(request)

    def login(self, data: str) -> None:
        """
        Apply login attempt by user and handle accordingly.
        """
        name = data.split('#')[0]
        password = data[len(name) + 1:]

        if name.isalpha():
            status = ChatServer.login(name, password)
        else:
            status = False

        if status:
            status = '1'
            self.client_name = name
        else:
            status = '0'
        request = self.build_request('LOGINCONF', status)
        self.send_request(request)

    def regstr(self, data: str) -> None:
        """
        Apply login attempt by user and handle accordingly.
        """
        name = data.split('#')[0]
        password = data[len(name) + 1:]

        if name.isalpha():
            status = ChatServer.register(name, password)
        else:
            status = False

        status = '1' if status else '0'
        request = self.build_request('REGSTRCONF', status)
        self.send_request(request)

    def getid(self, data: str = None) -> None:
        """
        After requested to, send the client its ID
        """
        request = self.build_request('GETIDCONF', self.client_id)
        self.send_request(request)

    def rcvdmsgconf(self, content: str) -> None:
        """
        Target confirms receiving message from sender.
        """
        sender_id = int(content.split('#')[0])
        message = content[5:]
        try:
            client_handler = ChatServer.clients[sender_id]
            client_handler.rcvd_buffer[self.client_id].remove(message)
            self.logger.debug(f'{self.log_message_start} Removed from buffer #{sender_id} - {message}')
        except Exception:
            self.logger.debug(f'{self.log_message_start} Message not in buffer #{sender_id} - {message}')

    def buffer(self, data: str = None) -> None:
        """
        Send the receive buffer.
        """
        request = ''
        
        for target_id, messages in self.rcvd_buffer.items():
            for message in messages:
                msgsize = str(len(message) + 1).zfill(4)
                request += f'{msgsize}#{target_id}#{message}\n'

        if not request:
            message = 'Buffer is empty'
            msgsize = str(len(message) + 1).zfill(4)
            request = f'{msgsize}#0000#{message}'

        request = self.build_request('BUFFERCONF', request)
        self.send_request(request)

    def sndmsg(self, data: str) -> None:
        """
        Forwards a message from one client to another.
        """
        data = data
        target_id = int(data[:4])
        message = data[5:]
        
        self.forward_rcvd(target_id, message)

    def forward_rcvd(self, target_id: int, message: str):
        self.logger.debug(f'{self.log_message_start} Forwarding: #{target_id} - {message}')

        try:
            if target_id == self.client_id:
                raise KeyError
            client_hanlder = ChatServer.clients[target_id]
            request = client_hanlder.build_request('RCVDMSG', f'{self.client_id}#{message}')
            
            try:
                self.rcvd_buffer[target_id].append(message)
            except KeyError:
                self.rcvd_buffer[target_id] = [message]
            finally:
                self.logger.debug(f'{self.log_message_start} Added to buffer: #{target_id} - {message}')

            client_hanlder.send_request(request)
        except KeyError:
            self.logger.debug(f'{self.log_message_start} ERROR: Forward to #{target_id} failed.')
            request = self.build_request('SNDMSGCONF', f'0#{target_id}')
            self.send_request(request)

    def database(self, data: str = None) -> None:
        """
        Sends to admin the database
        """
        response = ''
        if self.client_name != 'ADMIN':
            response = 'FAILURE'
        else:
            credentials = ChatServer.get_credentials()
            
            for name, password in credentials.items():
                passsize = str(len(password) + 1).zfill(4)
                response += f'{passsize}#{name}#{password}\n'

            if not response:
                response = 'EMPTY'

        request = self.build_request('DATABASECONF', response)
        self.send_request(request)

    def deluser(self, name: str) -> None:
        """
        Deletes a user from the database.
        """
        status = ''

        if self.client_name != 'ADMIN' or name == 'GUEST':
            status = '0'
        else:
            status = '1' if ChatServer.deluser(name) else '0'

        request = self.build_request('DELUSERCONF', f'{status}#{name}')
        self.send_request(request)

    def run(self) -> None:
        self.receive_loop()


class ChatServer:
    db = UserDatabase(Paths.DATABASE)
    clients_ids: set[int] = set()
    clients: dict[int, ClientHandler] = {}
    lock = threading.Lock()

    def __init__(self, port: int, logger: logging.Logger):
        """
        Initializes the Server's Chat
        self.logger - logger instance
        self.sock - server's socket
        """
        self.logger = logger
        self.logger.debug('Attempting to create socket.')
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug('Server socket successfully created.')
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((ServerConstants.HOST,
                            port))
        except Exception as err:
            self.logger.critical(f'Server failed to start: {err}')

    def listen(self) -> None:
        """
        Makes the server socket listen.
        Attempting to accept in a loop blocks the loop from continuing.
        When a client connects a thread is started for the client.
        The loop then continues to accept.
        """
        self.sock.listen()
        self.logger.debug('Server is now listening.')

        while True:
            self.logger.debug('Waiting for an incoming connection.')
            client, address = self.sock.accept()
            self.logger.info(f'New Connection: {client} {address}')
            thread = threading.Thread(target=self.handle_client,
                                      args=(client, address))
            thread.start()
            self.logger.info('Started thread for client.')
    
    def handle_client(self, client: socket.socket, address: tuple) -> None:
        """
        Handles a client thread
        """
        log_message_start = f'Client {client} {address}'

        try:
            client_id = ChatServer.generate_id(log_message_start, self.logger)
            client_handler = ClientHandler(self.logger, client_id,
                                           client, address)
            ChatServer.clients[client_id] = client_handler
            while True:
                client_handler.run()
        except NoAvailableIDError as err:
            self.logger.error(f'{log_message_start} Exception: {err}')
            client_id = None
        except ValueError as err:
            self.logger.error(f'{log_message_start} Exception (probably size): {err}')
        except Exception as err:
            self.logger.error(f'{log_message_start} Exception: {err}')
        finally:
            self.logger.debug(f'{log_message_start} Closing socket.')
            self.logger.debug(f'{log_message_start} Removing {client_id}')
            ChatServer.remove_client(client_id)
            client.close()

    @classmethod
    def login(cls, name: str, password: str) -> bool:
        with cls.lock:
            return cls.db.verify_login(name, password)

    @classmethod
    def register(cls, name: str, password: str) -> bool:
        with cls.lock:
            return cls.db.register_user(name, password)

    @classmethod
    def get_credentials(cls) -> dict[str, str]:
        with cls.lock:
            return cls.db.get_all_user_credentials()
        
    @classmethod
    def deluser(cls, name: str) -> bool:
        status = False
        with cls.lock:
            status = cls.db.delete_user(name)

            if status:
                for client in ChatServer.clients.values():
                    if client.client_name == name:
                        client.logout_client()
        
        return status

    @classmethod
    def remove_client(cls, client_id: int) -> None:
        """
        Removes a client by ID from the list of clients.
        """
        with cls.lock:
            if client_id in cls.clients:
                try:
                    del cls.clients[client_id]
                except KeyError:
                    pass
                cls.clients_ids.remove(client_id)

    @classmethod
    def generate_id(cls, log_message_start: str,
                    logger: logging.Logger) -> int:
        """
        Generates a random client ID.
        """
        with cls.lock:
            # Create a list of unused IDs by taking the difference between the
            # range of 1000 to 9999 and the existing clients_ids set
            unused_ids = list(set(range(1000, 10000)) - cls.clients_ids)

            # If there are no unused IDs available, raise a NoAvailableIDError
            if not unused_ids:
                raise NoAvailableIDError("No available IDs.")

            new_id = random.choice(unused_ids)
            cls.clients_ids.add(new_id)

            logger.debug(f'{log_message_start} Generated ID {new_id}')

            return new_id


def launch_server(port: int):
    logger = setup_logging(__name__)
    chat_server = ChatServer(port, logger)
    logger.debug('Activating Server listen mode.')
    chat_server.listen()


if __name__ == '__main__':
    launch_server()
