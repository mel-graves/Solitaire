import arcade

from constants import *


class Card(arcade.Sprite):

    def __init__(self, suit, value, scale=1):
        self.suit = suit
        self.value = value

        self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"
        self.face_down_image = ":resources:images/cards/cardBack_red5.png"
        self.is_face_up = False
        super().__init__(self.face_down_image, scale, hit_box_algorithm="None")

    def face_down(self):
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    def is_opposite_color(self, other_card):
        if self.suit == "Hearts" or self.suit == "Diamonds":
            return other_card.suit == "Clubs" or other_card.suit == "Spades"
        else:
            return other_card.suit == "Hearts" or other_card.suit == "Diamonds"

    def get_numeric_value(self):
        numeric_values = {
            'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
        }
        return numeric_values[self.value]

    @property
    def is_face_down(self):
        return not self.is_face_up
