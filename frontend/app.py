import sys
import copy
import random
import pygame
import itertools
import threading

from factory import *
from network import *
from rule import Rule

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
        self.font_factory = FontFactory().load()

        # var counter
        self.point_now = 0
        self.CARD_IN_DECK = 13
        self.CARD_SELECTED = 0
        self.CARD_SELECTED_BEFORE = 0
        self.count_player = 1

        self.player_card = []

        self.player_card_count = [0] * 4
        self.player_card_count[0] = 13
        self.player_card_count[1] = 13
        self.player_card_count[2] = 13
        self.player_card_count[3] = 13
        self.player_card_order = 0
        self.card_point_before = 0

        self.counter_button = {
            'pair' : 0,
            'trice' : 0,
            'straight' : 0,
            'flush' : 0,
            'full-house': 0,
            'four-of-a-kind' : 0,
        }

        # combo list
        self.combo_list = ['pair', 'trice', 'straight', 'flush' , 'full-house', 'four-of-a-kind']

        # boolean for turn
        self.MY_TURN = False

        # set button image to disabled
        self.button_factory.button['play'].index = 2

        # game state
        self.GAME_STATE = 1

        self.STATE_WELCOME = 1
        self.STATE_GAME = 2
        self.STATE_WINNER = 3

        # initialize Rule class
        self.game_rule = ''

        self.tutorial = pygame.image.load("./assets/tutorial-2.png").convert()


    def init_player_card(self):
        # check if card is loaded or not
        while self.LOADED_CARD == False:
            pass

        # if loaded , render it to player's card
        if self.LOADED_CARD == True:
            self.player_card = []
            for index in self.initial_card_index:
                self.player_card.append(self.card_factory.card[index])

        self.player_card.sort()
        self.choosen_card = []
        self.choosen_card_before = []


    def start(self):
        # set global threading
        global THREAD_RUNNING

        self.thread_server = threading.Thread(target=self.get_data_from_server)
        self.thread_server.start()

        self.init_player_card()

        while True:
            if self.GAME_STATE == self.STATE_WELCOME :
                self.handle_welcome()
            if self.GAME_STATE == self.STATE_GAME :
                self.handle_game()
            if self.GAME_STATE == self.STATE_WINNER :
                self.handle_winner()

    def handle_game(self):
        self.game_rule = Rule(self.player_card, self.card_point_before)
        self.card_point_before = self.game_rule.point_before

        # check if combo is avaiable
        combo_avaiable = False
        for combo_name in self.combo_list:
            if len(self.game_rule.combo[combo_name]) != 0:
                combo_avaiable = True                    
                self.button_factory.button[combo_name].index = 0
            else : 
                self.button_factory.button[combo_name].index = 2

        if not combo_avaiable:
            self.button_factory.button['play'].index = 2

        # check if is possible to make move
        exist_select = False
        counter_card = 0
        one_card_selected = ''
        for card in self.player_card:
            if card.select and self.MY_TURN:
                exist_select = True
                counter_card += 1
                one_card_selected = card
                self.button_factory.button['play'].index = 0
        
        # if no card selected, set the play button to disabled
        if not exist_select:
            self.button_factory.button['play'].index = 2

        if counter_card == 1:
            self.point_now = self.game_rule.calculate_point(self.game_rule.card_type_sequence.index(one_card_selected.type), one_card_selected.number, 'single')
            if self.point_now > self.card_point_before:
                self.button_factory.button['play'].index = 0
            else :
                self.button_factory.button['play'].index = 2


        # HANDLING PYGAME MAIN EVENT
        for event in pygame.event.get():
            # if current event is quit
            if event.type == pygame.QUIT:
                THREAD_RUNNING = False
                self.server.send(self.STATUS_QUIT, {})
                self.thread_server.join()
                sys.exit()
            
            # if current event is click
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                exist_select = False
                counter_card = 0
                for card in self.player_card:
                    card_rect = card.sprite.get_rect()
                    
                    # if card is not selected the width of bounding box become half of normal
                    # if sprite card is clicked in the bounding box then card is set to selected or not selected
                    # if card is selected, set the play button to click-able
                    if not card.select and card != self.player_card[-1]:
                        card_rect.w = card_rect.w//2
                    if card_rect.collidepoint(mouse_x - card.pos['x'], mouse_y - card.pos['y']):
                        print(card.type, card.number)
                        card.select = not card.select
                    if card.select and self.MY_TURN:
                        exist_select = True
                        counter_card += 1
                        last_card = card
                        self.button_factory.button['play'].index = 0
                
                # if no card selected, set the play button to disabled
                if not exist_select:
                    self.button_factory.button['play'].index = 2

                # click on button
                # if button click and not disabled, set the sprite to clicked
                for button in self.button_factory.button.values():
                    if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 0:
                        button.index = 1

            # if current event is clicked
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos

                # PLAY CLICKED
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

                    if counter_card == 1:
                        self.point_now = self.game_rule.calculate_point(self.game_rule.card_type_sequence.index(one_card_selected.type), one_card_selected.number, 'single')
                        if self.point_now > self.card_point_before:
                            self.button_factory.button['play'].index = 0

                    for card in self.choosen_card:
                        self.player_card.remove(card)

                    # send current play state to server
                    data = {}
                    data['id'] = self.id
                    data['play'] = 'PLAY'
                    data['selected_card'] = choosen_card_index
                    data['selected_card_point'] = self.point_now
                    self.server.send(self.STATUS_UPDATE, data)

                    self.button_factory.button['play'].index = 2

                # PASS CLICKED
                if self.button_factory.button['pass'].sprite[0].get_rect().collidepoint(mouse_x - self.button_factory.button['pass'].pos['x'], mouse_y - self.button_factory.button['pass'].pos['y']) and self.button_factory.button['pass'].index != 2:
                    # send if player is passes
                    data = {}
                    data['id'] = self.id
                    data['play'] = 'PASS'
                    self.server.send(self.STATUS_UPDATE, data)

                # COMBO BUTTON SET STATUS
                for combo_name in self.combo_list:
                    if len(self.game_rule.combo[combo_name]) == 0 :
                        self.button_factory.button[combo_name].index = 2
                    if self.button_factory.button[combo_name].sprite[0].get_rect().collidepoint(mouse_x - self.button_factory.button[combo_name].pos['x'], mouse_y - self.button_factory.button[combo_name].pos['y']) and self.button_factory.button[combo_name].index != 2:
                        combo = self.game_rule.combo[combo_name]

                        self.counter_button[combo_name] += 1
                        self.counter_button[combo_name] %= (len(combo) + 1)
                        index = self.counter_button[combo_name]-1

                        for card in self.player_card:
                            card.select = False
                        
                        if self.counter_button[combo_name] > 0 and self.MY_TURN:
                            for idx in combo[index]:
                                self.player_card[idx].select = True
                            self.point_now = self.game_rule.combo_point[combo_name][index]
                            self.button_factory.button['play'].index = 0
                        else :
                            self.button_factory.button['play'].index = 2

                # OTHER BUTTON SET STATUS
                for button in self.button_factory.button.values():
                    if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 1:
                        button.index=0
        
        self.set_asset_position()
        self.draw()
        pygame.display.update()

    def handle_welcome(self):
        welcome_title_text = "WELCOME TO CAPSA BANTING SUPER"
        welcome_title_font = self.font_factory.make_font(50)
        welcome_title_surface = welcome_title_font.render(welcome_title_text, 0, (255,255,255))

        player_text = "Player - {}".format(str(self.id+1))
        player_font = self.font_factory.make_font(50)
        player_surface = player_font.render(player_text, 0, (255,255,255))

        waiting_text = "waiting player-({}/4)...".format(self.count_player)
        waiting_font = self.font_factory.make_font(50)
        waiting_surface = waiting_font.render(waiting_text, 0, (255,255,255))

        instruction_text = "Game will start as soon as the player count reaches four"
        instruction_font = self.font_factory.make_font(30)
        instruction_surface = instruction_font.render(instruction_text, 0, (255,255,255))

        question_mark = "?"
        question_font = self.font_factory.make_font(30)
        question_surface = question_font.render(question_mark, 0, (255,255,255))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                THREAD_RUNNING = False
                self.server.send(self.STATUS_QUIT, {})
                self.thread_server.join()

                sys.exit()

        self.screen.blit(self.background_factory.background['welcome'], (0,0))
        self.screen.blit(welcome_title_surface, (640 - welcome_title_surface.get_width()//2 , 150 - welcome_title_surface.get_height()//2))
        self.screen.blit(player_surface,        (640 - player_surface.get_width()//2        , 250 - player_surface.get_height()//2))
        self.screen.blit(waiting_surface,       (640 - waiting_surface.get_width()//2       , 400 - waiting_surface.get_height()//2))
        self.screen.blit(instruction_surface,   (640 - instruction_surface.get_width()//2   , 470 - instruction_surface.get_height()//2))
        self.screen.blit(question_surface,      (0,0))

        qs = question_surface.get_rect()
        if qs.collidepoint(pygame.mouse.get_pos()) : 
            self.screen.blit(self.tutorial,  (640 - self.tutorial.get_width()//2 , 360 - self.tutorial.get_height()//2))


        pygame.display.update()


    def handle_winner(self):
        winner_text = "Player-{} win the Game!".format(self.victory_id+1)
        winner_font = self.font_factory.make_font(40)
        winner_surface = winner_font.render(winner_text, 0, (0,0,0))

        thankyou_text1 = "Thank you for playing this game!"
        thankyou_font1 = self.font_factory.make_font(30)
        thankyou_surface1 = thankyou_font1.render(thankyou_text1, 0, (0,0,0))

        thankyou_text2 = "Don't forget to share to your friend"
        thankyou_font2 = self.font_factory.make_font(30)
        thankyou_surface2 = thankyou_font2.render(thankyou_text2, 0, (0,0,0))

        thankyou_text3 = "Press x on right top window to quit"
        thankyou_font3 = self.font_factory.make_font(30)
        thankyou_surface3 = thankyou_font3.render(thankyou_text3, 0, (0,0,0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                THREAD_RUNNING = False
                self.server.send(self.STATUS_QUIT, {})
                self.thread_server.join()

                sys.exit()

        self.screen.blit(self.background_factory.background['winner'], (0,0))
        self.screen.blit(winner_surface,    (655 - winner_surface.get_width()//2    , 270 - winner_surface.get_height()//2))
        self.screen.blit(thankyou_surface1, (655 - thankyou_surface1.get_width()//2 , 360 - thankyou_surface1.get_height()//2))
        self.screen.blit(thankyou_surface2, (655 - thankyou_surface2.get_width()//2 , 400 - thankyou_surface2.get_height()//2))
        self.screen.blit(thankyou_surface3, (655 - thankyou_surface3.get_width()//2 , 440 - thankyou_surface3.get_height()//2))

        pygame.display.update()

    def get_data_from_server(self):
        global THREAD_RUNNING
        while THREAD_RUNNING :
            message = self.server.server_socket.recv(self.server.BUFFER_SIZE)
            if message:
                message = pickle.loads(message)
                print(message)

                # SERVER BROADCASTS WELCOME NEW PLAYER
                if message['status'] == 'WELCOME':
                    self.count_player = message['data']['count_player']
                    self.player = message['data']['player']
                    if self.count_player == 4:
                        self.GAME_STATE = self.STATE_GAME

                # SERVER BROADCASTS THAT GAME IS BEGIN
                elif message['status'] == 'START':
                    self.GAME_STATE = self.STATE_GAME

                # SERVER REPLY CURRENT PLAYER ID AND PLAYER CARD
                elif message['status'] == 'GET_ID':
                    self.id = message['data']['id']
                    self.initial_card_index = message['data']['card_index']
                    self.count_player = message['data']['count_player']
                    self.LOADED_CARD = True

                    self.current_player_id = message['data']['turn_player_id']

                    if message['data']['turn_player_id'] == self.id:
                        self.MY_TURN = True
                        self.button_factory.button['play'].index = 0
                        self.button_factory.button['pass'].index = 0
                    else :
                        self.MY_TURN = False
                        self.button_factory.button['play'].index = 2
                        self.button_factory.button['pass'].index = 2

                    if self.count_player == 4:
                        self.GAME_STATE = self.STATE_GAME

                # SERVER BROADCASTS FULL GAME STATE 
                elif message['status'] == 'BROADCAST':
                    player_id = message['data']['player_id']
                    self.choosen_card_index = message['data']['card_index_now']
                    self.choosen_card_before_index = message['data']['card_index_before']
                    self.choosen_card = []
                    if len(self.choosen_card_index) > 0 : 
                        for index in self.choosen_card_index:
                            self.choosen_card.append(self.card_factory.card[index])
                    self.choosen_card_before = []
                    for index in self.choosen_card_before_index:
                        self.choosen_card_before.append(self.card_factory.card[index])

                    for i in range(4):
                        idx = message['data']['player'][player_id]['player_sequence'][i]
                        self.player_card_count[i] = message['data']['player'][idx]['card_count']

                    self.player_card_order = message['data']['player'][player_id]['player_sequence'].index(message['data']['turn_player_id'])
                    self.current_player_id = message['data']['turn_player_id']

                    if message['data']['turn_player_id'] == self.id:
                        self.MY_TURN = True
                        self.button_factory.button['play'].index = 0
                        self.button_factory.button['pass'].index = 0
                    else :
                        self.MY_TURN = False
                        self.button_factory.button['play'].index = 2
                        self.button_factory.button['pass'].index = 2

                    self.card_point_before = message['data']['card_point_now']

                # SERVER DECIDED THE WINNER BASED ON GAME STATE AND DATA
                elif message['status'] == 'WINNER' :
                    self.GAME_STATE = self.STATE_WINNER
                    self.victory_id = message['data']['player_id']

                # SERVER REPLY FOR QUIT EVENT
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

        if self.MY_TURN :
            self.turn_text = "Your Turn"
        else :
            self.turn_text = "Player-{} Turn".format(self.current_player_id+1)

        self.turn_font = self.font_factory.make_font(36)
        self.turn_surface = self.turn_font.render(self.turn_text, 0, (255,255,255))

    
    def draw(self):
        # load assets to the screen -> (image,position)
        self.screen.blit(self.background_factory.background['game'], (0,0))
        self.screen.blit(self.button_factory.button['play'].get_sprite(), self.button_factory.button['play'].position())
        self.screen.blit(self.button_factory.button['pass'].get_sprite(), self.button_factory.button['pass'].position())

        self.screen.blit(self.turn_surface,       (1120 - self.turn_surface.get_width()//2       , 670 - self.turn_surface.get_height()//2))

        for combo_name in self.combo_list :
            self.screen.blit(self.button_factory.button[combo_name].get_sprite(), self.button_factory.button[combo_name].position())

        # set position of back card player 1
        for i in range(self.player_card_count[1]):
            player_back_card = self.back_card_factory.backcard
            player_back_card = pygame.transform.rotate(player_back_card, 90)
            if self.player_card_order == 1:
                self.screen.blit(player_back_card, (90, 120 + i * (player_back_card.get_height()//3)))
            else :
                self.screen.blit(player_back_card, (70, 120 + i * (player_back_card.get_height()//3)))

        for i in range(self.player_card_count[2]):
            player_back_card = self.back_card_factory.backcard
            if self.player_card_order == 2:
                self.screen.blit(player_back_card, (400 + i * (player_back_card.get_width()//3) , 27))
            else :
                self.screen.blit(player_back_card, (400 + i * (player_back_card.get_width()//3) , 7))

        for i in range(self.player_card_count[3]):
            player_back_card = self.back_card_factory.backcard
            player_back_card = pygame.transform.rotate(player_back_card, 90)
            if self.player_card_order == 3:
                self.screen.blit(player_back_card, (1060, 100 + i * (player_back_card.get_height()//3)))
            else:
                self.screen.blit(player_back_card, (1080, 100 + i * (player_back_card.get_height()//3)))

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
