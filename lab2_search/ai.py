import random

from game import AI, State, Objective
from typing import Union
from settings import MAX_DEPTH


class Random(AI):
    @staticmethod
    def best_move(current_state: State, objective: Objective):
        state = current_state.copy()

        available_moves = state.available_moves()
        if not available_moves:
            return None

        return random.choice(available_moves)


class MinMax(AI):
    expanded_nodes = 0

    @staticmethod
    def best_move(current_state: State, objective: Objective):
        state = current_state.copy()

        MinMax.expanded_nodes = 0

        available_moves = state.available_moves()
        if not available_moves:
            return None

        next_move = None
        best_value = float("-inf") if objective == Objective.MAX else float("inf")

        for move in available_moves:
            next_state = state.next_state(move)

            if objective == Objective.MAX:
                value = MinMax.min_value(next_state, MAX_DEPTH)
                if value > best_value:
                    best_value = value
                    next_move = move
            elif objective == Objective.MIN:
                value = MinMax.max_value(next_state, MAX_DEPTH)
                if value < best_value:
                    best_value = value
                    next_move = move

        if MAX_DEPTH is None:
            print(f"[MinMax - Unbounded] Expanded {MinMax.expanded_nodes} nodes")
        else:
            print(
                f"[MinMax - Bounded={MAX_DEPTH}] Expanded {MinMax.expanded_nodes} nodes"
            )
        return next_move

    @staticmethod
    def max_value(current_state: State, max_depth: Union[int, None]):
        MinMax.expanded_nodes += 1
        state = current_state.copy()

        if state.check_victory() is not None:
            return state.score

        if max_depth == 0 and max_depth is not None:
            return state.score
        max_depth = max_depth - 1 if max_depth is not None else max_depth

        available_moves = state.available_moves()
        if not available_moves:
            return state.score

        max_value = float("-inf")
        for move in available_moves:
            next_state = state.next_state(move)
            value = MinMax.min_value(next_state, max_depth)
            max_value = max(max_value, value)
        return max_value

    @staticmethod
    def min_value(current_state: State, max_depth: Union[int, None]):
        MinMax.expanded_nodes += 1
        state = current_state.copy()

        if state.check_victory() is not None:
            return state.score

        if max_depth == 0 and max_depth is not None:
            return state.score
        max_depth = max_depth - 1 if max_depth is not None else max_depth

        available_moves = state.available_moves()
        if not available_moves:
            return state.score

        min_value = float("inf")
        for move in available_moves:
            next_state = state.next_state(move)
            value = MinMax.max_value(next_state, max_depth)
            min_value = min(min_value, value)
        return min_value


class AlphaBeta(AI):
    expanded_nodes = 0
    pruned_nodes = 0

    @staticmethod
    def best_move(current_state: State, objective: Objective):
        state = current_state.copy()

        AlphaBeta.expanded_nodes = 0
        AlphaBeta.pruned_nodes = 0

        available_moves = state.available_moves()
        if not available_moves:
            return None

        next_move = None
        best_value = float("-inf") if objective == Objective.MAX else float("inf")
        alpha, beta = float("-inf"), float("inf")

        for move in available_moves:
            next_state = state.next_state(move)

            if objective == Objective.MAX:
                value = AlphaBeta.min_value(next_state, alpha, beta, MAX_DEPTH)
                if value > best_value:
                    alpha = max(alpha, value)
                    best_value = value
                    next_move = move
            elif objective == Objective.MIN:
                value = AlphaBeta.max_value(next_state, alpha, beta, MAX_DEPTH)
                if value < best_value:
                    beta = min(beta, value)
                    best_value = value
                    next_move = move

        if MAX_DEPTH is None:
            print(f"[AlphaBeta - Unbounded] Expanded {AlphaBeta.expanded_nodes} nodes")
        else:
            print(
                f"[AlphaBeta - Bounded={MAX_DEPTH}] Expanded {AlphaBeta.expanded_nodes} nodes"
            )

        return next_move

    @staticmethod
    def max_value(
        current_state: State, alpha: float, beta: float, max_depth: Union[int, None]
    ):
        state = current_state.copy()

        AlphaBeta.expanded_nodes += 1

        if state.check_victory() is not None:
            return state.score

        if max_depth == 0 and max_depth is not None:
            return state.score
        max_depth = max_depth - 1 if max_depth is not None else max_depth

        available_moves = state.available_moves()
        if not available_moves:
            return state.score

        max_value = float("-inf")
        for move in available_moves:
            next_state = state.next_state(move)
            value = AlphaBeta.min_value(next_state, alpha, beta, max_depth)
            max_value = max(max_value, value)
            alpha = max(alpha, value)

            if beta <= alpha:
                AlphaBeta.pruned_nodes += 1
                break

        return max_value

    @staticmethod
    def min_value(
        current_state: State, alpha: float, beta: float, max_depth: Union[int, None]
    ):
        state = current_state.copy()

        AlphaBeta.expanded_nodes += 1

        if state.check_victory() is not None:
            return state.score

        if max_depth == 0 and max_depth is not None:
            return state.score
        max_depth = max_depth - 1 if max_depth is not None else max_depth

        available_moves = state.available_moves()
        if not available_moves:
            return state.score

        min_value = float("inf")
        for move in available_moves:
            next_state = state.next_state(move)
            value = AlphaBeta.max_value(next_state, alpha, beta, max_depth)
            min_value = min(min_value, value)
            beta = min(beta, value)

            if beta <= alpha:
                AlphaBeta.pruned_nodes += 1
                break

        return min_value
