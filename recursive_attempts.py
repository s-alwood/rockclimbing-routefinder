import core_methods as cm
import preprocessing as prp
import random

randomness = 22 

def route_aware_fnm(graph, depth, pos=()):
    if not pos: pos = cm.initial_position(graph) #if not given a position, set it to initial position

    random.seed(randomness)
    randomizer = random.random()

    moves = cm.find_moves(graph, pos, randomizer)
    qualities = [(0, "impossible")]

    for move, quality_matrix in moves:
        qual = quality_matrix[-1][-1]
        boost = 0

        potential_pos = cm.make_move(pos, move)
        path_segment_quality = rec_route_aware_fnm(graph, potential_pos, depth-1)

        if move[1] == 0: boost += 20

        qualities.append((qual + path_segment_quality + boost, move))


    #print(prp.swaps, "\t\t", prp.kinda_swaps)
    return max(qualities)[-1]

def rec_route_aware_fnm(graph, pos, depth): #return quality of best path
    if depth == 0: return 0 #if we're past the # of moves we want to check, don't add to quality

    randomizer = random.random()
    moves = cm.find_moves(graph, pos, randomizer)
    qualities = [-100]
    boost = 0

    for move, quality_matrix in moves:
        
        qual = quality_matrix[-1][-1]

        potential_pos = cm.make_move(pos, move)


        if pos[0][0] == pos[1][0] and pos[0][0] == graph["top"]: boost = 20
        if potential_pos[0][0] == potential_pos[1][0] and potential_pos[0][0] == graph["top"]: boost += 5*depth; depth = 1 #if topping out on this move, boost path for being shorter and don't look further
        
        #if boost != 0: print(boost, potential_pos, depth)

        path_segment_quality = rec_route_aware_fnm(graph, potential_pos, depth-1)
        qualities.append(boost + qual + path_segment_quality)
        #cm.all_qualities.append([graph["name"], qualities[-1]])

    return max(qualities)

def route_aware_find_route(graph, depth, pos = ()):
    if not pos: pos = cm.initial_position(graph)

    route = [pos]
    while not (pos[0][0] == pos[1][0] and pos[0][0] == graph["top"]):
        #print(move_num)
        move = route_aware_fnm(graph, depth, pos)
        route.append(move)
        # if type(pos[0]) != tuple:
        #     print()
        pos = cm.make_move(pos, move)
        #print(move)

    return route

graphs = prp.make_graphs("all_data_wc.csv")
#graph = graphs[0]

my_graph = [graph for graph in graphs if graph["name"] == ('BY-PR-V1', '12/31/25')]
graph = my_graph[0]

route = route_aware_find_route(graph, 5)
cm.describe_route(route)
cm.show_route(graph, route)

# with open("qualitydata.csv", mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerows(cm.all_qualities)