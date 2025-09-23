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
    expanded = 0
    @staticmethod
    def best_move(current_state: State, objective: Objective):
        depth = 0
        MinMax.expanded = 0

        if objective == Objective.MAX:
            _, move = MinMax.max_value(current_state, depth)
        else:
            _, move = MinMax.min_value(current_state, depth)

        print(f"Expanded states: {MinMax.expanded}")

        return move
    @staticmethod
    def max_value(current_state: State, depth:int):
        if depth == 8:
            return current_state.score,None
        MinMax.expanded += 1

        if current_state.check_victory() is not None:
            return current_state.score, None

        moves = current_state.available_moves()
        if not moves:
            return current_state.score, None

        v = float("-inf")
        best_move = moves[0]
        for m in moves:
            child = current_state.next_state(m)
            if child.current_player == 0:
                child_value,_ = MinMax.max_value(child, depth + 1)
            else:
                child_value,_ = MinMax.min_value(child, depth + 1)

            if child_value > v:
                v = child_value
                best_move = m

        return v, best_move

    @staticmethod
    def min_value(current_state: State, depth:int):
        if depth == 8:
            return current_state.score, None

        MinMax.expanded += 1
        if current_state.check_victory() is not None:
            return current_state.score, None

        moves = current_state.available_moves()
        if not moves:
            return current_state.score, None

        v = float("inf")
        best_move = moves[0]
        for m in moves:
            child = current_state.next_state(m)

            if child.current_player == 1:
                child_value, _ = MinMax.min_value(child, depth + 1)
            else:
                child_value, _ = MinMax.max_value(child, depth + 1)

            if child_value < v:
                v = child_value
                best_move = m

        return v, best_move

class AlphaBeta(AI):
    expanded = 0
    pruned = 0
    depth = 0
    @staticmethod
    def best_move(current_state: State, objective: Objective):
        AlphaBeta.expanded = 0
        AlphaBeta.pruned = 0

        if objective == Objective.MAX:
            _, move = AlphaBeta.max_value(current_state, float("-inf"), float("inf"), AlphaBeta.depth )
        else:
            _, move = AlphaBeta.min_value(current_state, float("-inf"), float("inf"), AlphaBeta.depth)

        print(f"Expanded states AlphaBeta: {AlphaBeta.expanded}")
        print(f"Pruned branches: {AlphaBeta.pruned}")

        return move

    @staticmethod
    def max_value(current_state: State, alpha, beta, depth):
        if depth == 8:
            return current_state.score,None
        AlphaBeta.expanded += 1
        if current_state.check_victory() is not None:
            return current_state.score, None

        moves = current_state.available_moves()
        if not moves:
            return current_state.score, None

        v = float("-inf")
        best_move = moves[0]
        for i,m in enumerate(moves):
            child = current_state.next_state(m)

            v2, _ = AlphaBeta.min_value(child, alpha, beta, depth + 1)
            if v2 > v:
                v = v2
                best_move = m
                alpha = max(alpha, v)
            if v >= beta:
                AlphaBeta.pruned += len(moves) - i - 1
                return v, best_move

        return v, best_move

    @staticmethod
    def min_value(current_state: State, alpha, beta, depth):

        if depth == 8:
            return current_state.score,None

        AlphaBeta.expanded += 1
        if current_state.check_victory() is not None:
            return current_state.score, None

        moves = current_state.available_moves()
        if not moves:
            return current_state.score, None

        v = float("inf")
        best_move = moves[0]
        for i,m in enumerate(moves):
            child = current_state.next_state(m)

            v2, _ = AlphaBeta.max_value(child, alpha, beta, depth + 1)
            if v2 < v:
                v = v2
                best_move = m
                beta = min(beta, v)
            if v <= alpha:
                AlphaBeta.pruned += len(moves) - i - 1
                return v, best_move
        return v, best_move
