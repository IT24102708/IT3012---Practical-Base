# agent.py
import random
from collections import deque
import heapq

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
            
            all_food = percept.get('all_food', [])
            
            # Safety check: If there is no food left, do nothing
            if not all_food:
                return 'Stay'
                
            # Get current position and convert to tuple for coordinate math
            start_pos = tuple(percept['agent_pos'])
            
            # Step 2: Find the closest food pellet using Manhattan distance
            closest_food = min(
                all_food, 
                key=lambda f: abs(f[0] - start_pos[0]) + abs(f[1] - start_pos[1])
            )
            
            # Extract environment data for the search
            walls = set(percept['walls']) # Convert to set for faster lookups
            grid_size = percept['grid_size']
            
            # Step 3: Execute the search method matching self.active_algo
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start_pos, closest_food, walls, grid_size)
                
        # Step 4: Execute the plan step-by-step
        if self.plan:
            # Return the first action and remove it from the list
            return self.plan.pop(0)
        else:
            # Fallback if the search failed to find a path (e.g., food is fully blocked off)
            return 'Stay'

    


