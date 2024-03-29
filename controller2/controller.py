import interfaces as controller_template
from itertools import product
from typing import Tuple, List
from random import randint, uniform
from math import exp
import pickle

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

        self.discretized_state = self.discretize_features(self.compute_features())

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
        if (self.sensors[CHECKPOINT] == 1) or (self.prev_sens[DIST_CHECKPOINT] == 0):
            check_diff = 20
        else:
            check_diff = self.prev_sens[DIST_CHECKPOINT] - self.sensors[DIST_CHECKPOINT]


        return [check_diff]

    


    def discretize_features(self, features: Tuple) -> Tuple:
        """
        This function should map the (possibly continuous) features (calculated by compute features) and discretize them.
        :param features 
        :return: A tuple containing the discretized features
        """

        # we consider a 5 levels discretization having the levels 0, 1, 2, 3 and 4
        check_diff = features[0] // 4 if features[0] < 20 else 4 
        speed = self.sensors[SPEED] // 40 if self.sensors[SPEED] < 200 else 4 
        dist_ahead = self.sensors[DIST_CENTER] // 20 if self.sensors[DIST_CENTER] < 100 else 4

        # we consider a 3 levels discretization having the levels 0, 1 and 2
        dist_left = self.sensors[DIST_LEFT] // 33 if self.sensors[DIST_LEFT] < 99 else 2
        dist_rigth = self.sensors[DIST_RIGHT] // 33 if self.sensors[DIST_RIGHT] < 99 else 2

        # dist bomb: binary, either too close to a bomb or not
        dist_bomb = 0 if self.sensors[DIST_BOMB] > 50 else 1
        
        if abs(self.sensors[BOMB_ANGLE]) >= 45:
            angle_bomb = 0
        elif self.sensors[BOMB_ANGLE] < 0:
            angle_bomb = 1
        else:
            angle_bomb = 2

        on_ice = 1 if self.sensors[ON_TRACK] == 2 else 0
        on_grass = 1 if self.sensors[ON_TRACK] == 0 else 0
        #return (check_diff, speed, dist_ahead, dist_left, dist_rigth, dist_bomb, angle_bomb)
        return (speed, dist_ahead, dist_left, 
                dist_rigth, dist_bomb, angle_bomb, on_ice, 
                on_grass,)
        #return (check_diff, speed, dist_ahead, dist_left, 
         #       dist_rigth, on_ice, on_grass)

    @staticmethod
    def discretization_levels() -> Tuple:
        """
        This function should return a vector specifying how many discretization levels to use for each state feature.
        :return: A tuple containing the discretization levels of each feature
        """
        
        #check_diff, speed, dist_ahead, dist_left, dist_rigth, dist_bomb, angle_bomb
        #return [5, 5, 5, 3, 3, 2, 2]
        return [5, 5, 3, 3, 2, 3, 2, 2]
        #return [5, 5, 5, 3, 3, 2, 2]


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
        self.q_table = {}

        states = State.enumerate_all_possible_states()
        actions = range(1,6) # because the interval is [1, 6)

        for state in states:
            state_actions = {}
            for action in actions:
                state_actions[action] = 0#randint(0,50)
            self.q_table[state] = state_actions


    def get_q_value(self, key: State, action: int) -> float:
        """
        Used to securely access the values within this q-table
        :param key: a State object 
        :param action: an action
        :return: The Q-value associated with the given state/action pair
        """
        key = key.discretized_state
        q_value = self.q_table[key][action]
        return q_value

    def set_q_value(self, key: State, action: int, new_q_value: float) -> None:
        """
        Used to securely set the values within this q-table
        :param key: a State object 
        :param action: an action
        :param new_q_value: the new Q-value to associate with the specified state/action pair
        :return: 
        """
        key = key.discretized_state
        self.q_table[key][action] = new_q_value


    def get_best_action(self, key: State) -> (int, int):
        
        key = key.discretized_state
        values = self.q_table[key]
        best_action = max(values)
        best_q_value = self.q_table[key][best_action]
        return best_action, best_q_value


    @staticmethod
    def load(path: str) -> "QTable":
        """
        This method should load a Q-table from the specified file and return a corresponding QTable object
        :param path: path to file
        :return: a QTable object
        """
        with open(path, 'rb') as handle:
            q_table = pickle.load(handle)
        return q_table


    def save(self, path: str, *args) -> None:
        """
        This method must save this QTable to disk in the file file specified by 'path'
        :param path: 
        :param args: Any optional args you may find relevant; beware that they are optional and the function must work
                     properly without them.
        """
        with open(path, 'wb') as handle:
            pickle.dump(self    , handle, protocol=pickle.HIGHEST_PROTOCOL)
        return


class Controller(controller_template.Controller):
    def __init__(self, q_table_path: str):
        if q_table_path is None:
            self.q_table = QTable()
        else:
            self.q_table = QTable.load(q_table_path)

        # Available actions
        # {1: 'Right', 2: 'Left, 3: 'Accel', 4: 'Brake',  5: 'Nop'}
        self.actions = [1,2,3,4,5]
        self.num_actions = len(self.actions)
        
        self.checkpoints_reached = 0
        self.episode_number = 0

        # Attenuation of benefit
        self.atten = 0.9
        # Learning rate frame-wise
        self.alpha = 0.5
        # Curiosity for worse options
        # self.exploration_initial = 0.9
        # self.exploration_threshold = 0.5

        self.temperature = 90
        self.cooling_factor = 0.99


    def update_q(self, new_state: State, old_state: State, action: int, reward: float, end_of_race: bool) -> None:
        """
        This method is called by the learn() method in simulator.Simulation() to update your Q-table after each action is taken
        :param new_state: The state the car just entered
        :param old_state: The state the car just left
        :param action: the action the car performed to get to new_state
        :param reward: the reward the car received for getting to new_state  
        :param end_of_race: boolean indicating if a race timeout was reached
        """

        pref = self.q_table.get_q_value(old_state, action)
        next_action, next_pref = self.q_table.get_best_action(new_state)
        # Q-Learning equation:
        # Alpha rate of learning, gamma time attenuation of future benefit
        updated = (1-self.alpha)*pref + self.alpha*(reward + self.atten*next_pref)

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

        
        if (new_state.sensors[ON_TRACK] == 1) or (new_state.sensors[ON_TRACK] == 2):
            on_track = 1
        else:
            on_track = -1

        
        if new_state.sensors[CHECKPOINT] == 1: # got past a checkpoint
            diff = MAX_POSSIBLE_DIFF
            
        else:
            diff = old_state.sensors[DIST_CHECKPOINT] - new_state.sensors[DIST_CHECKPOINT]

        bomb_warning = 0
        if abs(new_state.sensors[BOMB_ANGLE]) < 45:
            bomb_warning = -15     

        speed_bonus = 5 if action == 3 else 0

        reward =    (on_track * 20) + \
                    bomb_warning + \
                    diff + \
                    speed_bonus
                    
        return reward
               

        """
        new_checkpoint = new_state.sensors[CHECKPOINT]

        old_ontrack = 0 if old_state.sensors[ON_TRACK] == 0 else 1
        new_ontrack = 0 if new_state.sensors[ON_TRACK] == 0 else 1

        old_lane = old_state.sensors[ON_TRACK]
        new_lane = new_state.sensors[ON_TRACK]
        reward = 0
        """

        """
        if old_state.sensors[ON_TRACK] == 0 and new_state.sensors[ON_TRACK] == 1:
            reward += 30
        elif new_state == 1:
            reward += 15
        elif old_state.sensors[ON_TRACK] == 1 and new_state.sensors[ON_TRACK] == 0:
            reward += -50
        else:
            reward += -15

        if new_state.sensors[CHECKPOINT] == 1:
            difference = 100
        else:
            difference = old_state.sensors[DIST_CHECKPOINT] - new_state.sensors[DIST_CHECKPOINT]

        reward += difference

        if abs(new_state.sensors[BOMB_ANGLE]) < 45:
            if new_state.sensors[BOMB_ANGLE] >= 0:
                if action not in [3, 4]:
                    reward += -15
            if new_state.sensors[BOMB_ANGLE] < 0:
                if action not in [3, 4]:
                    reward += -15
        """
        """
        R_ON_TRACK = 10
        P_NOT_ON_TRACK = -15

        R_BACC_ON_TRACC = 10
        P_WAYWARD_DRIVER = -10

        R_CROSSED_CHECKPOINT = 30
        P_CADE_CHECKPOINT = -0
        R_CLEAR_BOMB = 0


        if new_ontrack:
            reward += R_ON_TRACK
        else:
            reward += P_NOT_ON_TRACK
        if new_checkpoint:
            reward += R_CROSSED_CHECKPOINT
        else:
            reward += P_CADE_CHECKPOINT
        # if new_bomb_angle == 0:
        #     reward += R_CLEAR_BOMB

        # Driver was out of bounds but found her way (not by Do Nothing)
        if new_ontrack and not old_ontrack and action not in [2, 5]:
            reward += R_BACC_ON_TRACC
        # Driver was on track but now isn't
        if old_ontrack and not new_ontrack:
            if action == 1:
                # Accelerated
                reward += 6*P_WAYWARD_DRIVER
            if action == 2:
                # Tried to brake at least
                reward += P_WAYWARD_DRIVER
            if action in [3,4]:
                reward += 2*P_WAYWARD_DRIVER
            if action == 5:
                # Did nothing
                reward += 4*P_WAYWARD_DRIVER

        # Driver was out of bounds and still is
        if not old_ontrack and not new_ontrack:
            if action in [2,5]:
                # Hit brakes or Did nothing
                reward += 6*P_WAYWARD_DRIVER

        diff = old_state.sensors[DIST_CHECKPOINT] - new_state.sensors[DIST_CHECKPOINT]
        reward += diff

        if old_lane == 0 and new_lane != 0:
            if new_lane == 1 and action == 3: # turned left and is now too left
                reward += -10
            if new_lane == 2 and action == 4: # turned r and is now too r
                reward += -10

        if old_lane != 0 and new_lane == 0:
            if old_lane == 1 and action == 4: # was left and turned right
                reward += 10
            if old_lane == 2 and action == 3: # was r and turned L
                reward += 10

        if new_lane == 0:
            reward += 2
        if old_lane != 0:
            reward += -1
        """
        return reward

    def take_action(self, new_state: State, episode_number: int) -> int:
        """
        Decides which action the car must execute based on its Q-Table and on its exploration policy
        :param new_state: The current state of the car 
        :param episode_number: current episode/race during the training period
        :return: The action the car chooses to execute
        """
        #exploration = initial_exploration**log(episode_number)
        #if exploration > exploration_threshold:

        # Exploration policies: Greedy, epsilon greedy, Boltzmann roulette

        action = self.boltzmann(new_state)
        self.temperature = self.cooling(episode_number)
        return action

    def epsilon_greedy(self, new_state: State, eps: int):

        if eps <= uniform(0.0, 1.0):
            action, value = self.q_table.get_best_action(new_state)
        else:
            r = randint(1, self.num_actions)
            action = r
        return action

    def boltzmann(self, state: State):

        evals = []
        for action in self.actions:
            q_value = self.q_table.get_q_value(state, action)
            try:
                evals.append(exp(q_value/self.temperature))
            except:
                print("q val:", q_value)
                print("temp:", self.temperature)
                input()

        evals = [x/sum(evals) for x in evals]
        
        target = uniform(0, 1)
        roulette = 0

        for i in range(1, self.num_actions+1):

            roulette += evals[i-1]
            if roulette >= target:
                return i
                


    def cooling(self, episode_number: int):
        
        if episode_number == self.episode_number or self.temperature <= 1:
            return self.temperature
        
        else:
            self.episode_number = episode_number
            return self.cooling_factor * self.temperature