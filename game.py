import random
from typing import Optional
import arcade
import arcade.gui

from card import Card
from constants import *


class StartView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.DARTMOUTH_GREEN)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Welcome to Solitaire!", SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4,
                         arcade.color.GOLD, font_size=60, anchor_x="center")
        arcade.draw_text("Choose Your Game Mode:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
                         arcade.color.WHITE, font_size=28, anchor_x="center")
        arcade.draw_text("Press 1 for Classic Solitaire", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                         arcade.color.WHITE, font_size=28, anchor_x="center")
        arcade.draw_text("Press 2 for Vegas Rules", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120,
                         arcade.color.WHITE, font_size=28, anchor_x="center")

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.KEY_1:
            game_view = GameView(vegas_rules=False)
            game_view.setup()
            self.window.show_view(game_view)
        elif symbol == arcade.key.KEY_2:
            game_view = GameView(vegas_rules=True)
            game_view.setup()
            self.window.show_view(game_view)


class GameView(arcade.View):

    def __init__(self, vegas_rules=False):
        super().__init__()

        self.vegas_rules = vegas_rules

        self.card_list: Optional[arcade.SpriteList] = None
        self.game_paused = False
        self.is_game_won = False

        arcade.set_background_color(arcade.color.DARTMOUTH_GREEN)

        self.pause_text = "Press 'P' to Pause"
        self.restart_text = "Press 'R' to Restart"

        self.held_cards = None
        self.held_cards_original_position = None

        self.pile_mat_list = None
        self.piles = None

    def setup(self):

        self.held_cards = []
        self.score = -52 if self.vegas_rules else 0
        self.held_cards_original_position = []

        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.AMAZON)
        pile.position = START_X, BOTTOM_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.AMAZON)
        pile.position = START_X + X_SPACING, BOTTOM_Y
        self.pile_mat_list.append(pile)

        for i in range(7):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.AMAZON)
            pile.position = START_X + i * X_SPACING, MIDDLE_Y
            self.pile_mat_list.append(pile)

        for i in range(4):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.AMAZON)
            pile.position = START_X + i * X_SPACING, TOP_Y
            self.pile_mat_list.append(pile)

        self.card_list = arcade.SpriteList()

        for card_suit in CARD_SUITS:
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                card.position = START_X, BOTTOM_Y
                self.card_list.append(card)

        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        self.piles = [[] for _ in range(PILE_COUNT)]

        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

        for pile_no in range(PLAY_PILE_1, PLAY_PILE_7 + 1):

            for j in range(pile_no - PLAY_PILE_1 + 1):
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()

                self.piles[pile_no].append(card)

                card.position = self.pile_mat_list[pile_no].position

                self.pull_to_top(card)

        for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            self.piles[i][-1].face_up()

        if self.vegas_rules:

            pass
        else:

            pass

    def build_foundation(self, card: Card):
        # Check if the card can be placed on the foundation in ascending order and matching suit
        suit = card.suit
        if card.get_numeric_value() == 1:  # Ace can be placed on an empty foundation pile
            return True

        foundation_pile = None
        for i in range(TOP_PILE_1, TOP_PILE_4 + 1):
            if len(self.piles[i]) == 0:
                if card.get_numeric_value() == 1:
                    foundation_pile = self.piles[i]
                    break
            else:
                top_card = self.piles[i][-1]
                if card.suit == suit and card.get_numeric_value() == top_card.get_numeric_value() + 1:
                    foundation_pile = self.piles[i]
                    break

        if foundation_pile is not None:
            # Additional check for alternating colors
            if len(foundation_pile) > 0:
                top_card = foundation_pile[-1]
                if card.is_opposite_color(top_card):
                    return False
            foundation_pile.append(card)
            self.score += 10  # Increment the score by 10 when a card is added to the foundation pile
            return True  # Return True if the card is successfully added to the foundation pile

        return False

    def build_sequence(self, card: Card):
        for pile in self.piles:
            if len(pile) > 0:
                top_card = pile[-1]
                if card.value == CARD_VALUES[CARD_VALUES.index(top_card.value) + 1]:
                    # Additional check for alternating colors
                    if card.color != top_card.color:
                        return pile
        return None

    def deal_from_stock(self):
        if len(self.piles[BOTTOM_FACE_DOWN_PILE]) > 0:
            card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
            card.face_up()
            self.piles[BOTTOM_FACE_UP_PILE].append(card)
            return True
        return False

    def check_win_condition(self):
        for pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1):
            if len(self.piles[
                       pile_index]) != 13:  # 13 cards of each suit (Ace to King) in the foundation pile for a win
                return False
        return True

    def on_draw(self):
        self.clear()

        if self.game_paused:
            arcade.set_background_color(arcade.color.DARK_GRAY)
            arcade.draw_text("Game Paused", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.WHITE, font_size=50, anchor_x="center")
            arcade.draw_text("Press the 'SPACE' to unpause", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                             arcade.color.WHITE, font_size=30, anchor_x="center")
        else:
            arcade.set_background_color(arcade.color.DARTMOUTH_GREEN)
            if self.pause_text:
                arcade.draw_text("Press 'SPACE' to Pause", SCREEN_WIDTH - 40, SCREEN_HEIGHT - 10, arcade.color.WHITE,
                                 font_size=14, align="right", anchor_x="right", anchor_y="top",
                                 width=500)
            if self.restart_text:
                arcade.draw_text("Press 'R' to Restart", SCREEN_WIDTH - 40, SCREEN_HEIGHT - 30, arcade.color.WHITE,
                                 font_size=14, align="right", anchor_x="right", anchor_y="top",
                                 width=500)
            # Display the current score on the screen in the bottom right
            score_text = f"Score: {self.score}"
            arcade.draw_text(score_text, SCREEN_WIDTH - 40, 40, arcade.color.WHITE, font_size=20, anchor_x="right",
                             anchor_y="bottom")

            self.pile_mat_list.draw()
            self.card_list.draw()

    def pull_to_top(self, card: arcade.Sprite):

        self.card_list.remove(card)
        self.card_list.append(card)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.R:
            self.setup()

        if symbol == arcade.key.SPACE:  # Check for space bar press
            self.toggle_pause()

    def toggle_pause(self):
        self.game_paused = not self.game_paused
        arcade.pause(self.game_paused)  # Pause or unpause the game using arcade.pause

    def on_mouse_press(self, x, y, button, key_modifiers):
        if self.game_paused:  # Check if the game is paused
            return  # Ignore mouse press events when the game is paused

        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        if len(cards) > 0:

            primary_card = cards[-1]
            assert isinstance(primary_card, Card)

            pile_index = self.get_pile_for_card(primary_card)

            if pile_index == BOTTOM_FACE_DOWN_PILE:

                for i in range(3):

                    if len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                        break

                    card = self.piles[BOTTOM_FACE_DOWN_PILE][-1]

                    card.face_up()

                    card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position

                    self.piles[BOTTOM_FACE_DOWN_PILE].remove(card)

                    self.piles[BOTTOM_FACE_UP_PILE].append(card)

                    self.pull_to_top(card)

            elif primary_card.is_face_down:

                primary_card.face_up()
            else:

                self.held_cards = [primary_card]

                self.held_cards_original_position = [self.held_cards[0].position]

                self.pull_to_top(self.held_cards[0])

                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
                    self.held_cards.append(card)
                    self.held_cards_original_position.append(card.position)
                    self.pull_to_top(card)

        else:

            mats = arcade.get_sprites_at_point((x, y), self.pile_mat_list)

            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)

                if mat_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:

                    temp_list = self.piles[BOTTOM_FACE_UP_PILE].copy()
                    for card in reversed(temp_list):
                        card.face_down()
                        self.piles[BOTTOM_FACE_UP_PILE].remove(card)
                        self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
                        card.position = self.pile_mat_list[BOTTOM_FACE_DOWN_PILE].position

    def remove_card_from_pile(self, card):

        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def get_pile_for_card(self, card):

        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def move_card_to_new_pile(self, card, pile_index):

        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        if self.game_paused:
            return

        if len(self.held_cards) == 0:
            return

        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        if arcade.check_for_collision(self.held_cards[0], pile):
            pile_index = self.pile_mat_list.index(pile)

            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                pass

            elif PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
                if len(self.piles[pile_index]) > 0:
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = top_card.center_x, top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = pile.center_x, pile.center_y - CARD_VERTICAL_OFFSET * i

                # Check if the move to the play pile is valid
                if self.check_for_valid_stack(self.held_cards,
                                              pile_index):  # Ensure cards are in sequence and alternating colors
                    for card in self.held_cards:
                        self.move_card_to_new_pile(card, pile_index)
                    reset_position = False

            elif TOP_PILE_1 <= pile_index <= TOP_PILE_4 and len(self.held_cards) == 1:
                self.held_cards[0].position = pile.position

                # Check if the move to the foundation pile is valid
                if self.build_foundation(self.held_cards[0]):  # Ensure card is placed in foundation correctly
                    self.move_card_to_new_pile(self.held_cards[0], pile_index)
                    reset_position = False

        if reset_position:
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):

        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def on_update(self, delta_time: float):
        if self.game_paused:
            return

        for pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1):
            if len(self.piles[pile_index]) != 13:
                self.is_game_won = False
                break
        else:
            self.is_game_won = True

    def check_for_valid_move(self, card, pile_index):
        target_pile = self.piles[pile_index]

        if len(target_pile) == 0 and card.value == 13:  # Empty pile can only receive a king (value is 13)
            return True

        if len(target_pile) > 0:
            top_card = target_pile[-1]

            # Check if the card's value is one less than the top card's value
            # and the card's suit is different from the top card's suit
            if card.value == top_card.value - 1 and card.is_opposite_color(top_card):
                return True

        else:
            return False

    def update_score(self, score_delta):
        if self.vegas_rules:

            self.score += score_delta
        else:

            self.score += score_delta

    def perform_action_and_update_score(self, action):

        if action == "waste_to_tableau" or action == "waste_to_foundation" or action == "tableau_to_foundation" or action == "turn_tableau_card":
            self.update_score(5)
        elif action == "foundation_to_tableau":
            self.update_score(-15)
        elif action == "recycle_waste_by_ones":
            self.update_score(-50)

    def check_for_valid_stack(self, cards, pile_index):
        if len(cards) == 0:
            return False

        target_pile = self.piles[pile_index]

        if len(target_pile) == 0 and cards[
            0].get_numeric_value() == 13:  # Empty pile can only receive a king (value is 13)
            return True

        if len(target_pile) > 0:
            top_card = target_pile[-1]

            # Check if the bottom card's value is one less than the top card's value
            # and the bottom card's suit is different from the top card's suit
            if cards[0].get_numeric_value() == top_card.get_numeric_value() - 1 and cards[0].is_opposite_color(
                    top_card):
                return True

        return False
