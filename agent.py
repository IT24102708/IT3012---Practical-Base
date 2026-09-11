# agent.py
import random
from collections import deque
import heapq
import math
from logic_engine import KnowledgeBase

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    
    
    def sense_and_act(self, percept: dict) -> str:
        # IF food_here THEN stay (to consume)
        # IF wall_ahead THEN turn_left
        # ELSE move_forward
        if percept.get('food_here'):
            return 'Stay'
        elif percept.get('wall_ahead'):
            # Blindly turns left when facing a wall
            return 'Left' 
        else:
            # Blindly attempts to move forward
            return 'Up'   


class ModelBasedAgent:
    
    def __init__(self):
        # Initialize internal memory state
        self.previous_percept = None
        self.last_action = None
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # 1. Update State (Transition & Sensor Model tracking)
        # Check if we are seeing the exact same percept and we hit a wall previously
        stuck_in_loop = (self.previous_percept == percept and percept.get('wall_ahead'))

        # 2. Condition-Action Rules querying the memory
        if percept.get('food_here'):
            action = 'Stay'
        elif stuck_in_loop:
            # We are trapped! Force a completely different action than last time
            available_actions = list(self.actions_pool)
            if self.last_action in available_actions:
                available_actions.remove(self.last_action)
            action = random.choice(available_actions)
        elif percept.get('wall_ahead'):
             # Default reflex reaction
            action = 'Left'
        else:
            # Default forward movement
            action = 'Up'   
        
        # 3. Record history for the next iteration
        self.previous_percept = percept
        self.last_action = action
        
        return action


class SearchAgent: 

    def __init__(self):
        # Stores the sequence of actions to reach the goal
        self.plan = []
        # Configuration string to easily swap algorithms for the observation task
        self.active_algo = 'BFS'

        print(f"Manhattan Test: {self.manhattan_distance((0,0), (3,4))}") 
        print(f"Euclidean Test: {self.euclidean_distance((0,0), (3,4))}")

    def get_successors(self, state, walls, grid_size):
        
        x, y = state
        width, height = grid_size
        successors = []
        
        # Directions mapping based on your environment's coordinate system
        moves = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }
        
        for action, (dx, dy) in moves.items():
            nx, ny = x + dx, y + dy
            # Check boundaries
            if 0 <= nx < width and 0 <= ny < height:
                # Check walls
                if (nx, ny) not in walls:
                    successors.append((action, (nx, ny)))
                    
        return successors


    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        # FIFO Queue stores tuples of (current_state, path_taken)
        frontier = deque([(start_pos, [])])
        visited = set([start_pos])

        while frontier:
            current_state, path = frontier.popleft()

            if current_state == goal_pos:
                return path

            for action, next_state in self.get_successors(current_state, walls, grid_size):
                if next_state not in visited:
                    visited.add(next_state)
                    frontier.append((next_state, path + [action]))
                    
        return []  # Return empty if goal is unreachable


    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        # LIFO Stack stores tuples of (current_state, path_taken)
        frontier = [(start_pos, [])]
        visited = set() 

        while frontier:
            current_state, path = frontier.pop()
            
            if current_state == goal_pos:
                return path
                
            # For DFS, it's safer to mark visited when popping from the stack
            if current_state not in visited:
                visited.add(current_state)
                
                for action, next_state in self.get_successors(current_state, walls, grid_size):
                    if next_state not in visited:
                        frontier.append((next_state, path + [action]))
                        
        return []

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        # Priority Queue stores tuples of (cost, counter, current_state, path_taken)
        frontier = []
        counter = 0
        heapq.heappush(frontier, (0, counter, start_pos, []))
        visited = set()

        while frontier:
            cost, _, current_state, path = heapq.heappop(frontier)

            if current_state == goal_pos:
                return path
                
            if current_state not in visited:
                visited.add(current_state)
                
                for action, next_state in self.get_successors(current_state, walls, grid_size):
                    if next_state not in visited:
                        counter += 1
                        heapq.heappush(frontier, (cost + 1, counter, next_state, path + [action]))
                        
        return []


    def sense_and_act(self, percept: dict) -> str:
        # Step 1: Check if the current plan is empty
        if not self.plan:
            
            # Note: Your visual environment provides 'all_food' instead of 'remaining_food'
            all_food = percept.get('all_food', [])
            
            # Safety check: If there is no food left, do nothing
            if not all_food:
                return 'Stay'
                
            # Get current position and convert to tuple for coordinate math
            start_pos = tuple(percept['agent_pos'])
            
            # Using your new manhattan_distance method for cleaner code
            closest_food = min(
                all_food, 
                key=lambda f: self.manhattan_distance(start_pos, f)
            )
            
            # Extract environment data for the search
            walls = set(percept['walls']) # Convert to set for faster lookups
            grid_size = percept['grid_size']
            
            # Execute the search method matching self.active_algo
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start_pos, closest_food, walls, grid_size)
            # Task 2: Add the AStar block to handle the new algorithm
            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(start_pos, closest_food, walls, grid_size, 'manhattan')
                
        # Execute the plan step-by-step
        if self.plan:
            # Return the first action and remove it from the list
            return self.plan.pop(0)
        else:
            # Fallback if the search failed to find a path 
            return 'Stay'


    def manhattan_distance(self, pos, goal):
        # Calculates h(n) = |x_1 - x_2| + |y_1 - y_2|
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


    def euclidean_distance(self, pos, goal):
        # Calculates h(n) = \sqrt{(x_1-x_2)^2+(y_1-y_2)^2}
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)


    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        # Task 2: Initialize priority queue and reached_states set
        priority_queue = []
        reached_states = set()
        
        # Task 3: Calculate initial costs and push the starting node
        g_cost = 0
        if heuristic_type == 'manhattan':
            h_cost = self.manhattan_distance(start_pos, goal_pos)
        else:
            h_cost = self.euclidean_distance(start_pos, goal_pos)
            
        f_cost = g_cost + h_cost
        
        # Format: (f_cost, g_cost, current_pos, path_taken)
        heapq.heappush(priority_queue, (f_cost, g_cost, start_pos, []))
        
        # Task 4: Standard while loop to process the queue
        while priority_queue:
            current_f, current_g, current_pos, path_taken = heapq.heappop(priority_queue)
            
            # Goal Check
            if current_pos == goal_pos:
                return path_taken
                
            # Skip if we have already expanded this state with a cheaper path
            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)
            
            # Task 5: Node expansion using your existing get_successors method
            for action, next_state in self.get_successors(current_pos, walls, grid_size):
                if next_state not in reached_states:
                    # Calculate new g(n)
                    new_g = current_g + 1
                    
                    # Calculate new h(n) based on the selected heuristic
                    if heuristic_type == 'manhattan':
                        new_h = self.manhattan_distance(next_state, goal_pos)
                    else:
                        new_h = self.euclidean_distance(next_state, goal_pos)
                        
                    # Calculate new f(n)
                    new_f = new_g + new_h
                    
                    # Push the new state to the priority queue
                    heapq.heappush(priority_queue, (new_f, new_g, next_state, path_taken + [action]))
                    
        # Return an empty list if no path is found
        return []


class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start node
        self.h = 0  # Heuristic estimated cost to goal
        self.f = 0  # Total cost (g + h)

    def __lt__(self, other):
        return self.f < other.f

class Agent:
    def __init__(self):
        self.kb = KnowledgeBase()
        
        # Define Safety Constraints
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    def calculate_heuristic(self, current, goal):
        return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

    def get_neighbors(self, current_node, grid_size):
        x, y = current_node.position
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
                neighbors.append((nx, ny))
                
        return neighbors

    def get_percepts_for_tile(self, tile_position):
        # NOTE: Replace with your actual game map sensor function
        return [] 

    def a_star_search(self, start, goal, grid_size):
        start_node = Node(start)
        goal_node = Node(goal)

        open_list = []
        closed_set = set() 

        heapq.heappush(open_list, start_node)

        while open_list:
            current_node = heapq.heappop(open_list)
            closed_set.add(current_node.position)

            if current_node.position == goal_node.position:
                path = []
                while current_node:
                    path.append(current_node.position)
                    current_node = current_node.parent
                return path[::-1] 

            for neighbor_pos in self.get_neighbors(current_node, grid_size):
                if neighbor_pos in closed_set:
                    continue

                # Logical Feasibility Validation
                self.kb.clear_facts()
                
                current_percepts = self.get_percepts_for_tile(neighbor_pos)
                for percept in current_percepts:
                    self.kb.tell_fact(percept)
                    
                self.kb.forward_chain()
                
                # Mark Infeasible if Retreat is deduced
                if 'Retreat' in self.kb.facts:
                    continue 
                    
                # Standard A* path evaluation for feasible nodes
                neighbor_node = Node(neighbor_pos, current_node)
                neighbor_node.g = current_node.g + 1
                neighbor_node.h = self.calculate_heuristic(neighbor_pos, goal)
                neighbor_node.f = neighbor_node.g + neighbor_node.h

                if any(open_node for open_node in open_list if neighbor_node.position == open_node.position and neighbor_node.g >= open_node.g):
                    continue

                heapq.heappush(open_list, neighbor_node)

        return None