"""
This module collects command line arguments and prepares everything needed to run the simulator/game

Example:
    To quickly start the game and observe sensor readings:

        $ python AIRacers.py -t track1 play
"""
import argparse
import pygame
import simulator
from controller1.controller import Controller
from controller2.controller import Controller as Controller2
import tracks_config as track


def play(track, bot_type) -> None:
    """
    Launches the simulator in a mode where the player can control each action with the arrow keys.
    """
    game_state = simulator.Simulation(track, bot_type)
    while True:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    direction = 1
                    feedback = game_state.frame_step(direction)
                    print("sensors  " + str(feedback))
                    print("position " + str(game_state.car1.car_body.position))
                    print("color: " + str(simulator.get_point_from_rgb_list(int(game_state.car1.car_body.position[0])
                                                                            , int(game_state.car1.car_body.position[1])
                                                                            , game_state.car1.track_rgb)))
                elif event.key == pygame.K_LEFT:
                    direction = 2
                    feedback = game_state.frame_step(direction)
                    print("sensors  " + str(feedback))
                    print("position " + str(game_state.car1.car_body.position))
                    print("color: " + str(simulator.get_point_from_rgb_list(int(game_state.car1.car_body.position[0])
                                                                            , int(game_state.car1.car_body.position[1])
                                                                            , game_state.car1.track_rgb)))
                elif event.key == pygame.K_UP:
                    direction = 3
                    feedback = game_state.frame_step(direction)
                    print("sensors  " + str(feedback))
                    print("position " + str(game_state.car1.car_body.position))
                    print("color: " + str(simulator.get_point_from_rgb_list(int(game_state.car1.car_body.position[0])
                                                                            , int(game_state.car1.car_body.position[1])
                                                                            , game_state.car1.track_rgb)))

                elif event.key == pygame.K_DOWN:
                    direction = 4
                    feedback = game_state.frame_step(direction)
                    print("sensors  " + str(feedback))
                    print("position " + str(game_state.car1.car_body.position))
                    print("color: " + str(simulator.get_point_from_rgb_list(int(game_state.car1.car_body.position[0])
                                                                            , int(game_state.car1.car_body.position[1])
                                                                            , game_state.car1.track_rgb)))

                if event.key == pygame.K_q:
                    exit()
                if event.key == pygame.K_r:
                    game_state.reset()
        pass


def parser() -> (argparse.Namespace, list):
    """
    Parses command line arguments.

    :return: a tuple containing parsed arguments and leftovers
    """
    p = argparse.ArgumentParser(prog='AIRacers.py')
    mode_p = p.add_subparsers(dest='mode')
    mode_p.required = True
    p.add_argument('-b', nargs=1, choices=['dumb_bot', 'safe_bot', 'ninja_bot', 'custom_bot', 'none'],
                   help='Selects bot type')
    p.add_argument('-t', nargs=1,
                   help='Specifies the track you want to select; by default, track1 will be used. '
                        'Check the \'tracks.py\' file to see the available tracks/create new ones.\n')
    p.add_argument('-f', nargs=1,
                   help='Specifies the file you want to load your Qtable.\n')
    p.add_argument('-e', nargs=1, type=int,
                   help="Specifies the number of races/episodes that will be executed in learning mode, the default "
                        "value is 100.\n")
    mode_p.add_parser('learn',
                      help='Starts %(prog)s in learning mode. This mode does not render the game to your screen, '
                           'resulting in '
                           'faster learning.\n')
    mode_p.add_parser('evaluate',
                      help='Starts %(prog)s in evaluation mode. This mode runs your AI with the weights/parameters '
                           'passed as parameter \n')
    mode_p.add_parser('play',
                      help='Starts %(prog)s in playing mode. You can control each action of the car using the arrow '
                           'keys of your keyboard.\n')
    mode_p.add_parser('comp',
                      help='Starts %(prog)s in competition mode.\n')
    arguments, leftovers = p.parse_known_args()
    p.parse_args()
    return arguments, leftovers

if __name__ == '__main__':

    args, trash = parser()

    # Selects track; by default track1 will be selected
    chosen_track = track.track1
    if args.t is None:
        chosen_track = track.track1
    else:
        for a_track in track.track.track_list:
            if args.t[0] == a_track.name:
                chosen_track = a_track

    # Selects Bot Type
    if args.b is None:
        bot_type = None
    elif args.b[0] == 'none':
        bot_type = None
    else:
        bot_type = args.b[0]
    if args.f is None:
        table_path = None
    else:
        table_path = args.f[0]
    if args.e is None:
        number_of_episodes = 100
    else:
        number_of_episodes = int(args.e[0])

    # Starts simulator in play mode
    if str(args.mode) == 'play':
        simulator.show_simulation = True
        simulation = simulator.Simulation(chosen_track, bot_type)
        play(chosen_track, bot_type)
    # Starts simulator in evaluate mode
    elif str(args.mode) == 'evaluate':
        simulator.show_simulation = True
        ctrl = Controller(table_path)
        sim = simulator.Simulation(chosen_track, bot_type)
        sim.evaluate(ctrl)
    # Starts simulator in learn mode and saves the best results in a file
    elif str(args.mode) == 'learn':
        simulator.show_simulation = False
        simulation = simulator.Simulation(chosen_track, bot_type)
        ctrl = Controller(table_path)
        simulation.learn(ctrl, number_of_episodes)
    elif str(args.mode) == 'comp':
        simulator.show_simulation = True

        player_1_path = 'controller1/table.txt'
        player_2_path = 'controller2/table.txt'

        player_1_score = 0
        player_2_score = 0

        for current_track in track.track.track_list:

            print("Starting race in %s\n" % current_track.name)

            player_1 = Controller(player_1_path)
            player_2 = Controller2(player_2_path)

            sim = simulator.Simulation(current_track, 'player2')
            sim.evaluate_comp(player_1, player_2)

            print("Player 1 score: %d" % sim.car1.score)
            print("Player 2 score: %d" % sim.car_bot.score)

            if sim.car1.score > sim.car_bot.score:
                print("Player 1 wins and received 3pts")
                player_1_score += 3
            elif sim.car1.score < sim.car_bot.score:
                print("Player 2 wins and received 3pts")
                player_2_score += 3
            else:
                print("Oh no, it's a tie!")

            print("Player 1 points: %d" % player_1_score)
            print("Player 2 points: %d" % player_2_score)

        print("Switching sides...\n")

        for current_track in track.track.track_list:

            print("Starting race in %s\n" % current_track.name)

            current_track.car1_position, current_track.car2_position = current_track.car2_position, current_track.car1_position

            player_1 = Controller(player_1_path)
            player_2 = Controller2(player_2_path)

            sim = simulator.Simulation(current_track, 'player2')
            sim.evaluate_comp(player_1, player_2)

            print("Player 1 score: %d" % sim.car1.score)
            print("Player 2 score: %d" % sim.car_bot.score)

            if sim.car1.score > sim.car_bot.score:
                print("Player 1 wins and received 3pts")
                player_1_score += 3
            elif sim.car1.score < sim.car_bot.score:
                print("Player 2 wins and received 3pts")
                player_2_score += 3
            else:
                print("Oh no, it's a tie!")

            print("Player 1 points: %d" % player_1_score)
            print("Player 2 points: %d" % player_2_score)

        if player_1_score > player_2_score:
            print("Player 1 wins!")
        elif player_1_score < player_2_score:
            print("Player 2 wins!")
        else:
            print("Oh no! It's a tie!")



