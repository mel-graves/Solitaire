import os
import sys

import arcade
from game import StartView

SCREEN_WIDTH = 990
SCREEN_HEIGHT = 760
SCREEN_TITLE = "Solitaire"


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
