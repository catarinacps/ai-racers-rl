from itertools import product
from typing import List, Tuple, Any


primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
          103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193)


class State:
    def __init__(self, sensors: list):
        self.sensors = sensors

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
           11 bomb_distance = -1 or 0-???
           12 bomb_position_angle = -180 to 180
           13 bomb_detected = 0 or 1
          (see the specification file/manual for more details)
        :return: A Tuple containing the features you defined
        """
        raise NotImplementedError("This method must be implemented")

    def discretize_features(self, features: Tuple) -> Tuple:
        """
        This function should map the (possibly continuous) features (calculated by compute features) and discretize them.
        :param features 
        :return: A tuple containing the discretized features
        """
        raise NotImplementedError("This method must be implemented")

    @staticmethod
    def discretization_levels() -> Tuple:
        """
        This function should return a vector specifying how many discretization levels to use for each state feature.
        :return: A tuple containing the discretization levels of each feature
        """
        raise NotImplementedError("This method must be implemented")

    def get_current_state(self):
        """
        :return: computes the discretized features associated with this state object.
        """
        features = self.discretize_features(self.compute_features())
        return features

    @staticmethod
    def get_state_id(discretized_features: Tuple) -> int:
        """
        Handy function that calculates an unique integer identifier associated with the discretized state passed as parameter
        :param discretized_features
        :return: unique key
        """

        terms = [primes[i] ** discretized_features[i] for i in range(len(discretized_features))]

        s_id = 1
        for i in range(len(discretized_features)):
            s_id = s_id * terms[i]

        return s_id

    @staticmethod
    def get_number_of_states() -> int:
        """
        Handy function that computes the total number of possible states that exist in the system, according to the
        discretization levels specified by the user.
        :return: 
        """
        v = State.discretization_levels()
        num = 1

        for i in (v):
            num *= i

        return num

    @staticmethod
    def enumerate_all_possible_states() -> List:
        """
        Handy function that generates a list with all possible states of the system.
        :return: List with all possible states
        """

        levels = State.discretization_levels()

        levels_possibilities = [(j for j in range(i)) for i in levels]

        return [i for i in product(*levels_possibilities)]


class QTable:
    def __init__(self):
        """
        This class is used to create/load/store your Q-table. To store values we strongly recommend the use of a Python
        dictionary.
        """
        raise NotImplementedError()

    def get_q_value(self, key: State, action: int) -> float:
        """
        Used to securely access the values within this q-table
        :param key: a State object 
        :param action: an action
        :return: The Q-value associated with the given state/action pair
        """
        raise NotImplementedError()

    def set_q_value(self, key: State, action: int, new_q_value: float) -> None:
        """
        Used to securely set the values within this q-table
        :param key: a State object 
        :param action: an action
        :param new_q_value: the new Q-value to associate with the specified state/action pair
        :return: 
        """
        raise NotImplementedError()

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


class Controller:
    def __init__(self, q_table: str):
        pass

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

    def compute_reward(self, new_state: State, old_state: State, action: int, n_steps: int, end_of_race: bool) -> float:
        """
        This method is called by the learn() method in simulator.Simulation() to calculate the reward to be given to the agent
        :param new_state: The state the car just entered
        :param old_state: The state the car just left
        :param action: the action the car performed to get in new_state
        :param n_steps: number of steps the car has taken so far in the current race
        :param end_of_race: boolean indicating if a race timeout was reached
        :return: The reward to be given to the agent
        """
        raise NotImplementedError("This method must be implemented")

    def take_action(self, new_state: State, episode_number: int) -> int:
        """
        Decides which action the car must execute based on its Q-Table and on its exploration policy
        :param new_state: The current state of the car 
        :param episode_number: current episode/race during the training period
        :return: The action the car chooses to execute
        """
        raise NotImplementedError("This method must be implemented")
