import random

from game import AI, State, Objective


class Random(AI):
    @staticmethod
    def best_move(current_state: State, objective: Objective):
        state = current_state.copy()

        available_moves = state.available_moves()
        if not available_moves:
            return None

        return random.choice(available_moves)


class MinMax(AI):
    @staticmethod
    def best_move(current_state: State, objective: Objective):
        pass


class AlphaBeta(AI):
    @staticmethod
    def best_move(current_state: State, objective: Objective):
        pass
