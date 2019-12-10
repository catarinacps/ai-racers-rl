from random import randint, uniform
from math import exp
import interfaces as controller_template
from controller1.sensors import *
from controller1.state import State
from controller1.qtable import QTable

NUM_OF_ACTIONS = 5
MAX_POSSIBLE_DIFF = 20  # maximum speed going straigth towards the checkpoint


class Controller(controller_template.Controller):
    def __init__(self, q_table_path: str, atten: float, alpha: float, init_temp: float):
        if q_table_path is None:
            self.q_table = QTable()
        else:
            self.q_table = QTable.load(q_table_path)

        # Available actions
        # {1: 'Accel', 2: 'Brake', 3: 'Left', 4: 'Right', 5: 'Nop'}
        self.actions = [1, 2, 3, 4, 5]
        self.num_actions = len(self.actions)

        # Attenuation of benefit
        self.atten = atten
        # Learning rate frame-wise
        self.alpha = alpha
        # Curiosity for worse options
        # self.exploration_initial = 0.9
        # self.exploration_threshold = 0.5

        self.temperature = init_temp  # ???????

    def update_q(self, new_state: State, old_state: State, action: int, reward: float, end_of_race: bool) -> None:
        """

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
        updated = (1-self.alpha)*pref + self.alpha*(reward + self.atten * next_pref)

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

        old_disc = old_state.discretized_state
        new_disc = new_state.discretized_state

        old_checkpoint = old_disc[0]
        new_checkpoint = new_disc[0]

        old_ontrack = old_disc[1]
        new_ontrack = new_disc[1]

        old_lane = old_disc[2]
        new_lane = new_disc[2]

        # old_bomb_angle = old_disc[3]
        # new_bomb_angle = new_disc[3]

        if (new_state.sensors[ON_TRACK] == 1) or (new_state.sensors[ON_TRACK] == 2):
            on_track = 1
        else:
            on_track = -1


        if new_state.sensors[CHECKPOINT] == 1: # got past a checkpoint
            diff = MAX_POSSIBLE_DIFF
        else:
            diff = old_state.sensors[DIST_CHECKPOINT] - new_state.sensors[DIST_CHECKPOINT]


        if (old_state.sensors[DIST_BOMB] <= 50) and (new_state.sensors[DIST_BOMB] == -1):
            bomb_exploded = 1
        else:
            bomb_exploded = -1

        # then we have:
        # on_track and bomb_exploded belonging to {-1; 1}
        # and diff [0, 20]
        reward = (on_track * 15) + (bomb_exploded * 15) + diff


        # normalize reward to [0, 1]
        #reward = (reward - (-35)) / (50 + 35)
        reward = 0
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

        R_ON_TRACK = 10
        P_NOT_ON_TRACK = -15

        R_BACC_ON_TRACC = 10
        P_WAYWARD_DRIVER = -10

        R_CROSSED_CHECKPOINT = 30
        P_CADE_CHECKPOINT = -0
        R_CLEAR_BOMB = 0

        reward = 0
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
                reward += 6 * P_WAYWARD_DRIVER
            if action == 2:
                # Tried to brake at least
                reward += P_WAYWARD_DRIVER
            if action in [3, 4]:
                reward += 2 * P_WAYWARD_DRIVER
            if action == 5:
                # Did nothing
                reward += 4 * P_WAYWARD_DRIVER

        # Driver was out of bounds and still is
        if not old_ontrack and not new_ontrack:
            if action in [2, 5]:
                # Hit brakes or Did nothing
                reward += 6 * P_WAYWARD_DRIVER

        diff = old_state.sensors[DIST_CHECKPOINT] - new_state.sensors[DIST_CHECKPOINT]
        reward += diff

        if old_lane == 0 and new_lane != 0:
            if new_lane == 1 and action == 3:  # turned left and is now too left
                reward += -10
            if new_lane == 2 and action == 4:  # turned r and is now too r
                reward += -10

        if old_lane != 0 and new_lane == 0:
            if old_lane == 1 and action == 4:  # was left and turned right
                reward += 10
            if old_lane == 2 and action == 3:  # was r and turned L
                reward += 10

        if new_lane == 0:
            reward += 2
        if old_lane != 0:
            reward += -1

        # if old_bomb_angle != 0 and new_bomb_angle == 0:
        #     #desviou
        #     if old_bomb_angle != 0 and action in [3,4]:
        #         reward += 10

        return reward

    def take_action(self, new_state: State, episode_number: int) -> int:
        """
        Decides which action the car must execute based on its Q-Table and on its exploration policy
        :param new_state: The current state of the car
        :param episode_number: current episode/race during the training period
        :return: The action the car chooses to execute
        """
        # exploration = initial_exploration**log(episode_number)
        # if exploration > exploration_threshold:

        # Exploration policies: Greedy, epsilon greedy, Boltzmann roulette

        # action = self.boltzmann(new_state, episode_number+1) #+1 to avoid division by zero
        action = self.epsilon_greedy(new_state, 0.5)
        return action

    def epsilon_greedy(self, new_state: State, eps: int):

        if eps <= uniform(0.0, 1.0):
            action, value = self.q_table.get_best_action(new_state)
        else:
            r = randint(1, self.num_actions)
            action = r
        return action

    def boltzmann(self, state: State, temperature: int):

        evals = []
        for action in self.actions:
            q_value = self.q_table.get_q_value(state, action)
            evals.append(exp(q_value/temperature))

        evals = [x/sum(evals) for x in evals]
        target = uniform(0.0, 1.0)
        roulette = 0
        chosen_action = self.actions[0]

        for i in range(self.num_actions):

            roulette += evals[i]
            if roulette >= target:
                chosen_action = i

        return chosen_action
