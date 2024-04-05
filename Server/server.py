import socket, threading, json
from colorama import Fore, Style

class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.nicknames = []

    def start_listening(self, server, port):
        """
        Start the server and begin listening for connections.
        """
        self.socket.bind((server, port))
        self.socket.listen(10)
        print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} Server started.')

        self.connections.clear()
        self.nicknames.clear()
        self.connections.append(None)
        self.nicknames.append('SERVER')

        while True:
            connection, address = self.socket.accept()
            print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} {address} connected.')

            thread = threading.Thread(target=self.handle_new_connection, args=(connection,))
            thread.setDaemon(True)
            thread.start()

    def handle_new_connection(self, connection):
        """
        Handle a new connection and wait for the user to log in.
        """
        try:
            buffer = connection.recv(1024).decode()
            login_data = json.loads(buffer)

            if login_data['type'] == 'login':
                self.connections.append(connection)
                self.nicknames.append(login_data['nickname'])
                connection.send(json.dumps({'id': len(self.connections) - 1}).encode())

                thread = threading.Thread(target=self.handle_user, args=(len(self.connections) - 1,))
                thread.setDaemon(True)
                thread.start()
            else:
                print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} Unknown message received.')
        except Exception as e:
            print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} {e}')
            connection.close()

    def handle_user(self, user_id):
        """
        Handle messages from a connected user.
        """
        connection = self.connections[user_id]
        nickname = self.nicknames[user_id]
        print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} {nickname} connected.')
        self.broadcast(message=f'{Fore.GREEN}[USER]{Style.RESET_ALL} {nickname}' + '(' + str(user_id) + ')' + ' connected.')

        while True:
            try:
                buffer = connection.recv(1024).decode()
                message_data = json.loads(buffer)

                if message_data['type'] == 'broadcast':
                    self.broadcast(user_id, message_data['message'])
                elif message_data['type'] == 'direct':
                    self.direct_message(user_id, message_data['receiver_id'], message_data['message'])
                elif message_data['type'] == 'userlist':
                    self.send_userlist(user_id)
                elif message_data['type'] == 'logout':
                    print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} {nickname} disconnected.')
                    self.broadcast(message=f'{Fore.RED}[USER]{Style.RESET_ALL} {nickname}' + '(' + str(user_id) + ')' + ' disconnected.')
                    self.connections[user_id].close()
                    self.connections[user_id] = None
                    self.nicknames[user_id] = None
                    break
                else:
                    print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} {nickname} sent an unknown message.')
            except Exception as e:
                print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} {e}')
                self.connections[user_id].close()
                self.connections[user_id] = None
                self.nicknames[user_id] = None

    def broadcast(self, user_id=0, message=''):
        """
        Broadcast a message to all connected users.
        """
        for i in range(1, len(self.connections)):
            if user_id!= i and self.connections[i]:
                self.connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.nicknames[user_id],
                    'message': message,
                    't': 'broadcast'
                }).encode())
                
    def direct_message(self, sender_id, receiver_id, message):
        """
        Send a direct message to a specific user.
        """
        if 0 <= receiver_id < len(self.connections) and self.connections[receiver_id]:
            self.connections[receiver_id].send(json.dumps({
                'type': 'direct',
                'sender_id': sender_id,
                'sender_nickname': self.nicknames[sender_id],
                'message': message,
                't': 'direct'
            }).encode())
            print(f'{Fore.MAGENTA}[DIRECT]{Style.RESET_ALL} {self.nicknames[sender_id]} -> {self.nicknames[receiver_id]}: {message}')
        else:
            print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} User not found.')

    def send_userlist(self, user_id):
        """
        Send a list of all connected users to a specific user.
        """
        print(user_id)
        if 0 <= user_id < len(self.connections) and self.connections[user_id]:
            userlist = [{'id': i, 'nickname': self.nicknames[i]} for i in range(1, len(self.connections)) if self.connections[i]]
            self.connections[user_id].send(json.dumps({
                'type': 'userlist',
                'userlist': userlist,
                't': 'userlist'
            }).encode())