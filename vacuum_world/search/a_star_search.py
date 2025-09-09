from typing import List, Optional
from vacuum_world.search.search_node import SearchNode
from vacuum_world.search.problem import SearchProblem
from vacuum_world.world.grid_pos import GridPos
from .base_search import BaseSearch

import heapq


class AStarNode(SearchNode):
    def __init__(
        self,
        state: GridPos,
        parent: Optional["SearchNode"],
        cost: float,
        goal_state: GridPos,
    ):
        super().__init__(state, parent, None, cost)
        self.h_cost = self.state.distance_manhattan(goal_state)
        self.f_cost = self.cost + self.h_cost

    def __lt__(self, other):
        if not isinstance(other, AStarNode):
            return False

        return self.f_cost < other.f_cost


class AStarSearch(BaseSearch):
    def __init__(self):
        super().__init__()

    def search(self, problem: SearchProblem) -> List[SearchNode]:
        self.path = []
        self.explored = set()
        heapq.heapify(self.frontier)

        initial_state = problem.get_initial_state()
        initial_node = AStarNode(initial_state, None, 0.0, problem.goal_state)

        if problem.is_goal_state(initial_state):
            self.path = [initial_node]
            return self.path

        heapq.heappush(self.frontier, initial_node)
        self.explored.add(initial_node)

        while self.frontier:
            current_node = heapq.heappop(self.frontier)
            current_state = current_node.get_state()
            self.explored.add(current_node)

            if problem.is_goal_state(current_state):
                self.path = current_node.get_path_from_root()
                return self.path

            successors = [
                AStarNode(
                    state, current_node, current_node.get_cost() + 1, problem.goal_state
                )
                for state in problem.get_successors(current_state)
            ]

            for node in successors:
                if node in self.explored:
                    continue
                heapq.heappush(self.frontier, node)

        return []

    def get_frontier_nodes(self) -> List[SearchNode]:
        return list(self.frontier)

    def get_explored_nodes(self) -> List[SearchNode]:
        return list(self.explored)

    def get_all_expanded_nodes(self) -> List[SearchNode]:
        return self.get_frontier_nodes() + self.get_explored_nodes()
