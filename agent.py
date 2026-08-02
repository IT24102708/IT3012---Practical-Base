# agent.py
import random

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
