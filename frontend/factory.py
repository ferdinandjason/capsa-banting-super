import os
import pygame

"""
class BaseImage :
    sprite  : pygame.Surface
    position: dict {'x','y}
"""
class BaseImage:
    def __init__(self):
        self.sprite = ''
        self.pos = {
            'x' : 0,
            'y' : 0
        }

    def position(self):
        return (self.pos['x'], self.pos['y'])
    
    def set_position(self, x, y):
        self.pos['x'] = x
        self.pos['y'] = y



"""
class Card:
    type    : clover, diamond, heart, spade
    number  : 1 , 2, ..., 13
    sprite  : pygame.Surface
    select  : boolean True or False
    ongoing : boolean True or False
"""
class Card(BaseImage):
    def __init__(self, types, number, sprite):
        BaseImage.__init__(self)
        self.type = types
        self.number = number
        self.sprite = sprite
        self.select = False
        self.ongoing = False

    def __lt__(self, other):
        if self.number != other.number:
            return self.number < other.number
        else :
            return self.type < other.type

"""
class Button :
    name    : button image
    sprite  : array of pygame.Surface object
    index   : 
        0   -> clickable
        1   -> clicked
        2   -> disabled
"""
class Button(BaseImage):
    def __init__(self, name, sprite_non_pressed, sprite_pressed, sprite_disabled):
        BaseImage.__init__(self)
        self.name = name
        self.sprite = [sprite_non_pressed, sprite_pressed, sprite_disabled]
        self.index = 0

    def get_sprite(self):
        return self.sprite[self.index]


"""
class CardFactory :
    PATH        : path to the folder
    card_dict   : dictionary to save card
    card        : array contain flatten card_dict
"""
class CardFactory:
    def __init__(self):
        self.PATH = os.path.join('.','assets','card')
        self.card_dict = {
            'clover' : [0]*13,
            'diamond' : [0]*13,
            'heart' : [0]*13,
            'spade' : [0]*13,
        } 

    def load(self):
        for root, dirs, files in os.walk(self.PATH):
            card_image_path = [os.path.join(root, file) for file in files]
            self.load_image_path(card_image_path)
        self.flatten(self.card_dict)
        return self

    def load_image_path(self, paths):
        for path in paths: 
            card_type = path.split('_')[2][:-4]
            card_number = int(path.split('_')[1])
            card_value = card_number
            card_sprite = pygame.image.load(path).convert()
            if card_value == 1 : card_value = 14
            if card_value == 2 : card_value = 15
            self.card_dict[card_type][card_number-1] = Card(card_type, card_value, card_sprite)

    def flatten(self, card_dict):
        self.card = self.card_dict['diamond'] + self.card_dict['clover'] + self.card_dict['heart'] + self.card_dict['spade']

"""
class BackgroundFactory :
    PATH        : path to the image
    background  : pygame.Surface object
"""
class BackgroundFactory:
    def __init__(self):
        self.PATH = {}
        self.PATH['game'] = os.path.join('.','assets','background.jpg')
        self.PATH['winner'] = os.path.join('.', 'assets', 'winer.jpg')
        self.PATH['welcome'] = os.path.join('.', 'assets', 'welcome.jpg')
        self.background = {}

    def load(self):
        self.background['game'] = pygame.image.load(self.PATH['game']).convert()
        self.background['winner'] = pygame.transform.scale(pygame.image.load(self.PATH['winner']).convert(), (1280,720))
        self.background['welcome'] = pygame.transform.scale(pygame.image.load(self.PATH['welcome']).convert(), (1280,720))
        return self

"""
class ButtonFactory :
    PATH        : path to the folder
    button_dict : dictionary to save image
    button      : dictionary to map between button name and button sprite
"""
class ButtonFactory:
    def __init__(self):
        self.PATH = os.path.join('.','assets','button')
        self.button_dict = {}
        self.button = {}

    def load(self):
        for root, dirs, files in os.walk(self.PATH):
            button_image_path = [os.path.join(root, file) for file in files]
            self.load_image_path(button_image_path)
        self.load_button()
        return self

    def load_image_path(self, paths):
        for path in paths: 
            button_name = path.split(os.sep)[-1].split('.')[0]
            self.button_dict[button_name] = pygame.image.load(path).convert()
            self.button_dict[button_name] = pygame.transform.scale(self.button_dict[button_name], (70,40))

    def load_button(self):
        print(self.button_dict)
        self.button['play'] = Button('play', self.button_dict['play'], self.button_dict['play-pressed'], self.button_dict['play-disabled'])
        self.button['pass'] = Button('pass', self.button_dict['pass'], self.button_dict['pass-pressed'], self.button_dict['pass-disabled'])
        self.button['pair'] = Button('pair', self.button_dict['pair'], self.button_dict['pair-pressed'], self.button_dict['pair-disabled'])
        self.button['trice'] = Button('trice', self.button_dict['trice'], self.button_dict['trice-pressed'], self.button_dict['trice-disabled'])
        self.button['straight'] = Button('straight', self.button_dict['straight'], self.button_dict['straight-pressed'], self.button_dict['straight-disabled'])
        self.button['flush'] = Button('flush', self.button_dict['flush'], self.button_dict['flush-pressed'], self.button_dict['flush-disabled'])
        self.button['four-of-a-kind'] = Button('four-of-a-kind', self.button_dict['four-of-a-kind'], self.button_dict['four-of-a-kind-pressed'], self.button_dict['four-of-a-kind-disabled'])
        self.button['full-house'] = Button('full-house', self.button_dict['full-house'], self.button_dict['full-house-pressed'], self.button_dict['full-house-disabled'])

class BackCardFactory:
    def __init__(self):
        self.PATH = os.path.join('.','assets','card_back.png')

    def load(self):
        self.backcard = pygame.image.load(self.PATH).convert_alpha()
        return self


class FontFactory:
    def __init__(self):
        self.PATH = os.path.join('.','assets','font', 'ConnectionII.otf')

    def load(self):
        return self
    
    def make_font(self, size):
        return pygame.font.Font(self.PATH, size)