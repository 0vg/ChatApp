import socket, threading, json
from cmd import Cmd
from colorama import Fore, Style

class Client(Cmd):
    prompt = ''
    intro = f'{Fore.YELLOW}Welcome to the chat client. Type "help" for a list of commands.{Style.RESET_ALL}'
    
    def __init__(self):
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__id = None
        self.__nickname = None 
        self.__isLogin = False
        
    def __receive_message_thread(self):
        while self.__isLogin:
            try:
                buffer = self.__socket.recv(1024).decode()
                obj = json.loads(buffer)
                if obj['t'] == 'broadcast':
                    print(f'{Fore.GREEN}[' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + f']{Style.RESET_ALL} {obj["message"]}')
                elif obj['t'] == 'direct':
                    print(f'{Fore.MAGENTA}[DIRECT FROM ' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + f']{Style.RESET_ALL} {obj["message"]}')
            except Exception as e:
                print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} {e}')
                
    def __send_message_thread(self, message):
        self.__socket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message,
            't': 'broadcast'
        }).encode())
        # Remove the input line from the screen
        print('\033[A                             \033[A')
        print(f'{Fore.GREEN}[YOU(' + str(self.__id) + ')' + f']{Style.RESET_ALL} {message}')
        
    def start(self, IP, PORT):
        self.__socket.connect((IP, PORT))
        self.cmdloop()
        
        

    def do_direct(self, args):
        # direct <user_id> <message>
        args = args.split(' ')
        user_id = int(args[0])
        message = ' '.join(args[1:])
        
        self.__socket.send(json.dumps({
            'type': 'direct',
            'sender_id': self.__id,
            'receiver_id': user_id,
            'message': message,
            't': 'direct',
        }).encode())

    def do_userlist(self, args=None):
        self.__socket.send(json.dumps({
            'type': 'userlist',
            'sender_id': self.__id,
            't': 'userlist'
        }).encode())
        
    def do_login(self, args):
        nickname = args.split(' ')[0]
        self.__socket.send(json.dumps({
            'type': 'login',
            'nickname': nickname,
            't': 'login'
        }).encode())
        
        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.__isLogin = True
                print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} Logged in as {nickname}.')
                
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
            else:
                print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} Login failed.')
        except Exception as e:
            print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} {e}')
            
    def do_send(self, args):
        message = args
        thread = threading.Thread(target=self.__send_message_thread, args=(message,))
        thread.setDaemon(True)
        thread.start()
        
    def do_logout(self, args=None):
        self.__socket.send(json.dumps({
            'type': 'logout',
            'sender_id': self.__id,
            't': 'logout'
        }).encode())
        self.__isLogin = False
        print(f'{Fore.YELLOW}[INFO]{Style.RESET_ALL} Logged out.')
        return True
    
    def do_help(self, arg):
        command = arg.split(' ')[0]
        if command == '':
            print(f'{Fore.YELLOW}login <nickname>{Style.RESET_ALL} - Log in with a nickname.')
            print(f'{Fore.YELLOW}send <message>{Style.RESET_ALL} - Send a message to all users.')
            print(f'{Fore.YELLOW}logout{Style.RESET_ALL} - Log out.')
            print(f'{Fore.YELLOW}direct <user_id> <message>{Style.RESET_ALL} - Send a message to a specific user.')
            print(f'{Fore.YELLOW}userlist{Style.RESET_ALL} - Get a list of all connected users.')
        elif command == 'login':
            print(f'{Fore.YELLOW}login <nickname>{Style.RESET_ALL} - Log in with a nickname.')
        elif command == 'send':
            print(f'{Fore.YELLOW}send <message>{Style.RESET_ALL} - Send a message to all users.')
        elif command == 'logout':
            print(f'{Fore.YELLOW}logout{Style.RESET_ALL} - Log out.')
        elif command == 'direct':
            print(f'{Fore.YELLOW}direct <user_id> <message>{Style.RESET_ALL} - Send a message to a specific user.')
        elif command == 'userlist':
            print(f'{Fore.YELLOW}userlist{Style.RESET_ALL} - Get a list of all connected users.')
        else:
            print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} Unknown command.')