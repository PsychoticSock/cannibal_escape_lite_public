new_hunter_castles = [{'x': 105, 'y': 121}, {'x': 106, 'y': 94}, {'x': 98, 'y': 94}]
new_hunter_wonder = [{'x': 98, 'y': 121}]
new_hunter_walls = [{'x': 93, 'y': 117}, {'x': 93, 'y': 118}, {'x': 109, 'y': 125}, {'x': 93, 'y': 123}, {'x': 93, 'y': 124}, {'x': 93, 'y': 125}, {'x': 94, 'y': 125}, {'x': 110, 'y': 117}, {'x': 110, 'y': 118}, {'x': 110, 'y': 119}, {'x': 108, 'y': 125}, {'x': 110, 'y': 124}, {'x': 110, 'y': 125}, {'x': 95, 'y': 125}, {'x': 93, 'y': 98}, {'x': 110, 'y': 98}, {'x': 93, 'y': 97}, {'x': 108, 'y': 90}, {'x': 109, 'y': 90}, {'x': 110, 'y': 97}, {'x': 110, 'y': 96}, {'x': 93, 'y': 90}, {'x': 94, 'y': 90}, {'x': 95, 'y': 90}, {'x': 93, 'y': 91}, {'x': 93, 'y': 96}, {'x': 110, 'y': 91}, {'x': 110, 'y': 90}]
new_hunter_gate_up = [{'x': 98, 'y': 125}, {'x': 106, 'y': 125}, {'x': 102, 'y': 125}, {'x': 106, 'y': 90}, {'x': 102, 'y': 90}, {'x': 98, 'y': 90}]
new_hunter_gate_down = [{'x': 93, 'y': 121}, {'x': 110, 'y': 122}, {'x': 93, 'y': 94}, {'x': 110, 'y': 94}]
new_hunter_gate_placeholder = [{'x': 93, 'y': 92}, {'x': 93, 'y': 93}, {'x': 93, 'y': 94}, {'x': 93, 'y': 95}, {'x': 96, 'y': 90}, {'x': 97, 'y': 90}, {'x': 98, 'y': 90}, {'x': 99, 'y': 90}, {'x': 100, 'y': 90}, {'x': 101, 'y': 90}, {'x': 102, 'y': 90}, {'x': 103, 'y': 90}, {'x': 104, 'y': 90}, {'x': 105, 'y': 90}, {'x': 106, 'y': 90}, {'x': 107, 'y': 90}, {'x': 110, 'y': 92}, {'x': 110, 'y': 93}, {'x': 110, 'y': 94}, {'x': 110, 'y': 95}, {'x': 110, 'y': 120}, {'x': 110, 'y': 121}, {'x': 110, 'y': 122}, {'x': 110, 'y': 123}, {'x': 107, 'y': 125}, {'x': 106, 'y': 125}, {'x': 105, 'y': 125}, {'x': 104, 'y': 125}, {'x': 103, 'y': 125}, {'x': 102, 'y': 125}, {'x': 101, 'y': 125}, {'x': 100, 'y': 125}, {'x': 99, 'y': 125}, {'x': 98, 'y': 125}, {'x': 97, 'y': 125}, {'x': 96, 'y': 125}, {'x': 93, 'y': 122}, {'x': 93, 'y': 121}, {'x': 93, 'y': 120}, {'x': 93, 'y': 119}]
new_hunter_smoke = [{'x': 92, 'y': 98}, {'x': 92, 'y': 93}, {'x': 92, 'y': 89}, {'x': 98, 'y': 89}, {'x': 103, 'y': 89}, {'x': 108, 'y': 89}, {'x': 111, 'y': 92}, {'x': 111, 'y': 95}, {'x': 111, 'y': 99}, {'x': 111, 'y': 117}, {'x': 111, 'y': 121}, {'x': 111, 'y': 126}, {'x': 107, 'y': 126}, {'x': 103, 'y': 126}, {'x': 98, 'y': 126}, {'x': 92, 'y': 126}, {'x': 92, 'y': 121}, {'x': 92, 'y': 116}]

"""new_hunter_areas = [new_hunter_castles,
                    new_hunter_wonder,
                    new_hunter_walls,
                    new_hunter_gate_up,
                    new_hunter_gate_down,
                    new_hunter_gate_placeholder]
area_list_x = []
area_list_y = []
for area in new_hunter_areas:
    for tile in area:
        area_list_x.append(tile['x'])
        area_list_y.append(tile['y'])
print(min(area_list_x))
print(min(area_list_y))
print(max(area_list_x))
print(max(area_list_y))"""

new_hunter_top_left_area = {'x1': 93, 'y1': 90, 'x2': 101, 'y2': 101 }
new_hunter_top_right_area = {'x1': 102, 'y1': 90, 'x2': 110, 'y2': 101 }
new_hunter_bottom_left_area = {'x1': 93, 'y1': 116, 'x2': 101, 'y2': 125}
new_hunter_bottom_right_area = {'x1': 102, 'y1': 116, 'x2': 110, 'y2': 125 }
new_hunter_top_left_exit = {'x': 90, 'y': 87}
new_hunter_top_right_exit = {'x': 113, 'y': 87}
new_hunter_bottom_left_exit = {'x': 90, 'y': 128}
new_hunter_bottom_right_exit ={'x': 113, 'y': 128}

new_hunter_exit_areas = [{'area':new_hunter_top_left_area, 'exit':new_hunter_top_left_exit},
                         {'area':new_hunter_top_right_area, 'exit':new_hunter_top_right_exit},
                         {'area':new_hunter_bottom_left_area, 'exit':new_hunter_bottom_left_exit},
                         {'area':new_hunter_bottom_right_area, 'exit':new_hunter_bottom_right_exit}]

for exit in new_hunter_exit_areas:
    print(exit['area']['x1'])
    print(exit['exit']['x'])