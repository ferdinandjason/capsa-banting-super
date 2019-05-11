import sys
import socket
import pickle
import select

class Server:
    def __init__(self):
        self.SERVER_ADDRESS = ('localhost', 5000)
        self.BUFFER_SIZE = 2048

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.SERVER_ADDRESS)
        self.server.listen(5)

        self.clients = []


    def run(self):
        input_list = [self.server, sys.stdin]
        RUNNING = True
        while RUNNING :
            input_ready, output_ready, except_ready = select.select(input_list, [], [])

            for files in input_ready:
                if files == self.server :
                    client_socket, client_address = self.server.accept()
                    input_list.append(client_socket)
                    self.clients.append(client_socket)
                    player_index = self.clients.index(client_socket)
                    print('Hi {} as player {}!'.format(client_address, player_index))
                    client_socket.send(str.encode(str(player_index)))
                elif files == sys.stdin :
                    to_send = sys.stdin.readline()
                    to_send = to_send.strip()
                    self.clients[0].send(str.encode(to_send))
                else :
                    message = files.recv(self.BUFFER_SIZE).decode()
                    if message == 'OUT':
                        files.send(str.encode('OK'))


        self.server.close()

if __name__ == "__main__":
    server = Server()
    server.run()