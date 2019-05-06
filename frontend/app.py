import sys
import copy
import random
import pygame

from loader import CardLoader, BackgroundLoader, ButtonLoader

class Game:
    def __init__(self):
        self.SCREEN_RESOLUTION = (1280, 720)
        self.CAPTION = "Capsa Banting Super"

        # init pygame
        pygame.init()
        pygame.display.set_caption(self.CAPTION)
        
        # set pygame screen
        self.screen = pygame.display.set_mode(self.SCREEN_RESOLUTION, 0 , 32)

        # load assets
        self.card_loader = CardLoader().load()
        self.background_loader = BackgroundLoader().load()
        self.button_loader = ButtonLoader().load()
        
        # TODO: shuffle on server
        random.shuffle(self.card_loader.card)

        # set button image to disabled
        self.button_loader.button['play'].index = 2

    def start(self):
        # TODO: get player card index from server
        # shallow copy
        player_card = copy.copy(self.card_loader.card[:13])
        player_card.sort()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # click on player card
                    exist_select = False
                    for card in player_card:
                        card_rect = card.sprite.get_rect()
                        
                        # if card is not selected the width of bounding box become half of normal
                        if not card.select and card != player_card[-1]:
                            card_rect.w = card_rect.w//2
                        # if sprite card is clicked in the bounding box then card is set to selected or not selected
                        if card_rect.collidepoint(mouse_x - card.pos['x'], mouse_y - card.pos['y']):
                            print(card.type, card.number)
                            card.select = not card.select
                        # if card is selected, set the play button to click-able
                        if card.select:
                            exist_select = True
                            self.button_loader.button['play'].index = 0
                    
                    # if no card selected, set the play button to disabled
                    if not exist_select:
                        self.button_loader.button['play'].index = 2

                    # click on button
                    # if button click and not disabled, set the sprite to clicked
                    for button in self.button_loader.button.values():
                        if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 0:
                            button.index = 1

                if event.type == pygame.MOUSEBUTTONUP:
                    # if button is clicked, on mouseup set the sprite to click-able
                    for button in self.button_loader.button.values():
                        if button.sprite[0].get_rect().collidepoint(mouse_x - button.pos['x'], mouse_y - button.pos['y']) and button.index == 1:
                            button.index=0

            # TODO: make a function for set initial position
            # set initial position of button
            self.button_loader.button['play'].pos['x'] = 850
            self.button_loader.button['play'].pos['y'] = 650

            self.button_loader.button['pass'].pos['x'] = 850
            self.button_loader.button['pass'].pos['y'] = 600

            # load assets to the screen -> (image,position)
            self.screen.blit(self.background_loader.background, (0,0))
            self.screen.blit(self.button_loader.button['play'].get_sprite(), self.button_loader.button['play'].position())
            self.screen.blit(self.button_loader.button['pass'].get_sprite(), self.button_loader.button['pass'].position())

            # set position of card
            for i in range(13):   
                player_card[i].pos['y'] = 600
                player_card[i].pos['x'] = 400 + i * player_card[i].sprite.get_width()//2
                # if card is selected, set position higher 
                if player_card[i].select :
                    player_card[i].pos['y'] -= 32

            # load card assets to the screen
            for i in range(13):
                self.screen.blit(player_card[i].sprite, player_card[i].position())

            pygame.display.update()

                
                
        
if __name__ == "__main__":
    app = Game()
    app.start()
