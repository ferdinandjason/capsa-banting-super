import sys
import copy
import pygame

from loader import CardLoader

class Application:
    def __init__(self):
        self.SCREEN_RESOLUTION = (1280, 720)
        self.CAPTION = "Capsa Banting Super"

        pygame.init()
        pygame.display.set_caption(self.CAPTION)
        
        self.screen = pygame.display.set_mode(self.SCREEN_RESOLUTION, 0, 32)

        self.cards = CardLoader().load()

    def start(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            player_card = copy.copy(self.cards['spade'])
            player_card_rect  = [[0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0], [0,0]]

            for i in range(1,14):
                player_card_rect[i][1] = 600
                player_card_rect[i][0] = 400 + i * player_card[i].get_width()//2

            for i in range(1,14):
                self.screen.blit(player_card[i], (player_card_rect[i][0], player_card_rect[i][1]))

            pygame.display.update()

                
                
        
if __name__ == "__main__":
    app = Application()
    app.start()
