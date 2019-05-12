import sys
import copy
import random
import pygame
import itertools
import threading

from factory import *
from network import *

class GameRule:
    def __init__(self, cards, before_point):
        self.cards = cards
        self.card_counter = {
            3 : [],
            4 : [],
            5 : [],
            6 : [],
            7 : [],
            8 : [],
            9 : [],
            10 : [],
            11 : [],
            12 : [],
            13 : [],
            14 : [],
            15 : [],
        }
        self.card_type_counter = {
            'clover' : [],
            'diamond' : [],
            'heart' : [],
            'spade' : [],
        }
        self.card_type_sequence = ['diamond', 'clover', 'heart', 'spade']
        self.counting_card()

        self.combo = {
            "pair" : [],
            "trice" : [],
            "straight" : [],
            "flush" : [],
            "four-of-a-kind" : [],
            "full-house" : [],
        }

        self.combo_point = {
            "pair" : [],
            "trice" : [],
            "straight" : [],
            "flush" : [],
            "four-of-a-kind" : [],
            "full-house" : [],
        }

        self.combo_value = {
            'single' : 0,
            'pair' : 1,
            'trice' : 2,
            'straight' : 3,
            'flush' : 4,
            'full-house' : 5,
            'four-of-a-kind' : 6,
            'straight-flush' : 7,
            'royal-flush' : 8,
        }

        self.point_before = before_point
        self.card_combo = -1
        temp = before_point // 1000
        if temp == 0:
            self.card_combo = 1
        elif temp == 1:
            self.card_combo = 2
        elif temp == 2:
            self.card_combo = 3
        elif temp >= 3 and temp <= 8:
            self.card_combo = 5

        if before_point == -1 :
            self.card_combo = -1

        self.generate_combo()

    def counting_card(self):
        index = 0
        for card in self.cards:
            self.card_counter[card.number].append(index)
            self.card_type_counter[card.type].append(index)
            index += 1

    def calculate_point(self, types, number, combo):
        POINT = self.combo_value[combo] * 1000 + number * 10 + types
        return POINT

    def generate_combo(self):
        index_pair = []
        index_trice = []
        index_straight = []
        index_flush = []
        index_four = []
        index_full_house = []

        point_pair = []
        point_trice = []
        point_straight = []
        point_flush = []
        point_four = []
        point_full_house = []
        for key, value in self.card_counter.items():
            if len(value) == 2 and (self.card_combo == 2 or self.card_combo == -1):
                largest_type = max(self.card_type_sequence.index(self.cards[value[0]].type), self.card_type_sequence.index(self.cards[value[1]].type))
                point = self.calculate_point(largest_type, self.cards[value[0]].number, 'pair')
                if point > self.point_before :
                    index_pair.append([value[0], value[1]])
                    point_pair.append(point)
            elif len(value) == 3 and (self.card_combo == 3 or self.card_combo == -1):
                largest_type = max(self.card_type_sequence.index(self.cards[value[0]].type), self.card_type_sequence.index(self.cards[value[1]].type), self.card_type_sequence.index(self.cards[value[2]].type))
                point = self.calculate_point(largest_type, self.cards[value[0]].number, 'trice')
                if point > self.point_before :
                    index_trice.append([value[0], value[1], value[2]])
                    point_trice.append(point)
            elif len(value) == 4  and (self.card_combo == 5 or self.card_combo == -1):
                for index in range(3,16):
                    if index != key and len(self.card_counter[index]) != 4:
                        for index_card in self.card_counter[index]:
                            point = self.calculate_point(3, self.cards[value[0]].number, 'four-of-a-kind')
                            if point > self.point_before :
                                index_four.append([value[0], value[1], value[2], value[3], index_card])
                                point_four.append(point)

            if key <= 11 and (self.card_combo == 5 or self.card_combo == -1):
                straight_exist = True
                for straight_key in range(key, key+5):
                    if len(self.card_counter[straight_key]) == 0 :
                        straight_exist = False
                
                if straight_exist :
                    for straight1 in self.card_counter[key]:
                        for straight2 in self.card_counter[key+1]:
                            for straight3 in self.card_counter[key+2]:
                                for straight4 in self.card_counter[key+3]:
                                    for straight5 in self.card_counter[key+4]:
                                        if self.cards[straight5].type == self.cards[straight4].type and \
                                            self.cards[straight4].type == self.cards[straight3].type and \
                                            self.cards[straight3].type == self.cards[straight2].type and \
                                            self.cards[straight2].type == self.cards[straight1].type :
                                            if self.cards[straight1].number == 11 :
                                                point = self.calculate_point(self.card_type_sequence.index(self.cards[straight5].type), self.cards[straight5].number, 'royal-flush')
                                                if point > self.point_before:
                                                    point_straight.append(point)
                                                    index_straight.append([straight1, straight2, straight3, straight4, straight5])
                                            else :    
                                                point = self.calculate_point(self.card_type_sequence.index(self.cards[straight5].type), self.cards[straight5].number, 'straight-flush')
                                                if point > self.point_before:
                                                    point_straight.append(point)
                                                    index_straight.append([straight1, straight2, straight3, straight4, straight5])
                                        else :
                                            point = self.calculate_point(self.card_type_sequence.index(self.cards[straight5].type), self.cards[straight5].number, 'straight')
                                            if point > self.point_before:
                                                point_straight.append(point)
                                                index_straight.append([straight1, straight2, straight3, straight4, straight5])
        
        for key, value in self.card_type_counter.items():
            if len(value) >= 5 and (self.card_combo == 5 or self.card_combo == -1):
                for permutation in itertools.combinations(value, 5):
                    # permutation = permutation.sort()
                    
                    if self.cards[permutation[0]].number == self.cards[permutation[1]].number-1 and \
                        self.cards[permutation[1]].number == self.cards[permutation[2]].number-1 and \
                        self.cards[permutation[2]].number == self.cards[permutation[3]].number-1 and \
                        self.cards[permutation[3]].number == self.cards[permutation[4]].number-1 :
                        if self.cards[permutation[0]].number == 11 :
                            point = self.calculate_point(self.card_type_sequence.index(self.cards[permutation[-1]].type), self.cards[permutation[-1]].number, 'royal-flush')
                            if point > self.point_before:
                                point_flush.append(point)
                                index_flush.append(permutation)
                        else :
                            point = self.calculate_point(self.card_type_sequence.index(self.cards[permutation[-1]].type), self.cards[permutation[-1]].number, 'straight-flush')
                            if point > self.point_before:
                                point_flush.append(point)
                                index_flush.append(permutation)
                    else :
                        point = self.calculate_point(self.card_type_sequence.index(self.cards[permutation[-1]].type), self.cards[permutation[-1]].number, 'flush')
                        if point > self.point_before:
                            point_flush.append(point)
                            index_flush.append(permutation)

        for pair in index_pair:
            for trice in index_trice:
                if (self.card_combo == 5 or self.card_combo == -1):
                    largest_type = max(self.card_type_sequence.index(self.cards[trice[0]].type), self.card_type_sequence.index(self.cards[trice[1]].type), self.card_type_sequence.index(self.cards[trice[2]].type))
                    point = self.calculate_point(largest_type, self.cards[trice[0]].number, 'full-house')
                    if point > self.point_before:
                        index_full_house.append([pair[0], pair[1], trice[0], trice[1], trice[2]])
                        point_full_house.append(point)

        
        
        for trice in index_trice:
            if (self.card_combo == 2 or self.card_combo == -1):
                largest_type = max(self.card_type_sequence.index(self.cards[trice[0]].type), self.card_type_sequence.index(self.cards[trice[1]].type))
                point = self.calculate_point(largest_type, self.cards[trice[0]].number, 'pair')
                if point > self.point_before:
                    point_pair.append(point)
                    index_pair.append([trice[0], trice[1]])

                largest_type = max(self.card_type_sequence.index(self.cards[trice[0]].type), self.card_type_sequence.index(self.cards[trice[2]].type))
                point = self.calculate_point(largest_type, self.cards[trice[0]].number, 'pair')
                if point > self.point_before:
                    point_pair.append(point)
                    index_pair.append([trice[0], trice[2]])

                largest_type = max(self.card_type_sequence.index(self.cards[trice[1]].type), self.card_type_sequence.index(self.cards[trice[2]].type))
                point = self.calculate_point(largest_type, self.cards[trice[1]].number, 'pair')
                if point > self.point_before:
                    point_pair.append(point)
                    index_pair.append([trice[1], trice[2]])

        self.combo['pair'] = index_pair
        self.combo['trice'] = index_trice
        self.combo['straight'] = index_straight
        self.combo['flush'] = index_flush
        self.combo['four-of-a-kind'] = index_four
        self.combo['full-house'] = index_full_house

        self.combo_point['pair'] = point_pair
        self.combo_point['trice'] = point_trice
        self.combo_point['straight'] = point_straight
        self.combo_point['flush'] = point_flush
        self.combo_point['four-of-a-kind'] = point_four
        self.combo_point['full-house'] = point_full_house
            
THREAD_RUNNING = True

class Game:
    def __init__(self):
        self.id = -1
        self.server = Network()
        self.SCREEN_RESOLUTION = (1280, 720)
        self.CAPTION = "Capsa Banting Super"
        self.STATUS_UPDATE = "UPDATE"
        self.STATUS_QUIT = "QUIT"

        self.LOADED_CARD = False
        self.initial_card_index = []
        
        # init pygame
        pygame.init()
        pygame.display.set_caption(self.CAPTION)
        
        # set pygame screen
        self.screen = pygame.display.set_mode(self.SCREEN_RESOLUTION, 0 , 32)

        # load assets
        self.card_factory = CardFactory().load()
        self.background_factory = BackgroundFactory().load()
        self.button_factory = ButtonFactory().load()
        self.back_card_factory = BackCardFactory().load()
        self.CARD_IN_DECK = 13
        self.CARD_SELECTED = 0
        self.CARD_SELECTED_BEFORE = 0

        self.combo_list = ['pair', 'trice', 'straight', 'flush' , 'full-house', 'four-of-a-kind']
        self.MY_TURN = False
        
        # TODO: shuffle on server
        # random.shuffle(self.card_factory.card)

        # set button image to disabled
        self.button_factory.button['play'].index = 2

    def start(self):
        global THREAD_RUNNING
        # TODO: get player card index from server
        # shallow copy

        self.thread_server = threading.Thread(target=self.get_data_from_server)
        self.thread_server.start()

        while self.LOADED_CARD == False:
            pass

        if self.LOADED_CARD == True:
            self.player_card = []
            for index in self.initial_card_index:
                self.player_card.append(self.card_factory.card[index])

        # self.player_card = copy.copy(self.card_factory.card[:13])
        self.player_card.sort()
        self.choosen_card = []
        self.choosen_card_before = []
        counter_button = {
            'pair' : 0,
            'trice' : 0,
            'straight' : 0,
            'flush' : 0,
            'full-house': 0,
            'four-of-a-kind' : 0,
        }
        game_rule = ''

        self.player_card_count = [0] * 4
        self.player_card_count[0] = len(self.player_card)
        self.player_card_count[1] = 13
        self.player_card_count[2] = 13
        self.player_card_count[3] = 13
        self.card_point_before = -1

        point_now = 0

        while True:

            game_rule = GameRule(self.player_card, self.card_point_before)

            for combo_name in self.combo_list:
                if len(game_rule.combo[combo_name]) == 0 :
                    self.button_factory.button[combo_name].index = 2
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    THREAD_RUNNING = False
                    self.server.send(self.STATUS_QUIT, {})
                    self.thread_server.join()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # click on player card
                    exist_select = False
                    counter_card = 0
                    last_card = 0
                    for card in self.player_card:
                        card_rect = card.sprite.get_rect()
                        
                        # if card is not selected the width of bounding box become half of normal
                        if not card.select and card != self.player_card[-1]:
                            card_rect.w = card_rect.w//2
                        # if sprite card is clicked in the bounding box then card is set to selected or not selected
                        if card_rect.collidepoint(mouse_x - card.pos['x'], mouse_y - card.pos['y']):
                            print(card.type, card.number)
                            card.select = not card.select
                        # if card is selected, set the play button to click-able
                        if card.select and self.MY_TURN:
                            exist_select = True
                            counter_card += 1
                            last_card = card
                            self.button_factory.button['play'].index = 0
                    
                    # if no card selected, set the play button to disabled
                    if not exist_select:
                        self.button_factory.button['play'].index = 2

                    if counter_card == 1:
                        point = game_rule.calculate_point(game_rule.card_type_sequence.index(last_card.type), last_card.number, 'single')
                        if point > self.point_before:
                            self.button_factory.button['play'].index = 0
                        else :
                            self.button_factory.button['play'].index = 2

                    # click on button
                    # if button click and not disabled, set the sprite to clicked
                    for button in self.button_factory.button.values():
                        if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 0:
                            button.index = 1

                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    # if play button clicked
                    if self.button_factory.button['play'].sprite[0].get_rect().collidepoint(mouse_x - self.button_factory.button['play'].pos['x'], mouse_y - self.button_factory.button['play'].pos['y']) and self.button_factory.button['play'].index != 2:
                        counter_card = 0
                        self.choosen_card_before = copy.copy(self.choosen_card)
                        self.choosen_card = []
                        choosen_card_index = []
                        for card in self.player_card:
                            if card.select :
                                counter_card += 1
                                self.choosen_card.append(card)
                                choosen_card_index.append(self.card_factory.card.index(card))

                        for card in self.choosen_card:
                            self.player_card.remove(card)

                        data = {}
                        data['id'] = self.id
                        data['play'] = 'PLAY'
                        data['selected_card'] = choosen_card_index
                        data['selected_card_point'] = point_now
                        self.server.send(self.STATUS_UPDATE, data)

                        self.button_factory.button['play'].index = 2

                    for combo_name in self.combo_list:
                        if len(game_rule.combo[combo_name]) == 0 :
                           self.button_factory.button[combo_name].index = 2
                        if self.button_factory.button[combo_name].sprite[0].get_rect().collidepoint(mouse_x - self.button_factory.button[combo_name].pos['x'], mouse_y - self.button_factory.button[combo_name].pos['y']) and self.button_factory.button[combo_name].index != 2:
                            combo = game_rule.combo[combo_name]
                            print(game_rule.card_counter)
                            print(combo)

                            counter_button[combo_name] += 1
                            counter_button[combo_name] %= (len(combo) + 1)
                            index = counter_button[combo_name]-1

                            for card in self.player_card:
                                card.select = False
                            
                            if counter_button[combo_name] > 0 and self.MY_TURN:
                                for idx in combo[index]:
                                    self.player_card[idx].select = True
                                point_now = game_rule.combo_point[combo_name][index]
                                print(point_now)
                                self.button_factory.button['play'].index = 0
                            else :
                                self.button_factory.button['play'].index = 2

                    # if button is clicked, on mouseup set the sprite to click-able
                    for button in self.button_factory.button.values():
                        if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 1:
                            button.index=0
            
            self.set_asset_position()
            self.draw()
            pygame.display.update()

    def get_data_from_server(self):
        global THREAD_RUNNING
        while THREAD_RUNNING :
            print(THREAD_RUNNING)
            message = self.server.server_socket.recv(self.server.BUFFER_SIZE)
            if message:
                message = pickle.loads(message)
                print(message)
                if message['status'] == 'GET_ID':
                    self.id = message['data']['id']
                    self.initial_card_index = message['data']['card_index']
                    self.LOADED_CARD = True

                    if message['data']['turn_player_id'] == self.id:
                        self.MY_TURN = True
                        self.button_factory.button['play'].index = 0
                    else :
                        self.MY_TURN = False

                elif message['status'] == 'BROADCAST':
                    player_id = message['data']['player_id']
                    self.choosen_card_index = message['data']['card_index_now']
                    self.choosen_card_before_index = message['data']['card_index_before']
                    self.choosen_card = []
                    for index in self.choosen_card_index:
                        self.choosen_card.append(self.card_factory.card[index])
                    self.choosen_card_before = []
                    for index in self.choosen_card_before_index:
                        self.choosen_card_before.append(self.card_factory.card[index])

                    for i in range(4):
                        idx = message['data']['player'][player_id]['player_sequence'][i]
                        self.player_card_count[i] = message['data']['player'][idx]['card_count']

                    if message['data']['turn_player_id'] == self.id:
                        self.MY_TURN = True
                        self.button_factory.button['play'].index = 0
                    else :
                        self.MY_TURN = False

                    self.card_point_before = message['data']['card_point_now']
                elif message['status'] == 'BYE':
                    break



    def set_asset_position(self):
        center_position_x = 640
        center_position_y = 360                

        self.CARD_SELECTED_BEFORE = len(self.choosen_card_before)
        self.CARD_SELECTED = len(self.choosen_card)
        self.CARD_IN_DECK = len(self.player_card)


        PADDING_BEFORE = 10
        PADDING = 2
        bounding_box_card_x = ( self.card_factory.card[0].sprite.get_width() + PADDING ) * self.CARD_SELECTED
        bounding_box_card_y = ( self.card_factory.card[0].sprite.get_height() )

        center_position_x -= bounding_box_card_x // 2
        center_position_y -= bounding_box_card_y // 2

        for i in range(self.CARD_SELECTED):
            self.choosen_card[i].pos['y'] = center_position_y
            self.choosen_card[i].pos['x'] = center_position_x + i * ( self.choosen_card[i].sprite.get_width() + PADDING ) 

        for i in range(self.CARD_SELECTED_BEFORE):
            self.choosen_card_before[i].pos['y'] = 200


        # TODO: make a function for set initial position
        # set initial position of button
        self.button_factory.button['play'].set_position(850, 615)
        self.button_factory.button['pass'].set_position(850, 570)

        for i in range(len(self.combo_list)):
            position_y = 670
            position_x = 400 + i * (self.button_factory.button[self.combo_list[i]].sprite[0].get_width()+3)
            self.button_factory.button[self.combo_list[i]].set_position(position_x, position_y)

        # set position of card
        for i in range(self.CARD_IN_DECK):   
            self.player_card[i].pos['y'] = 570
            self.player_card[i].pos['x'] = 400 + i * self.player_card[i].sprite.get_width()//2
            # if card is selected, set position higher 
            if self.player_card[i].select :
                self.player_card[i].pos['y'] -= 32
    
    def draw(self):
        # load assets to the screen -> (image,position)
        self.screen.blit(self.background_factory.background, (0,0))
        self.screen.blit(self.button_factory.button['play'].get_sprite(), self.button_factory.button['play'].position())
        self.screen.blit(self.button_factory.button['pass'].get_sprite(), self.button_factory.button['pass'].position())

        for combo_name in self.combo_list :
            self.screen.blit(self.button_factory.button[combo_name].get_sprite(), self.button_factory.button[combo_name].position())

        # set position of back card player 1
        for i in range(self.player_card_count[1]):
            player_back_card = self.back_card_factory.backcard
            player_back_card = pygame.transform.rotate(player_back_card, 90)
            self.screen.blit(player_back_card, (70, 120 + i * (player_back_card.get_height()//3)))

        for i in range(self.player_card_count[2]):
            player_back_card = self.back_card_factory.backcard
            self.screen.blit(player_back_card, (400 + i * (player_back_card.get_width()//3) , 7))

        for i in range(self.player_card_count[3]):
            player_back_card = self.back_card_factory.backcard
            player_back_card = pygame.transform.rotate(player_back_card, 90)
            self.screen.blit(player_back_card, (1080, 120 + i * (player_back_card.get_height()//3)))

        # load card assets to the screen
        for i in range(len(self.player_card)):
            self.screen.blit(self.player_card[i].sprite, self.player_card[i].position())

        for i in range(len(self.choosen_card)):
            self.screen.blit(self.choosen_card[i].sprite, self.choosen_card[i].position())

        for i in range(len(self.choosen_card_before)):
            self.screen.blit(self.choosen_card_before[i].sprite, self.choosen_card_before[i].position())



        
if __name__ == "__main__":
    app = Game()
    app.start()
