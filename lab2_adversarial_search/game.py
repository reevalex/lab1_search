import sys
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

import pygame

from rich import print

from settings import *
from utils import Singleton


class Objective(Enum):
    MIN = 0,
    MAX = 1


class State:
    def __init__(self, pits, current_player):
        self.pits = pits.copy()
        self.current_player = current_player

    @property
    def score(self) -> int:
        # TODO: Complete this method
        return 0

    def next_state(self, pit):
        """
        Given a pit to perform a move on, create the resulting state
        """
        pits = self.pits.copy()
        seeds = pits[pit]
        pits[pit] = 0

        last_pit = (pit + seeds) % TOTAL_PITS

        # Find out if special rules apply to this move:
        # 1. Does the last stone end up in the player's store?
        # 2. Does the last stone end up in an empty pit on the player's side?
        for i in range(pit + 1, pit + 1 + seeds):
            pits[i % TOTAL_PITS] += 1

        # If the last stone ended up in an empty pit on the player's side, steal the stones in the opposing pit
        if pits[last_pit] == 1 and Kalah.pit_to_player(last_pit) == self.current_player \
                and pits[Kalah.opposing_pit(last_pit)] != 0 and last_pit not in [PLAYER_0_STORE, PLAYER_1_STORE]:
            pits[self.current_players_store] += pits[Kalah.opposing_pit(last_pit)] + pits[last_pit]
            pits[Kalah.opposing_pit(last_pit)] = 0
            pits[last_pit] = 0

        # If the last stone did not end up in the current player's store, we alternate the current player
        if not ((self.current_player == 0 and last_pit == PLAYER_0_STORE) or
                (self.current_player == 1 and last_pit == PLAYER_1_STORE)):
            current_player = 1 - self.current_player
        else:
            current_player = self.current_player

        new_state = State(pits, current_player)

        # If some player has no stone left on their side, move everything to the store of the other player
        winner = new_state.check_if_players_side_empty()
        if winner is not None:
            new_state.move_stones_to_store(winner)

        return new_state


    def check_if_players_side_empty(self):
        # Return the first player whose side of the board is empty
        found_empty_player = True
        for i in range(PITS_PER_PLAYER):
            if self.pits[i] != 0:
                found_empty_player = False
                break

        if found_empty_player:
            return 1

        found_empty_player = True
        for i in range(PLAYER_0_STORE + 1, TOTAL_PITS - 1):
            if self.pits[i] != 0:
                found_empty_player = False
                break

        if found_empty_player:
            return 0

        return None

    def check_victory(self):
        """
        Return the player who won, or None if all players still have stones in their pits.
        In case of a tie, return -1
        """
        is_game_finished = self.check_if_players_side_empty()

        if is_game_finished is None:
            return None

        player_0_score = self.pits[PLAYER_0_STORE]
        player_1_score = self.pits[PLAYER_1_STORE]

        if player_0_score == player_1_score:
            return -1

        return int(player_1_score > player_0_score)

    def move_stones_to_store(self, player):
        """
        Move all the stones to the store of the player passed as argument
        """
        assert player in [0, 1], "Invalid player"
        # if player == -1:
        #     print(f"[{DCOL_GAME}][GAME] [white]The game is a tie!")
        #     return

        # print(f"[{DCOL_GAME}][GAME] [white]Player {player}'s pits are empty!")
        players_store = PLAYER_0_STORE if player == 0 else PLAYER_1_STORE

        for i in range(PLAYER_0_STORE):
            self.pits[players_store] += self.pits[i]
            self.pits[i] = 0
        for i in range(PLAYER_0_STORE + 1, TOTAL_PITS - 1):
            self.pits[players_store] += self.pits[i]
            self.pits[i] = 0

        # print(f"[{DCOL_GAME}][GAME] [white]Player {player} is victorious")
        # print(f"[{DCOL_GAME}][GAME] [white]Final scores: {self.pits[PLAYER_0_STORE]} to {self.pits[PLAYER_1_STORE]}")

    def is_move_valid(self, pit):
        if self.pits[pit] == 0:
            return False

        if pit in [PLAYER_0_STORE, PLAYER_1_STORE]:
            # print("[DEBUG] ERROR: Tried to play a store")
            return False

        if self.current_player == 0:
            if not 0 <= pit < PITS_PER_PLAYER:
                return False
        else:
            if not PITS_PER_PLAYER + 1 <= pit < TOTAL_PITS:
                return False

        return True

    def available_moves(self) -> List[int]:
        """
        Return a list of available moves
        """
        moves = []
        if self.check_victory() is not None:
            return moves

        if self.current_player == 0:
            for i in range(PITS_PER_PLAYER + 1):
                if self.is_move_valid(i):
                    moves.append(i)
        else:
            for i in range(PITS_PER_PLAYER + 1, TOTAL_PITS - 1):
                if self.is_move_valid(i):
                    moves.append(i)

        return moves

    @property
    def current_players_store(self):
        if self.current_player == 0:
            return PLAYER_0_STORE
        return PLAYER_1_STORE

    def copy(self):
        return State(self.pits.copy(), self.current_player)


class Player:
    pass


class Human(Player):
    pass


class AI(Player, ABC):
    @staticmethod
    @abstractmethod
    def best_move(current_state: State, objective: Objective) -> int:
        pass


#
# Scenes
#

class Scene(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def draw(self):
        pass


class MainScene(Scene):
    def initialize(self):
        from ai import MinMax
        game = Game()

        title = TextBox(WIDTH / 2, HEIGHT / 2, "Kalah", "center", font=pygame.font.Font(None, 72))
        game.add_object(title)

        button_hvh = Button(250, 300, 100, 50, game.start_kalah, {'player0': Human(), 'player1': Human()}, button_text="H vs H")
        game.add_object(button_hvh)

        button_hvai = Button(350, 300, 100, 50, game.start_kalah, {'player0': Human(), 'player1': game.ai1()}, button_text="H vs AI")
        game.add_object(button_hvai)

        button_aivai = Button(450, 300, 100, 50, game.start_kalah, {'player0': game.ai0(), 'player1': game.ai1()}, button_text="AI vs AI")
        game.add_object(button_aivai)

    def draw(self):
        game = Game()
        game.screen.fill((0, 64, 0))


class KalahScene(Scene):
    def initialize(self):
        kalah = Kalah()
        kalah.initialize()

    def draw(self):
        kalah = Kalah()
        game = Game()

        game.screen.fill((0, 128, 0))

        board_length = PITS_PER_PLAYER * (PIT_RADIUS * 2.5)  # Also accounts for the gaps between the pits

        # Stores
        left_store_anchor = WIDTH / 2 - board_length / 2
        pygame.draw.rect(game.screen, PIT_COLOR, (left_store_anchor - 55, 245, 60, 20), border_radius=5)
        pygame.draw.rect(game.screen, PIT_COLOR_DARK, (left_store_anchor - 55, 145, 60, 110), border_radius=5)
        pygame.draw.rect(game.screen, PIT_COLOR_LIGHT, (left_store_anchor - 50, 150, 50, 100), border_radius=5)
        pygame.draw.rect(game.screen, PIT_COLOR, (left_store_anchor - 50, 150, 50, 10), border_radius=5)

        right_store_anchor = WIDTH / 2 + board_length / 2
        pygame.draw.rect(game.screen, PIT_COLOR, (right_store_anchor - 5, 245, 60, 20), border_radius=5)
        pygame.draw.rect(game.screen, PIT_COLOR_DARK, (right_store_anchor - 5, 145, 60, 110), border_radius=5)
        pygame.draw.rect(game.screen, PIT_COLOR_LIGHT, (right_store_anchor, 150, 50, 100), border_radius=5)
        pygame.draw.rect(game.screen, PIT_COLOR, (right_store_anchor, 150, 50, 10), border_radius=5)

        game.screen.blit(game.font.render(str(kalah.state.pits[PLAYER_0_STORE]), True, TEXT_COLOR), (right_store_anchor + 10, 180))
        game.screen.blit(game.font.render(str(kalah.state.pits[PLAYER_1_STORE]), True, TEXT_COLOR), (left_store_anchor - 40, 180))

        # Main board
        pygame.draw.rect(game.screen, BOARD_COLOR_DARK, (left_store_anchor, 110, board_length, 210), border_radius=20)
        pygame.draw.rect(game.screen, BOARD_COLOR, (left_store_anchor, 100, board_length, 200), border_radius=20)

        for board_pit in kalah.board_pits:
            if board_pit is None:
                continue
            board_pit.draw()

#
# Game
#

class Game(metaclass=Singleton):
    objects: list
    scene: Scene

    player0: Player
    player1: Player

    last_move_time: float
    next_move: int

    screen = None
    font = None

    running = True

    ai0 = None
    ai1 = None

    def initialize(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.font = pygame.font.Font(None, FONT_SIZE)

        self.objects = []

        self.scene = MainScene()
        self.scene.initialize()

        self.next_move = -1
        self.last_move_time = 0

    def set_ai_players(self, ai0, ai1):
        """
        Set the AI to be used for each player, when an AI should play

        :param ai0: A subclass of class AI, which dictates the strategy of the AI used by player 0
        :param ai1: A subclass of class AI, which dictates the strategy of the AI used by player 1
        :return: None
        """
        self.ai0 = ai0
        self.ai1 = ai1

    def run(self):
        kalah = Kalah()

        while self.running:
            self.scene.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if kalah.is_initialized and kalah.playing:
                if (kalah.current_player == 0 and isinstance(self.player0, AI)) or \
                    (kalah.current_player == 1 and isinstance(self.player1, AI)):

                    pygame.display.flip()

                    print(f"[{DCOL_AI}][AI] [white]Thinking...")
                    ai_thinking_starts = time.perf_counter()
                    if self.next_move == -1:
                        if kalah.current_player == 0:
                            self.next_move = self.player0.best_move(kalah.state, Objective.MAX)
                        else:
                            self.next_move = self.player1.best_move(kalah.state, Objective.MIN)

                    print(f"[{DCOL_AI}][AI] [white]Move found in {(time.perf_counter() - ai_thinking_starts)*1000:0.1f}ms")

                    # Wait some time to let the player see their move and its outcome
                    if self.last_move_time * 1000 + AI_WAIT_TIME >= time.time() * 1000:
                        time_to_wait = self.last_move_time * 1000 + AI_WAIT_TIME - time.time() * 1000
                        print(f"[{DCOL_AI}][AI] [white]Sleeping...")
                        pygame.time.wait(int(time_to_wait))

                    print(f"[{DCOL_AI}][AI] [white]Move chosen: {self.next_move}")
                    kalah.move(self.next_move)
                    self.next_move = -1

            for obj in self.objects:
                obj.process()
            pygame.display.flip()

            if kalah.is_initialized and kalah.state.check_victory() is not None:
                self.make_victory_popup()
                for obj in self.objects:
                    obj.process()
                kalah.stop_game()
                pygame.display.flip()


    def add_object(self, obj):
        self.objects.append(obj)

    def change_scene(self, scene=None):
        self.objects = []

        self.scene = scene
        scene.initialize()

        self.last_move_time = time.time()

    def start_kalah(self, player0=None, player1=None):
        self.player0 = player0
        self.player1 = player1

        self.change_scene(KalahScene())

    def make_victory_popup(self):
        kalah = Kalah()
        game = Game()

        winner = kalah.state.check_victory()

        if winner in [0, 1]:
            victory_text = f"Player {winner} wins!"
        elif winner == -1:
            victory_text = f"It's a tie!"
        else:
            victory_text = f"ERROR"

        game.add_object(TextBox(WIDTH - 10, HEIGHT - 10, victory_text, anchor="bottomright"))

        back_button = Button(10, HEIGHT - 60, 250, 50, game.change_scene, {'scene': MainScene()}, button_text="Back to menu")
        game.add_object(back_button)

        pygame.display.flip()


class Kalah(metaclass=Singleton):
    pits: List[int]
    state: State

    board_pits: list

    playing: bool
    last_move_player: int

    def __init__(self):
        self.is_initialized = False

    def initialize(self):
        self.pits = [SEEDS] * TOTAL_PITS
        self.pits[PLAYER_0_STORE] = 0
        self.pits[PLAYER_1_STORE] = 0

        self.state = State(self.pits, 0)

        self.board_pits = [None] * TOTAL_PITS

        self.playing = False
        self.last_move_player = -1

        game = Game()

        board_length = PITS_PER_PLAYER * (PIT_RADIUS * 2.5)
        left_board_edge = WIDTH / 2 - board_length / 2

        for i in range(PITS_PER_PLAYER):
            pit1 = BoardPit(50 + left_board_edge + i * (PIT_RADIUS * 2.5), 250, PIT_RADIUS, self.try_move, args={'pit': i})
            game.add_object(pit1)

            self.board_pits[i] = pit1

            pit2 = BoardPit(50 + left_board_edge + (PITS_PER_PLAYER - 1 - i) * 100, 150, PIT_RADIUS, self.try_move,
                            args={'pit': i + PITS_PER_PLAYER + 1})
            game.add_object(pit2)

            self.board_pits[i + PITS_PER_PLAYER + 1] = pit2

            self.playing = True

        self.is_initialized = True

    @staticmethod
    def pit_to_player(pit):
        """
        Player to whom the pit belongs
        """
        if 0 <= pit <= PITS_PER_PLAYER:
            return 0
        if PITS_PER_PLAYER < pit <= TOTAL_PITS:
            return 1

    @staticmethod
    def opposing_pit(pit):
        return (TOTAL_PITS - 2 - pit) % TOTAL_PITS

    @staticmethod
    def player_to_store(player):
        return PLAYER_0_STORE if player == 0 else PLAYER_1_STORE

    @property
    def current_player(self):
        return self.state.current_player

    def set_pit(self, pit_id, new_value):
        self.pits[pit_id] = new_value
        if pit_id not in [PLAYER_0_STORE, PLAYER_1_STORE]:
            self.board_pits[pit_id].seeds = new_value

    def move(self, pit):
        print(f"[{DCOL_GAME}][GAME] [white]Moving pit {pit}")
        game = Game()
        self.last_move_player = self.state.current_player

        self.state = self.state.next_state(pit)

        # Update the board pit's behavior
        for i in range(TOTAL_PITS):
            self.set_pit(i, self.state.pits[i])

        player_0_turn = True if self.state.current_player == 0 else False
        for i in range(PITS_PER_PLAYER):
            if self.pits[i] == 0:
                self.board_pits[i].set_active(False)
            else:
                self.board_pits[i].set_active(player_0_turn)
            self.board_pits[i].set_highlighted(False)

        for i in range(PITS_PER_PLAYER + 1, TOTAL_PITS - 1):
            if self.pits[i] == 0:
                self.board_pits[i].set_active(False)
            else:
                self.board_pits[i].set_active(not player_0_turn)
            self.board_pits[i].set_highlighted(False)

        # If the last player was an AI, show the move played
        if (self.last_move_player == 0 and isinstance(game.player0, AI)) or \
                (self.last_move_player == 1 and isinstance(game.player1, AI)):
            self.board_pits[pit].set_highlighted(True)

        game.last_move_time = time.time()

        # Check victory conditions
        winning_player = self.state.check_victory()
        if winning_player is not None:
            # self.state.moves_stones_to_store(winning_player)
            self.playing = False


    def try_move(self, pit=-1):
        if pit == -1:
            return
        if self.state.is_move_valid(pit):
            self.move(pit)

    def stop_game(self):
        self.playing = False
        self.is_initialized = False

    def is_playing(self):
        return self.playing


class GameObject(ABC):
    @abstractmethod
    def process(self):
        pass


class TextBox(GameObject):
    def __init__(self, x, y, text, anchor="topleft", font=None):
        game = Game()

        self.x = x
        self.y = y

        if font is None:
            font = game.font
        self.text = font.render(text, True, (20, 20, 20))

        self.anchor = anchor

    def process(self):
        super().process()

        game = Game()

        text_rect = self.text.get_rect()
        assert self.anchor in ["topleft", "bottomright", "topright", "bottomleft", "center"], \
            "Invalid anchor position for button"
        setattr(text_rect, self.anchor,  (self.x - 10, self.y - 10))
        bg_rect = pygame.Rect(
            text_rect.left - 10,
            text_rect.top - 5,
            text_rect.width + 20,
            text_rect.height + 10
        )
        pygame.draw.rect(game.screen, (255, 255, 255), bg_rect)  # White background
        pygame.draw.rect(game.screen, (0, 0, 0), bg_rect, 2)  # Black border
        game.screen.blit(self.text, text_rect)


class Clickable(GameObject):
    def __init__(self, on_click, args=None, collider=None):
        game = Game()

        self.on_click = on_click
        if args is None:
            self.args = {}
        else:
            self.args = args

        self.collider = collider

        self.already_pressed = False

        game.add_object(self)

    def collides_with(self, x, y):
        if self.collider is not None:
            return self.collider.collidepoint((x, y))
        return False

    def process(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.collides_with(mouse_x, mouse_y):
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                if not self.already_pressed:
                    self.on_click(**self.args)
                    self.already_pressed = True
            else:
                self.already_pressed = False


class Button(Clickable):
    def __init__(self, x, y, width, height, on_click, args=None, button_text='Button'):
        collider = pygame.Rect(x, y, width, height)
        super().__init__(on_click, args=args, collider=collider)

        game = Game()

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.already_pressed = False

        # Replace this by a class "ColorScheme"
        self.fill_colors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.surface = pygame.Surface((self.width, self.height))
        self.text = game.font.render(button_text, True, (20, 20, 20))

    def process(self):
        super().process()

        game = Game()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.surface.fill(self.fill_colors['normal'])
        if self.collider.collidepoint(mouse_x, mouse_y):
            self.surface.fill(self.fill_colors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.surface.fill(self.fill_colors['pressed'])

        self.surface.blit(self.text, [
            self.collider.width/2 - self.surface.get_rect().width/2,
            self.collider.height/2 - self.surface.get_rect().height/2
        ])
        game.screen.blit(self.surface, self.collider)


class BoardPit(Clickable):
    def __init__(self, x, y, radius, on_click, args=None):
        super().__init__(on_click, args=args, collider=None)

        game = Game()

        self.x = x
        self.y = y
        self.radius = radius
        self.already_pressed = False

        self.fill_colors = {
            'normal': pygame.Color(205, 133, 63),
            'hover': pygame.Color(210, 150, 93),
            'pressed': pygame.Color(170, 100, 43),
            'highlighted': pygame.Color(210, 36, 36),
        }

        # Seeds shown on the pit
        self.seeds = SEEDS

        # Whether the pit should react to the mouse or not. Purely visual
        self.active = True

        # Highlight the pit when the last move was played
        self.highlighted = False

        self.text = game.font.render(str(self.seeds), True, (20, 20, 20))

    def collides_with(self, x, y):
        return (self.x - x) ** 2 + (self.y - y) ** 2 <= self.radius ** 2

    def draw(self):
        game = Game()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        circ_color = self.fill_colors['normal']
        if self.active and self.collides_with(mouse_x, mouse_y):
            circ_color = self.fill_colors['hover']
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                circ_color = self.fill_colors['pressed']

        if not self.active and self.highlighted:
            circ_color = self.fill_colors['highlighted']

        pygame.draw.circle(game.screen, circ_color, (self.x, self.y), self.radius)
        game.screen.blit(game.font.render(str(self.seeds), True, TEXT_COLOR), (self.x - FONT_SIZE/4, self.y - FONT_SIZE/4))

    def set_active(self, active=True):
        self.active = active

    def set_highlighted(self, highlighted=True):
        self.highlighted = highlighted
