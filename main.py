from pygame import Color

from game import Game, CellOptions, BoardOptions


def main():
    game = Game(CellOptions(10, 10, alive_color=Color(255, 255, 255), dead_color=Color(0, 0, 0)),
                BoardOptions(100, 100, Color(127, 127, 127)))
    game.run()


if __name__ == "__main__":
    main()
