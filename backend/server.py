import sys
import socket
import pickle
import select
import random
import copy
import queue

class Server:
    def __init__(self):
        self.SERVER_ADDRESS = ('localhost', 5000)
        self.BUFFER_SIZE = 4096

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.SERVER_ADDRESS)
        self.server.listen(5)

        self.clients = []
        self.card_index = list(range(52))
        random.shuffle(self.card_index)

        self.game_data = {}
        self.game_data['card_index_before'] = []
        self.game_data['card_point_before'] = -1
        self.game_data['card_index_now'] = []
        self.game_data['card_point_now'] = -1
        self.game_data['player'] = {}
        self.game_data['player'][0] = {}
        self.game_data['player'][0]['player_sequence'] = [0,1,2,3]
        self.game_data['player'][0]['card_index'] = self.card_index[:13]
        self.game_data['player'][0]['card_count'] = 13
        self.game_data['player'][1] = {}
        self.game_data['player'][1]['player_sequence'] = [1,0,2,3]
        self.game_data['player'][1]['card_index'] = self.card_index[13:26]
        self.game_data['player'][1]['card_count'] = 13
        self.game_data['player'][2] = {}
        self.game_data['player'][2]['player_sequence'] = [2,0,1,3]
        self.game_data['player'][2]['card_index'] = self.card_index[26:39]
        self.game_data['player'][2]['card_count'] = 13
        self.game_data['player'][3] = {}
        self.game_data['player'][3]['player_sequence'] = [3,0,1,2]
        self.game_data['player'][3]['card_index'] = self.card_index[39:52]
        self.game_data['player'][3]['card_count'] = 13

        self.game_data['turn_player_id'] = 0

    def run(self):
        input_list = [self.server, sys.stdin]
        game_order = queue.Queue()
        RUNNING = True
        FIRST = True
        while RUNNING :
            input_ready, output_ready, except_ready = select.select(input_list, [], [])

            for files in input_ready:
                if files == self.server :
                    client_socket, client_address = self.server.accept()
                    input_list.append(client_socket)
                    self.clients.append(client_socket)
                    player_index = self.clients.index(client_socket)
                    self.reply_with_id(client_socket, player_index)
                    client_socket.send(str.encode(str(player_index)))
                    game_order.put(player_index)

                    if len(self.clients) == 2:
                        game_order.put(game_order.get())
                elif files == sys.stdin :
                    to_send = sys.stdin.readline()
                    to_send = to_send.strip()
                    self.clients[0].send(str.encode(to_send))
                else :
                    message = files.recv(self.BUFFER_SIZE)
                    message = pickle.loads(message)
                    print(message)
                    print(message['status'] == 'QUIT')
                    if message['status'] == 'QUIT':
                        self.reply_ok(files)
                        input_list.remove(files)
                    elif message['status'] == 'UPDATE' :
                        player_id = message['data']['id']
                        is_play = message['data']['play'] == 'PLAY'
                        print(message['data']['play'], is_play)
                        if is_play :
                            player_card = self.game_data['player'][player_id]['card_index']
                            player_choosen_card = message['data']['selected_card']
                            player_choosen_card_point = message['data']['selected_card_point']
                            for card in player_choosen_card:
                                player_card.remove(card)
                            self.game_data['player'][player_id]['card_index'] = player_card
                            self.game_data['player'][player_id]['card_count'] = len(player_card)
                            self.game_data['card_index_before'] = self.game_data['card_index_now']
                            self.game_data['card_point_before'] = self.game_data['card_point_now']
                            self.game_data['card_index_now'] = player_choosen_card
                            self.game_data['card_point_now'] = player_choosen_card_point
                            
                            self.game_data['turn_player_id'] = game_order.get()
                            
                            game_order.put(self.game_data['turn_player_id'])
                        else :
                            active_player_id = game_order.get()
                            active_player = game_order.qsize()
                            if active_player == 1 :
                                self.game_data['card_point_now'] = 0
                                for i in range(active_player_id + 1, len(self.clients)):
                                    game_order.put(i)
                                for i in range(0, active_player_id):
                                    game_order.put(i)
                            print(list(game_order.queue))
                            

                        self.broadcast_game_data(self.game_data)

        self.server.close()

    def reply_ok(self, client_socket):
        data_to_send = {}
        data_to_send['status'] = 'BYE'
        data_to_send['data'] = {}
        data_pickled = pickle.dumps(data_to_send)
        client_socket.send(data_pickled)
    
    def reply_with_id(self, client_socket, player_id) :
        data_to_send = {}
        data_to_send['status'] = 'GET_ID'
        data_to_send['data'] = {}
        data_to_send['data']['id'] = player_id
        data_to_send['data']['card_index'] = self.game_data['player'][player_id]['card_index']
        data_to_send['data']['turn_player_id'] = self.game_data['turn_player_id']
        data_pickled = pickle.dumps(data_to_send)
        client_socket.send(data_pickled)

    def broadcast_game_data(self, data):
        data_to_send = {}
        data_to_send['status'] = 'BROADCAST'
        data_to_send['data'] = {}
        data_to_send['data'] = data
        for client_socket in self.clients :
            player_id = self.clients.index(client_socket)
            data_to_send_p = copy.deepcopy(data_to_send)
            data_to_send_p['data']['player_id'] = player_id
            data_pickled = pickle.dumps(data_to_send_p)
            client_socket.send(data_pickled)



if __name__ == "__main__":
    server = Server()
    server.run()