

import math


poly = {}

poly['25|-40|30|-35'] = 'this is a correct grid square'


xcoord = 28.203
ycoord = -39.902

upper_x = math.ceil(xcoord/5)*5

upper_y = math.ceil(ycoord/5)*5


lower_x = math.floor(xcoord/5)*5
lower_y = math.floor(ycoord/5)*5


grid_square = [lower_x, lower_y, upper_x, upper_y]
print(grid_square)


try: 
    print(poly[f'{lower_x}|{lower_y}|{upper_x}|{upper_y}'])
except: 
    print('womp womp u wrong')









