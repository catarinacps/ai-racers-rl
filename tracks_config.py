"""
Use this module to define the racing tracks available in the game, or to create new ones.
"""
import track as track
from math import pi




"""
Use this module to define the racing tracks available in the game, or to create new ones.
"""
import track as track
from math import pi


# BABY_PARK BEGINS

baby_park = track.Track('assets/baby_park.png', 'assets/baby_park_textura.png', 'baby_park')

baby_park.episode_length = 500
baby_park.timeout = 30
baby_park.car1_position = (308.67982891788586, 271.57617644235376)
baby_park.car2_position = (308.67982891788586, 231.57617644235376)
baby_park.angle_of_cars = 2*pi - (pi/16)


baby_park.add_checkpoint([(441.1051625641563, 271.6561341001731), (415.2613336278362, 166.55071823782586)])
baby_park.add_checkpoint([(699.5764940803684, 144.4274492589917), (696.9703498893376, 42.46074875115163)])
baby_park.add_checkpoint([(867.5504266698458, 225.0554828206116), (969.0228317305006, 182.5896022668501)])
baby_park.add_checkpoint([(718.7143842588047, 370.0719054776359), (723.9466167152078, 473.94020547105106)])
baby_park.add_checkpoint([(483.77766062797707, 427.6930058157275), (510.7796665619176, 533.2955231888633)])
baby_park.add_checkpoint([(244.81284439972373, 544.8478134831403), (221.275776875401, 644.0950121960279)])
baby_park.add_checkpoint([(142.7653171805199, 496.7199034399432), (52.59500724703348, 550.5187436365408)])
baby_park.add_checkpoint([(109.43016970985042, 269.14011286147985), (166.37622717767763, 358.5445117402318)])


baby_park.add_bomb((682, 70), -pi / 2)
baby_park.add_bomb((724, 448), -pi / 2)
baby_park.add_bomb((302, 567), -pi / 2)
baby_park.add_bomb((196, 311), -pi / 2)

# BABY_PARK ENDS


# INTERLAGOS BEGINS
interlagos = track.Track('assets/interlagos.png', 'assets/interlagos_textura.jpg', 'interlagos')

# Specifies episode length and timeout
interlagos.episode_length = 500
interlagos.timeout = 100

# Determines both cars' positions and initial angles/orientations (in radians)
interlagos.car1_position = (805, 700-458-30-24)
interlagos.car2_position = (813, 700-483-30-26)
interlagos.angle_of_cars = 2*pi + (pi/16)

# Adds checkpoints, in the order they must be crossed

interlagos.add_checkpoint([(925, 1000-436-300), (999, 1000-454-300)])
interlagos.add_checkpoint([(888, 1000-370-300), (970, 1000-370-300)])
interlagos.add_checkpoint([(923, 1000-300-300), (999, 1000-300-300)])
interlagos.add_checkpoint([(870, 1000-230-300), (917, 1000-166-300)])
interlagos.add_checkpoint([(605.9352634660668, 528.3218085366615), (625.8090013891796, 603.7474974030124)])
interlagos.add_checkpoint([(275, 1000-30-300), (308, 1000-99-300)])
interlagos.add_checkpoint([(222, 1000-123-300), (295, 1000-136-300)])
interlagos.add_checkpoint([(248-10, 1000-221-300-10), (293, 1000-180-300)])
interlagos.add_checkpoint([(484, 1000-313-300), (527, 1000-252-300)])
interlagos.add_checkpoint([(606, 1000-408-300), (680, 1000-408-300)])
interlagos.add_checkpoint([(563, 1000-459-300), (592, 1000-525-300)])
interlagos.add_checkpoint([(380, 1000-546-300), (430, 1000-494-300)])
interlagos.add_checkpoint([(375, 1000-442-300), (444, 1000-431-300)])
interlagos.add_checkpoint([(340, 1000-371-300), (364, 1000-441-300)])
interlagos.add_checkpoint([(248, 1000-457-300), (293, 1000-509-300)])
interlagos.add_checkpoint([(175, 1000-506-300), (224, 1000-456-300)])
interlagos.add_checkpoint([(150, 1000-413-300), (222, 1000-422-300)])
interlagos.add_checkpoint([(183, 1000-347-300), (257, 1000-340-300)])
interlagos.add_checkpoint([(131, 1000-285-300), (163, 1000-219-300)])
interlagos.add_checkpoint([(35, 1000-232-300), (91, 1000-280-300)])
interlagos.add_checkpoint([(21, 1000-476-300), (92, 1000-453-300)])
interlagos.add_checkpoint([(198, 1000-628-300), (221, 1000-564-300)])
interlagos.add_checkpoint([(444, 1000-594-300), (457, 1000-663-300)])
interlagos.add_checkpoint([(727, 1000-508-300), (753, 1000-592-300)])


interlagos.add_bomb((-100, -100), -pi / 2)
interlagos.add_bomb((-100, -100), -pi / 2)
interlagos.add_bomb((-100, -100), -pi / 2)
interlagos.add_bomb((-100, -100), -pi / 2)

# INTERLAGOS ENDS




# TRACK1 BEGINS

# Specifies binary image, mask image, and track name
track1 = track.Track('assets/track.png', 'assets/track_mask.png', 'track1')

# Specifies episode length and timeout
track1.episode_length = 500
track1.timeout = 30

# Determines both cars' positions and initial angles/orientations (in radians)
track1.car1_position = (186,124)
track1.car2_position = (186, 124-40)
track1.angle_of_cars = 0

# Adds checkpoints, in the order they must be crossed
track1.add_checkpoint([(278, 68), (284, 162)])
track1.add_checkpoint([(524, 171), (486, 258)])
track1.add_checkpoint([(859, 90), (831, 181)])
track1.add_checkpoint([(937, 391), (853, 339)])
track1.add_checkpoint([(510, 375), (509, 466)])
track1.add_checkpoint([(226, 648), (225, 549)])
track1.add_checkpoint([(96, 346), (181, 374)])

# Specifies parked cars positions and angles/orientations
track1.add_bomb((120, 500), -pi / 2)
track1.add_bomb((250, 620), 0)
track1.add_bomb((500, 390), 0)
track1.add_bomb((720, 470), 0)
track1.add_bomb((880, 430), -pi / 4)
track1.add_bomb((950, 250), -2 * pi / 4)

# TRACK1 ENDS

# TRACK2 BEGINS

track2 = track.Track('assets/track_2.png', 'assets/track_2_mask.png', 'track2')

track2.episode_length = 500
track2.timeout = 30
track2.car1_position = (80, 150)
track2.car2_position = (120, 150)
track2.angle_of_cars = -pi/2


track2.add_checkpoint([(278, 68), (284, 162)])
track2.add_checkpoint([(543, 177), (438, 172)])
track2.add_checkpoint([(427, 328), (349, 392)])
track2.add_checkpoint([(611, 186), (692, 252)])
track2.add_checkpoint([(883, 149), (980, 112)])
track2.add_checkpoint([(835, 342), (740, 334)])
track2.add_checkpoint([(802, 503), (871, 571)])
track2.add_checkpoint([(643., 523), (633, 432)])
track2.add_checkpoint([(457, 692), (459, 594)])
track2.add_checkpoint([(142, 615), (150, 520)])
track2.add_checkpoint([(46, 429), (146, 484)])
track2.add_checkpoint([(180, 351), (280, 370)])


track2.add_bomb((120, 500), -pi / 2)
track2.add_bomb((500, 590), -pi / 4)
track2.add_bomb((870, 430), pi / 2 - pi / 8)
track2.add_bomb((590, 250), -pi / 4)

# TRACK2 ENDS

# TRACK3 BEGINS

track3 = track.Track('assets/track_3.png', 'assets/track_3_mask.png', 'track3')

track3.episode_length = 500
track3.timeout = 30
track3.car1_position = (186,124)
track3.car2_position = (186, 124-40)
track3.angle_of_cars = 0


track3.add_checkpoint([(278, 68), (284, 162)])
track3.add_checkpoint([(524, 171), (486, 258)])
track3.add_checkpoint([(859, 90), (831, 181)])
track3.add_checkpoint([(937, 391), (853, 339)])
track3.add_checkpoint([(702, 452), (703, 552)])
track3.add_checkpoint([(226, 648), (225, 549)])
track3.add_checkpoint([(96, 346), (181, 374)])


track3.add_bomb((110, 500), -pi / 2)
track3.add_bomb((500, 410), 0)
track3.add_bomb((720, 470), 0)
track3.add_bomb((950, 250), -2 * pi / 4)

# TRACK3 ENDS



