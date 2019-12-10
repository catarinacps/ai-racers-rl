import interfaces as controller_template
from controller1.state import State
import pickle


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
        actions = range(1, 6)  # because the interval is [1, 6)

        for state in states:
            state_actions = {}
            for action in actions:
                state_actions[action] = 0  # randint(0,50)
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
            pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)
