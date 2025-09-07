from typing import List
from vacuum_world.search.search_node import SearchNode
from vacuum_world.search.problem import SearchProblem
from .base_search import BaseSearch


class DepthFirstSearch(BaseSearch):
    def __init__(self):
        super().__init__()

    def search(self, problem: SearchProblem) -> List[SearchNode]:
        self.path = []

        initial_state = problem.get_initial_state()
        initial_node = SearchNode(initial_state, None, None, 0.0)

        if problem.is_goal_state(initial_state):
            self.path = [initial_node]
            return self.path

        self.frontier.append(initial_node)
        self.explored.append(initial_node)

        while self.frontier:
            current_node = self.frontier.pop()
            current_state = current_node.get_state()

            successors = problem.get_successors(current_state)

            for child_state in successors:
                child_node = SearchNode(
                    state=child_state,
                    parent=current_node,
                    action=None,
                    cost=current_node.get_cost() + 1,
                )
                if problem.is_goal_state(child_state):
                    self.path = child_node.get_path_from_root()
                    return self.path

                if child_node not in self.explored:
                    self.explored.append(child_node)
                    self.frontier.append(child_node)

        return []

    def get_frontier_nodes(self) -> List[SearchNode]:
        return self.frontier

    def get_explored_nodes(self) -> List[SearchNode]:
        return self.explored
