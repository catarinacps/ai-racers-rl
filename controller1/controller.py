from random import randint, uniform
from math import exp
import interfaces as controller_template
from controller1.sensors import *
from controller1.state import State
from controller1.qtable import QTable

NUM_OF_ACTIONS = 5
ACT_RIGHT = 1
ACT_LEFT = 2
ACT_ACCEL = 3
ACT_BRAKE = 4
ACT_NONE = 5
MAX_POSSIBLE_DIFF = 20  # maximum speed going straigth towards the checkpoint

class Controller(controller_template.Controller):
    def __init__(self, q_table_path: str, atten: float, alpha: float, init_temp: float, strategy: str):
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
        self.atten = atten
        # Learning rate frame-wise
        self.alpha = alpha
        
        # Exploration
        self.strategy = strategy

        self.temperature = init_temp  
        self.cooling_factor = 0.995

        self.eps = 0.1
        self.eps_factor = 0.99

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
        R_ON_TRACK = 10
        P_NOT_ON_TRACK = -15
        R_BACK_ON_TRACC = 10
        P_WAYWARD_DRIVER = -10


        URGE_CHECKPOINT = -10
        
        BOMB_WARNING = -15

        new_ontrack = 0 if new_state.sensors[ON_TRACK] == 0 else 1
        old_ontrack = 0 if old_state.sensors[ON_TRACK] == 0 else 1

        new_lane = new_state.sensors[ON_TRACK]
        old_lane = old_state.sensors[ON_TRACK]


        reward = 0
        if new_ontrack:
            reward += R_ON_TRACK
        else:
            reward += P_NOT_ON_TRACK
            

        # Driver was out of bounds but found her way (not by Do Nothing)
        if new_ontrack and not old_ontrack and action not in [ACT_BRAKE, ACT_NONE]:
            reward += R_BACK_ON_TRACC
        # Driver was on track but now isn't
        if old_ontrack and not new_ontrack:
            if action == ACT_ACCEL:
                # Accelerated
                reward += 6 * P_WAYWARD_DRIVER
            if action == ACT_BRAKE:
                # Tried to brake at least
                reward += 2 * P_WAYWARD_DRIVER
            if action in [ACT_LEFT, ACT_RIGHT]:
                reward += P_WAYWARD_DRIVER
            if action == ACT_NONE:
                # Did nothing
                reward += 4 * P_WAYWARD_DRIVER

        # Driver was out of bounds and still is
        if not old_ontrack and not new_ontrack:
            if action in [ACT_BRAKE, ACT_NONE]:
                # Hit brakes or Did nothing
                reward += 6 * P_WAYWARD_DRIVER

        # Too close and pointing to a bomb
        if (abs(new_state.sensors[BOMB_ANGLE]) < 45) and (new_state.sensors[BOMB_NEAR] < 30):
            reward += BOMB_WARNING
        # Close but not pointing: avoiding
        if (abs(new_state.sensors[BOMB_ANGLE]) > 45) and (new_state.sensors[BOMB_NEAR] < 30):
            reward += -BOMB_WARNING

        if new_state.sensors[CHECKPOINT] == 1: # got past a checkpoint
            reward += MAX_POSSIBLE_DIFF*2
        else:
            reward += URGE_CHECKPOINT
            diff = old_state.sensors[DIST_CHECKPOINT] - new_state.sensors[DIST_CHECKPOINT]
            reward += 2 * diff

        if old_lane == 0 and new_lane != 0:
            if new_lane == 1 and action == ACT_LEFT:  # turned left and is now too left
                reward += -10
            if new_lane == 2 and action == ACT_RIGHT:  # turned r and is now too r
                reward += -10

        if new_lane == 0:
            reward += 2

        reward += new_state.sensors[SPEED] / 5
        
        return reward
               


    def take_action(self, new_state: State, episode_number: int) -> int:
        """
        Decides which action the car must execute based on its Q-Table and on its exploration policy
        :param new_state: The current state of the car
        :param episode_number: current episode/race during the training period
        :return: The action the car chooses to execute
        """

        # Exploration policies: Epsilon greedy, Boltzmann roulette
        if self.strategy == "boltzmann":
            action = self.boltzmann(new_state, episode_number)
        else:
            action = self.epsilon_greedy(new_state, episode_number)
        # oh dear inheritance, i miss you

        return action

    def epsilon_greedy(self, new_state: State, episode_number: int):
        
        self.weakens_curiosity(episode_number)

        if uniform(0.0, 1.0) <= self.eps:
            action, value = self.q_table.get_best_action(new_state)
        else:
            r = randint(1, self.num_actions)
            action = r
        return action


    def weakens_curiosity(self, episode_number: int):
        if episode_number == self.episode_number or self.eps >= 0.98:
            return 
        
        else:
            self.episode_number = episode_number
            self.eps = self.eps / self.eps_factor
            return


    def boltzmann(self, state: State, episode_number: int):

        self.cooling(episode_number)

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
        
        if episode_number == self.episode_number or self.temperature <= 2:
            return 
        
        else:
            self.episode_number = episode_number
            self.temperature = self.cooling_factor * self.temperature
            return