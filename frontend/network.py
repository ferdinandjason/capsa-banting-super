import pickle
import socket

class Network:
    def __init__(self):
        self.SERVER_ADDRESS = ('10.151.253.145', 5000)
        self.BUFFER_SIZE = 4096
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(self.SERVER_ADDRESS)

    def send(self, status, data):
        data_to_send = {}
        data_to_send['status'] = status
        data_to_send['data'] = {}
        data_to_send['data'] = data
        data_pickled = pickle.dumps(data_to_send)
        self.server_socket.send(data_pickled)

    def get_socket(self):
        return self.server_socket