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
        MinMax.expanded = 0

        if objective == Objective.MAX:
            _, move = MinMax.max_value(current_state)
        else:
            _, move = MinMax.min_value(current_state)

        print(f"Expanded states: {MinMax.expanded}")

        return move
    @staticmethod
    def max_value(current_state: State):
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
                child_value,_ = MinMax.max_value(child)
            else:
                child_value,_ = MinMax.min_value(child)

            if child_value > v:
                v = child_value
                best_move = m

        return v, best_move

    @staticmethod
    def min_value(current_state: State):
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
                child_value, _ = MinMax.min_value(child)
            else:
                child_value, _ = MinMax.max_value(child)

            if child_value < v:
                v = child_value
                best_move = m

        return v, best_move

class AlphaBeta(AI):
    @staticmethod
    def best_move(current_state: State, objective: Objective):
        pass
