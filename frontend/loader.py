import os
import pygame

class CardLoader:
    def __init__(self):
        self.PATH = './assets'
        self.cards = {
            'clover' : [0]*14,
            'diamond' : [0]*14,
            'heart' : [0]*14,
            'spade' : [0]*14,
        }

    def load(self):
        for root, dirs, files in os.walk(self.PATH):
            card_image_path = [os.path.join(root, file) for file in files]
            self.load_image_path(card_image_path)
        return self.cards

    def load_image_path(self, paths):
        for path in paths: 
            card_type = path.split('_')[2][:-4]
            card_number = int(path.split('_')[1])
            card_sprite = pygame.image.load(path).convert()
            self.cards[card_type][card_number] = card_sprite

    