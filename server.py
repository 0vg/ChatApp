import Server.server as srv
import yaml

def read_config(key):
    """
    Read a value from the config file.
    """
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        return config['config'][key]
    except Exception as e:
        if key == 'IP':
            return '127.0.0.1'
        elif key == 'PORT':
            return 5555

def start_server():
    """
    Start the server with the IP and PORT specified in the config file.
    """
    server = srv.Server()
    server.start_listening(read_config('IP'), read_config('PORT'))

if __name__ == '__main__':
    start_server()