import pickle
import socket

class Network:
    def __init__(self):
        self.SERVER_ADDRESS = ('localhost', 5000)
        self.BUFFER_SIZE = 2048
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(self.SERVER_ADDRESS)

    def send(self, data):
        data_pickled = pickle.dumps(data)
        self.server_socket.send(data_pickled)

    def get_socket(self):
        return self.server_socket