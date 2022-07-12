from dataclasses import dataclass

import pygame
from pygame.color import Color
from pygame.event import Event


@dataclass
class CellOptions:
    width: int
    height: int
    alive_color: Color
    dead_color: Color


@dataclass
class BoardOptions:
    width: int
    height: int
    bg_color: Color


class Game:
    NEW_GENERATION_EVENT = 6969

    def __init__(self, cell: CellOptions, board: BoardOptions, time_per_generation: int = 100) -> None:
        self.cell = cell
        self.board = board
        self.surface = pygame.display.set_mode([cell.width * board.width, cell.height * board.height])
        self.surface.fill(board.bg_color)

        self.range_w = range(board.width)
        self.range_h = range(board.height)

        self.cells = self.init_cells()

        self.is_running = False
        self.is_mouse_down = False
        self.is_mouse_reviving = False
        self.is_mouse_killing = False
        self.is_generation_paused = True

        self.time_per_generation = time_per_generation

    def init_cells(self) -> list[list[bool]]:
        return [[False for _ in self.range_w] for _ in self.range_h]

    def set_cell(self, x: int, y: int, alive: bool):
        self.cells[x][y] = alive

    def draw_cell(self, x: int, y: int):
        pygame.draw.rect(self.surface, self.cell.alive_color if self.cells[x][y] else self.cell.dead_color,
                         (x * self.cell.width, y * self.cell.height, self.cell.width, self.cell.height))

    def draw_cells(self):
        for x in self.range_w:
            for y in self.range_h:
                self.draw_cell(x, y)

    def kill_all_cells(self):
        self.cells = self.init_cells()
        self.draw_cells()

    def handle_quit(self, event: Event):
        self.is_running = False

    def handle_mouse_down(self, event: Event):
        match event.button:
            case 1:
                self.is_mouse_reviving = True
            case 3:
                self.is_mouse_killing = True

    def handle_mouse_up(self, event: Event):
        match event.button:
            case 1:
                self.is_mouse_reviving = False
            case 3:
                self.is_mouse_killing = False

    def handle_key_down(self, event: Event):
        match event.key:
            case pygame.K_SPACE:
                self.is_generation_paused = not self.is_generation_paused
                print(f"Is generation paused: {self.is_generation_paused}")
            case pygame.K_k:
                self.kill_all_cells()
                print("Killed all cells")
            case pygame.K_UP:
                self.increase_time_per_generation(20)
                pygame.time.set_timer(self.NEW_GENERATION_EVENT, self.time_per_generation)
                print(f"Time per generation {self.time_per_generation}ms")
            case pygame.K_DOWN:
                self.decrease_time_per_generation(20)
                pygame.time.set_timer(self.NEW_GENERATION_EVENT, self.time_per_generation)
                print(f"Time per generation {self.time_per_generation}ms")

    def handle_key_up(self, event: Event):
        pass

    def handle_event(self, event: Event):
        match event.type:
            case pygame.QUIT:
                self.handle_quit(event)
            case pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
            case pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)
            case pygame.KEYDOWN:
                self.handle_key_down(event)
            case pygame.KEYUP:
                self.handle_key_up(event)
            case self.NEW_GENERATION_EVENT:
                self.handle_next_generation()
            case other:
                return

    def handle_mouse_revive(self):
        x, y = self.get_mouse_grid_pos()
        self.set_cell(x, y, True)
        self.draw_cell(x, y)

    def handle_mouse_kill(self):
        x, y = self.get_mouse_grid_pos()
        self.set_cell(x, y, False)
        self.draw_cell(x, y)

    def handle_next_generation(self):
        if not self.is_generation_paused:
            self.advance_generation()
            self.draw_cells()

    def increase_time_per_generation(self, amount: int):
        if self.time_per_generation < 2000:
            self.time_per_generation += amount

    def decrease_time_per_generation(self, amount: int):
        if self.time_per_generation > amount:
            self.time_per_generation -= amount

    def determine_survival(self, x: int, y: int) -> bool:
        neighbor_count = 0
        for n_x in range(x - 1, x + 2):
            for n_y in range(y - 1, y + 2):
                if not (n_y == y and n_x == x) and self.cells[n_x % self.board.width][n_y % self.board.height]:
                    neighbor_count += 1
        return neighbor_count == 3 or neighbor_count == 2 and self.cells[x][y]

    def advance_generation(self):
        new_generation = self.init_cells()
        for x in self.range_w:
            for y in self.range_h:
                new_generation[x][y] = self.determine_survival(x, y)
        self.cells = new_generation

    def get_mouse_grid_pos(self) -> (int, int):
        pos_x, pos_y = pygame.mouse.get_pos()
        x = pos_x // self.cell.width
        y = pos_y // self.cell.height
        return x, y

    def run(self):
        self.is_running = True

        pygame.time.set_timer(self.NEW_GENERATION_EVENT, self.time_per_generation)

        while self.is_running:
            for event in pygame.event.get():
                self.handle_event(event)

            if self.is_mouse_reviving:
                self.handle_mouse_revive()

            if self.is_mouse_killing:
                self.handle_mouse_kill()

            pygame.display.flip()

        pygame.quit()
