
class one:
    def __init__(me2):
        me2.name = 'England'
        me2._file_dir = 'bin/maps/one/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 1312, 233

    def layer(me2, layer: int):
       
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((1312, 233, 32, 183), (1428, 513, 215, 27), (1376, 665, 32, 183), (928, 665, 32, 183),
                    (512, 665, 32, 183), (276, 513, 215, 27), (512, 233, 32, 183), (928, 233, 32, 183))
        else:
            raise ValueError("one.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
        
        if pos == 1:
            return me2._start[0] - 77, me2._start[1] + 52, 270
        elif pos == 2:
            return me2._start[0] - 77, me2._start[1] + 122, 270
        elif pos == 3:
            return me2._start[0] - 192, me2._start[1] + 52, 270
        elif pos == 4:
            return me2._start[0] - 192, me2._start[1] + 122, 270
        elif pos == 5:
            return me2._start[0] - 307, me2._start[1] + 52, 270
        elif pos == 6:
            return me2._start[0] - 307, me2._start[1] + 122, 270
        else:
            raise ValueError("one.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class two:
    def __init__(me2):
        me2.name = 'Pool'
        me2._file_dir = 'bin/maps/two/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 930, 773

    def layer(me2, layer: int):
       
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((930, 773, 32, 183), (1172, 675, 216, 27), (1472, 449, 32, 183), (1556, 351, 216, 27),
                    (1376, 125, 32, 183), (928, 125, 32, 183), (660, 351, 216, 27), (480, 449, 32, 183),
                    (148, 675, 216, 27), (544, 773, 32, 183))
        else:
            raise ValueError("two.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
       
        if pos == 1:
            return me2._start[0] - 77, me2._start[1] + 52, 270
        elif pos == 2:
            return me2._start[0] - 77, me2._start[1] + 122, 270
        elif pos == 3:
            return me2._start[0] - 192, me2._start[1] + 52, 270
        elif pos == 4:
            return me2._start[0] - 192, me2._start[1] + 122, 270
        elif pos == 5:
            return me2._start[0] - 307, me2._start[1] + 52, 270
        elif pos == 6:
            return me2._start[0] - 307, me2._start[1] + 122, 270
        else:
            raise ValueError("two.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class three:
    def __init__(me2):
        me2.name = 'Desert 1'
        me2._file_dir = 'bin/maps/three/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 706, 341

    def layer(me2, layer: int):
       
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((706, 341, 32, 183), (367, 125, 32, 183), (148, 432, 216, 27), (148, 675, 216, 27),
                    (448, 773, 31, 183), (768, 665, 32, 183), (1120, 665, 32, 183), (1440, 773, 32, 183),
                    (1556, 675, 216, 27), (1556, 432, 216, 27), (1521, 125, 31, 183), (1184, 341, 31, 183))
        else:
            raise ValueError("three.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
       
        if pos == 1:
            return me2._start[0] + 109, me2._start[1] + 52, 90
        elif pos == 2:
            return me2._start[0] + 109, me2._start[1] + 122, 90
        elif pos == 3:
            return me2._start[0] + 224, me2._start[1] + 52, 90
        elif pos == 4:
            return me2._start[0] + 224, me2._start[1] + 122, 90
        elif pos == 5:
            return me2._start[0] + 339, me2._start[1] + 52, 90
        elif pos == 6:
            return me2._start[0] + 339, me2._start[1] + 122, 90
        else:
            raise ValueError("three.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class four:
    def __init__(me2):
        me2.name = 'Siberia'
        me2._file_dir = 'bin/maps/four/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 1184, 125

    def layer(me2, layer: int):
     
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((1184, 125, 32, 183), (1472, 124, 32, 183), (1556, 459, 216, 27), (1556, 702, 216, 27),
                    (1408, 773, 32, 183), (1044, 702, 216, 27), (928, 449, 32, 183), (660, 675, 216, 27),
                    (576, 773, 32, 183), (148, 702, 216, 27), (148, 351, 216, 27), (448, 125, 32, 183),
                    (736, 125, 32, 183))
        else:
            raise ValueError("four.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
  
        if pos == 1:
            return me2._start[0] - 77, me2._start[1] + 52, 270
        elif pos == 2:
            return me2._start[0] - 77, me2._start[1] + 122, 270
        elif pos == 3:
            return me2._start[0] - 192, me2._start[1] + 52, 270
        elif pos == 4:
            return me2._start[0] - 192, me2._start[1] + 122, 270
        elif pos == 5:
            return me2._start[0] - 307, me2._start[1] + 52, 270
        elif pos == 6:
            return me2._start[0] - 307, me2._start[1] + 122, 270
        else:
            raise ValueError("four.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class five:
    def __init__(me2):
        me2.name = 'Silverstone'
        me2._file_dir = 'bin/maps/five/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 704, 773

    def layer(me2, layer: int):
   
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((704, 773, 32, 183), (148, 675, 215, 27), (448, 449, 32, 183), (660, 324, 215, 27),
                    (992, 125, 32, 183), (1280, 341, 32, 183), (1556, 540, 215, 27), (1504, 773, 32, 183),
                    (1120, 773, 32, 183))
        else:
            raise ValueError("five.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
  
        if pos == 1:
            return me2._start[0] + 109, me2._start[1] + 52, 90
        elif pos == 2:
            return me2._start[0] + 109, me2._start[1] + 122, 90
        elif pos == 3:
            return me2._start[0] + 224, me2._start[1] + 52, 90
        elif pos == 4:
            return me2._start[0] + 224, me2._start[1] + 122, 90
        elif pos == 5:
            return me2._start[0] + 339, me2._start[1] + 52, 90
        elif pos == 6:
            return me2._start[0] + 339, me2._start[1] + 122, 90
        else:
            raise ValueError("five.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class six:
    def __init__(me2):
        me2.name = 'Medina'
        me2._file_dir = 'bin/maps/six/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 1060, 449

    def layer(me2, layer: int):
     
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((1060, 449, 32, 183), (1172, 351, 215, 27), (1440, 125, 32, 183), (1556, 351, 215, 27),
                    (1556, 675, 215, 27), (1440, 773, 32, 183), (960, 773, 32, 183), (416, 773, 32, 183),
                    (148, 675, 215, 27), (448, 449, 32, 183))
        else:
            raise ValueError("six.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
      
        if pos == 1:
            return me2._start[0] - 77, me2._start[1] + 52, 270
        elif pos == 2:
            return me2._start[0] - 77, me2._start[1] + 122, 270
        elif pos == 3:
            return me2._start[0] - 192, me2._start[1] + 52, 270
        elif pos == 4:
            return me2._start[0] - 192, me2._start[1] + 122, 270
        elif pos == 5:
            return me2._start[0] - 307, me2._start[1] + 52, 270
        elif pos == 6:
            return me2._start[0] - 307, me2._start[1] + 122, 270
        else:
            raise ValueError("six.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class seven:
    def __init__(me2):
        me2.name = 'Arabia'
        me2._file_dir = 'bin/maps/seven/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 1444, 125

    def layer(me2, layer: int):
      
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((1444, 125, 32, 183), (1556, 432, 215, 27), (1556, 702, 215, 27), (1440, 773, 32, 183),
                    (1172, 675, 215, 27), (1056, 449, 32, 183), (788, 675, 215, 27), (704, 773, 32, 183),
                    (416, 773, 32, 183), (148, 675, 215, 27), (416, 449, 31, 183), (532, 378, 215, 27),
                    (768, 125, 32, 183), (992, 125, 32, 183))
        else:
            raise ValueError("seven.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
      
        if pos == 1:
            return me2._start[0] - 77, me2._start[1] + 52, 270
        elif pos == 2:
            return me2._start[0] - 77, me2._start[1] + 122, 270
        elif pos == 3:
            return me2._start[0] - 192, me2._start[1] + 52, 270
        elif pos == 4:
            return me2._start[0] - 192, me2._start[1] + 122, 270
        elif pos == 5:
            return me2._start[0] - 307, me2._start[1] + 52, 270
        elif pos == 6:
            return me2._start[0] - 307, me2._start[1] + 122, 270
        else:
            raise ValueError("seven.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class eight:
    def __init__(me2):
        me2.name = 'Canada'
        me2._file_dir = 'bin/maps/eight/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 1060, 125

    def layer(me2, layer: int):
      
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((1060, 125, 32, 183), (1172, 351, 215, 27), (1440, 449, 32, 183), (1556, 675, 215, 27),
                    (1472, 773, 32, 183), (1184, 773, 32, 183), (916, 675, 215, 27), (832, 449, 32, 183),
                    (416, 449, 32, 183), (148, 351, 215, 27), (416, 125, 32, 183), (672, 125, 32, 183))
        else:
            raise ValueError("eight.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
       
        if pos == 1:
            return me2._start[0] - 77, me2._start[1] + 52, 270
        elif pos == 2:
            return me2._start[0] - 77, me2._start[1] + 122, 270
        elif pos == 3:
            return me2._start[0] - 192, me2._start[1] + 52, 270
        elif pos == 4:
            return me2._start[0] - 192, me2._start[1] + 122, 270
        elif pos == 5:
            return me2._start[0] - 307, me2._start[1] + 52, 270
        elif pos == 6:
            return me2._start[0] - 307, me2._start[1] + 122, 270
        else:
            raise ValueError("eight.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class nine:
    def __init__(me2):
        me2.name = 'Madripoor'
        me2._file_dir = 'bin/maps/nine/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 1316, 125

    def layer(me2, layer: int):
       
        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((1316, 125, 32, 183), (1556, 324, 215, 27), (1300, 648, 215, 27), (1215, 773, 32, 183),
                    (916, 675, 215, 27), (800, 449, 32, 183), (532, 676, 215, 27), (448, 773, 32, 183),
                    (148, 675, 215, 27), (148, 351, 215, 27), (448, 125, 32, 183), (864, 125, 32, 183))
        else:
            raise ValueError("nine.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):
        
        if pos == 1:
            return me2._start[0] - 77, me2._start[1] + 52, 270
        elif pos == 2:
            return me2._start[0] - 77, me2._start[1] + 122, 270
        elif pos == 3:
            return me2._start[0] - 192, me2._start[1] + 52, 270
        elif pos == 4:
            return me2._start[0] - 192, me2._start[1] + 122, 270
        elif pos == 5:
            return me2._start[0] - 307, me2._start[1] + 52, 270
        elif pos == 6:
            return me2._start[0] - 307, me2._start[1] + 122, 270
        else:
            raise ValueError("nine.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


class ten:
    def __init__(me2):
        me2.name = 'Night Turn'
        me2._file_dir = 'bin/maps/ten/'
        me2._bg = 'background.png'
        me2._obj = 'objects.png'
        me2._trk = 'track.png'
        me2._start = 1218, 773

    def layer(me2, layer: int):

        if layer == 0:
            return me2._file_dir + me2._bg
        elif layer == 1:
            return me2._file_dir + me2._obj
        elif layer == 2:
            return me2._file_dir + me2._trk
        elif layer == 3:
            return ((1218, 773, 32, 183), (864, 557, 32, 183), (480, 773, 32, 183), (148, 702, 215, 27),
                    (148, 540, 215, 27), (416, 341, 32, 183), (768, 125, 32, 183), (1137, 341, 32, 183),
                    (1408, 125, 32, 183), (1556, 351, 215, 27), (1556, 648, 215, 27))
        else:
            raise ValueError("ten.layer(layer) | 'layer' must be between 0 and 3 not " + str(layer))

    def start_pos(me2, pos: int):

        if pos == 1:
            return me2._start[0] + 109, me2._start[1] + 52, 90
        elif pos == 2:
            return me2._start[0] + 109, me2._start[1] + 122, 90
        elif pos == 3:
            return me2._start[0] + 224, me2._start[1] + 52, 90
        elif pos == 4:
            return me2._start[0] + 224, me2._start[1] + 122, 90
        elif pos == 5:
            return me2._start[0] + 339, me2._start[1] + 52, 90
        elif pos == 6:
            return me2._start[0] + 339, me2._start[1] + 122, 90
        else:
            raise ValueError("ten.start_pos(pos) | 'pos' must be between 1 and 6 not " + str(pos))


index = ('England', 'Pool', 'Desert 1', 'Siberia', 'Silverstone', 'Medina', 'Arabia', 'Canada', 'Madripoor', 'Night Turn')
objs = (one, two, three, four, five, six, seven, eight, nine, ten)
