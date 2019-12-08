import interfaces as controller_template
from itertools import product
from typing import Tuple, List
from random import randint, uniform
from math import exp

# Constants for sensor indexing
DIST_LEFT = 0
DIST_CENTER = 1
DIST_RIGHT = 2
ON_TRACK = 3
DIST_CHECKPOINT = 4
SPEED = 5
DIST_ENEMY = 6
ENEMY_ANGLE = 7
ENEMY_NEAR = 8
CHECKPOINT = 9
NEXT_TRACK = 10
DIST_BOMB = 12
BOMB_ANGLE = 13
BOMB_NEAR = 11

NUM_OF_ACTIONS = 5
MAX_POSSIBLE_DIFF = 20  # maximum speed going straigth towards the checkpoint

class State(controller_template.State):
    def __init__(self, sensors: list):
        self.sensors = sensors

        self.prev_sens = [0.0 for x in self.sensors]
        self.prev_feats = []

    def compute_features(self) -> Tuple:
        """
        This function should take the raw sensor information of the car (see below) and compute useful features for selecting an action
        The car has the following sensors:

        self.sensors contains (in order):
            0 track_distance_left: 1-100
            1 track_distance_center: 1-100
            2 track_distance_right: 1-100
            3 on_track: 0 if off track, 1 if on normal track, 2 if on ice
            4 checkpoint_distance: 0-???
            5 car_velocity: 10-200
            6 enemy_distance: -1 or 0-???
            7 enemy_position_angle: -180 to 180
            8 enemy_detected: 0 or 1
            9 checkpoint: 0 or 1
           10 incoming_track: 1 if normal track, 2 if ice track or 0 if car is off track
           
           wrong:
           11 bomb_distance = -1 or 0-???
           12 bomb_position_angle = -180 to 180
           13 bomb_detected = 0 or 1

            right:
            11: detected
            12: distance
            13: angle

          (see the specification file/manual for more details)
        :return: A Tuple containing the features you defined
        """

        
        # Some features
        if self.sensors[CHECKPOINT] == 1:
            check_diff = 20
        else:
            check_diff = self.prev_sens[DIST_CHECKPOINT] - self.sensors[DIST_CHECKPOINT]

        speed = self.sensors[SPEED]
        dist_ahead = self.sensors[DIST_CENTER]
        dist_left = self.sensors[DIST_LEFT]
        dist_rigth = self.sensors[DIST_RIGHT]
        

        dist_bomb = self.sensors[DIST_BOMB]
        angle_bomb = self.sensors[BOMB_ANGLE]

        
        return [check_diff, speed, dist_ahead, dist_left, dist_rigth, dist_bomb, angle_bomb]

    


    def discretize_features(self, features: Tuple) -> Tuple:
        """
        This function should map the (possibly continuous) features (calculated by compute features) and discretize them.
        :param features 
        :return: A tuple containing the discretized features
        """
        
        # we consider a 5 levels discretization having the levels 0, 1, 2, 3 and 4
        check_diff = features[0] // 4 if features[0] < 20 else 4 
        speed = features[1] // 40 if features[1] < 200 else 4 
        dist_ahead = features[2] // 20 if features[2] < 100 else 4

        # we consider a 3 levels discretization having the levels 0, 1 and 2
        dist_left = features[3] // 33 if features[3] < 99 else 2
        dist_rigth = features[4] // 33 if features[4] < 99 else 2

        # dist bomb: binary, either too close to a bomb or not
        dist_bomb = 0 if features[5] > 50 else 1
        # angle bomb: binary, either in a possible colision or not
        #HELP IDK WHAT TO PUT HERE
        angle_bomb = 0 if abs(features[6]) >= 45 else 1

        return [check_diff, speed, dist_ahead, dist_left, dist_rigth, dist_bomb, angle_bomb]


    @staticmethod
    def discretization_levels() -> Tuple:
        """
        This function should return a vector specifying how many discretization levels to use for each state feature.
        :return: A tuple containing the discretization levels of each feature
        """
        
        #check_diff, speed, dist_ahead, dist_left, dist_rigth, dist_bomb, angle_bomb
        return [5, 5, 5, 3, 3, 2, 2]


    @staticmethod
    def enumerate_all_possible_states() -> List:
        """
        Handy function that generates a list with all possible states of the system.
        :return: List with all possible states
        """
        levels = State.discretization_levels()
        levels_possibilities = [(j for j in range(i)) for i in levels]
        return [i for i in product(*levels_possibilities)]


class QTable(controller_template.QTable):
    def __init__(self):
        """
        This class is used to create/load/store your Q-table. To store values we strongly recommend the use of a Python
        dictionary.
        """

        # The key to the dictionary is the state, the value is another dictonary
        # The key of that dictionary is an action and the value is the Q value
        # of that action in that state
        # {
        #   <State> {
        #               1: q val
        #               2: q val
        #               3: q val
        #               4: q val
        #               5: q val
        #           }
        #   <Another state> { ... }
        #   ....
        # }

        self.default_pref = 0.1
        self.table = {}

        states = State.enumerate_all_possible_states()
        actions = range(1,6) # because it's a closed interval

        for state in states:
            state_actions = {}
            for action in actions:
                state_actions[action] = randint(0,50)
            self.table[state] = state_actions


    def get_q_value(self, key: State, action: int) -> float:
        """
        Used to securely access the values within this q-table
        :param key: a State object 
        :param action: an action
        :return: The Q-value associated with the given state/action pair
        """

        q_value = self.table[key][action]
        return q_value

    def set_q_value(self, key: State, action: int, new_q_value: float) -> None:
        """
        Used to securely set the values within this q-table
        :param key: a State object 
        :param action: an action
        :param new_q_value: the new Q-value to associate with the specified state/action pair
        :return: 
        """

        self.table[key][action] = new_q_value


    def get_best_action(self, key: State) -> (int, int):

        values = self.table[key]
        best_action = max(values)
        best_q_value = self.table[key][best_action]
        return best_action, best_q_value

    @staticmethod
    def load(path: str) -> "QTable":
        """
        This method should load a Q-table from the specified file and return a corresponding QTable object
        :param path: path to file
        :return: a QTable object
        """
        raise NotImplementedError()

    def save(self, path: str, *args) -> None:
        """
        This method must save this QTable to disk in the file file specified by 'path'
        :param path: 
        :param args: Any optional args you may find relevant; beware that they are optional and the function must work
                     properly without them.
        """
        raise NotImplementedError()


class Controller(controller_template.Controller):
    def __init__(self, q_table_path: str):
        if q_table_path is None:
            self.q_table = QTable()
        else:
            self.q_table = QTable.load(q_table_path)

        # Available actions
        self.actions = {1: 'Accel', 2: 'Brake', 3: 'Left', 4: 'Right', 5: 'Nop'}
        self.num_actions = len(self.actions.keys)
        self.features = []
        self.num_features = len(self.features)

        # Attenuation of benefit
        self.atten = 0.9
        # Learning rate frame-wise
        self.alpha = 0.5
        # Curiosity for worse options
        # self.exploration_initial = 0.9
        # self.exploration_threshold = 0.5



    def update_q(self, new_state: State, old_state: State, action: int, reward: float, end_of_race: bool) -> None:
        """
        This method is called by the learn() method in simulator.Simulation() to update your Q-table after each action is taken
        :param new_state: The state the car just entered
        :param old_state: The state the car just left
        :param action: the action the car performed to get to new_state
        :param reward: the reward the car received for getting to new_state  
        :param end_of_race: boolean indicating if a race timeout was reached
        """
        raise NotImplementedError("This method must be implemented")

        pref = self.q_table.get_q_value(old_state, action)
        next_action, next_pref = self.q_table.get_best_action(new_state)
        # Q-Learning equation:
        # Alpha rate of learning, gamma time attenuation of future benefit
        updated = (1-alpha)*pref + alpha*(reward + atten*next_pref)

        self.q_table.set_q_value(old_state, action, updated)

    def compute_reward(self, new_state: State, old_state: State, action: int, n_steps: int,
                       end_of_race: bool) -> float:
        """
        This method is called by the learn() method in simulator.Simulation() to calculate the reward to be given to the agent
        :param new_state: The state the car just entered
        :param old_state: The state the car just left
        :param action: the action the car performed to get in new_state
        :param n_steps: number of steps the car has taken so far in the current race
        :param end_of_race: boolean indicating if a race timeout was reached
        :return: The reward to be given to the agent
        """

        if (new_state[ON_TRACK] == 1) or (new_state[ON_TRACK] == 2):
            on_track = 1
        else:
            on_track = -1

        
        if new_state[CHECKPOINT] == 1: # got past a checkpoint
            diff = MAX_POSSIBLE_DIFF  
        else:
            diff = old_state[DIST_CHECKPOINT] - new_state[DIST_CHECKPOINT]
        

        if (old_state[DIST_BOMB] <= 50) and (new_state[DIST_BOMB] == -1):
            bomb_exploded = 1
        else:
            bomb_exploded = -1

        # then we have:
        # on_track and bomb_exploded belonging to {-1; 1}
        # and diff [0, 20]
        reward =    (on_track * 15) + \
                    (bomb_exploded * 15) + \
                    diff

        return reward


    def take_action(self, new_state: State, episode_number: int) -> int:
        """
        Decides which action the car must execute based on its Q-Table and on its exploration policy
        :param new_state: The current state of the car 
        :param episode_number: current episode/race during the training period
        :return: The action the car chooses to execute
        """
        raise NotImplementedError("This method must be implemented")
        #exploration = initial_exploration**log(episode_number)
        #if exploration > exploration_threshold:

        # Exploration policies: Greedy, epsilon greedy, Boltzmann roulette

        action = boltzmann(new_state, episode_number)
        return action

    def epsilon_greedy(self, new_state: State, eps: int):

        if eps <= uniform(0.0, 1.0):
            action, value = self.q_table.get_best_action(new_state)
        else:
            r = randint(self.num_actions)
            action = self.actions.keys[r]
        return action

    def boltzmann(self, state: State, temperature: int):

        evals = []
        for action in self.actions.keys:
            q_value = self.q_table.get_q_value(state, action)
            evals.append(exp(q_value/self.temperature))

        evals /= sum(evals)
        target = uniform(0.0, 1.0)
        roulette = 0
        chosen_action = self.actions.keys[0]

        for i in range(self.num_actions):
            roulette += evals[i]
            if roulette >= target:
                chosen_action = self.actions.keys[i]

        return chosen_action
