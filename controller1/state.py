from itertools import product
from typing import Tuple, List
import interfaces as controller_template
from controller1.sensors import *


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
           11 bomb_detected = 0 or 1
           12 bomb_distance = -1 or 0-???
           13 bomb_position_angle = -180 to 180

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
        
        # angle bomb: ternary, informing which side is dangerous to continue
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


    @staticmethod
    def discretization_levels() -> Tuple:
        """
        This function should return a vector specifying how many discretization levels to use for each state feature.
        :return: A tuple containing the discretization levels of each feature
        """
        
        #check_diff, speed, dist_ahead, dist_left, dist_rigth, dist_bomb, angle_bomb
        #return [5, 5, 5, 3, 3, 2, 2]
        return [5, 5, 3, 3, 2, 3, 2, 2]


    @staticmethod
    def enumerate_all_possible_states() -> List:
        """
        Handy function that generates a list with all possible states of the system.
        :return: List with all possible states
        """
        levels = State.discretization_levels()
        levels_possibilities = [(j for j in range(i)) for i in levels]
        return [i for i in product(*levels_possibilities)]
