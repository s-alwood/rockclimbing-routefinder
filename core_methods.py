import preprocessing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main(): #assumes data is already processed and all processed data is saved in "all_data_wc.csv"
    graphs = preprocessing.make_graphs("all_data_wc.csv")

    graph = graphs[3]

    pos = initial_position(graph)

    display_position(graph, pos, True)

    for i in range(50):

        moves = find_next_move(graph, pos)

        print(f"~~~ {i}")
        print("\n".join(str(i) for i in moves))
        move, quality_matrix = moves[0]
        print(move, quality_matrix)

        pos = make_next_move(pos, move)

        display_position(graph, pos, False)

    print()

    #preprocessing.display_graph(graphs[0])
    

def initial_position(graph):
    starts = graph["start"]
    l_f = 0; r_f = 0 #floor indicator

    if len(starts) == 1: #if only one starting hold
        l_h = int(starts[0]); r_h = int(starts[0]) #both hands go on that one

    elif len(starts) == 2: #if two starting holds
        hold_0 = (graph["holds"][starts[0]]["coords"], starts[0]) #extract tuple of form ((x, y), hold#)
        hold_1 = (graph["holds"][starts[1]]["coords"], starts[1]) #for both starts

        starts = sorted([hold_0, hold_1]) #sort the holds (ascending) (will go by x coord w/ y coord tiebreaker)
        l_h = int(starts[0][-1]); r_h = int(starts[1][-1]) #set left hand on leftmost, right heand on rightmost

    else: #not 1 nor 2 start holds --> impossible
        print(f"starts improper length {len(starts)}")

    return (l_h, r_h, l_f, r_f) #(Left Hand, Right Hand, Left Foot, Right Foot) hold #'s

def display_position(graph, position, show_connections):

    ## climb display
    x_coords = []; y_coords = []; labels = []; connections = []
    for hold in graph["holds"]:
        if hold == 0: continue
        x_coords.append(graph["holds"][hold]["coords"][0])
        y_coords.append(graph["holds"][hold]["coords"][1])
        r_text = str(hold)
        labels.append(r_text)

        if show_connections:
            for n in graph["holds"][hold]["nbrs"]:
                coords = graph["holds"][n[1]]["coords"]
                connections.append(([x_coords[-1],coords[0]], [y_coords[-1], coords[1]]))

    plt.figure(figsize=(4, 10)) #create the plot

    for ln in connections:
        plt.plot(ln[0], ln[1], marker='', linestyle='-', c = "black") 

    for i, label in enumerate(labels): #add labels to each point
        plt.annotate(label, (x_coords[i], y_coords[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.scatter(x_coords, y_coords, s = 50)        


    ## position displaY

    limb_x, limb_y = [], []
    labels = ["lh", "rh", "lf", "rf"]

    counter = 1
    for p in position:
        if p != 0:
            hold = graph["holds"][p]["coords"]
            limb_x.append(hold[0]); limb_y.append(hold[1])
        else:
            limb_x.append(limb_x[0]+0.33*counter*(limb_x[1]-limb_x[0])); limb_y.append(0)
            counter += 1


    odd = False
    for i, label in enumerate(labels): #add labels to each point
        plt.annotate(label, (limb_x[i], limb_y[i]), textcoords="offset points", xytext=(-10+20*odd, 0), ha='center', c="red")
        #print(-10+int(20*odd), odd)
        odd = not odd
        

    plt.scatter(limb_x, limb_y, c="red", s = 30)


    ## title & show
    plt.title(f"{graph["name"][0]} taken on {graph["name"][1]} @ {position}")
    plt.grid(True)
    plt.show()
    return

def find_next_move(graph, position):
    moves = []

    weights = [0.7, 0.5] #strong_weight, dist_weight
    max_quality = weights[0] + weights[1]*((10*preprocessing.MAX_DIST)**0.5) # w/ height = 1.68, strong_weight + 0.84*dist_weight --> 1.42
    for limb, limb_pos in enumerate(position):
        for distance, hold_to, theta in graph["holds"][limb_pos]["nbrs"]:
            print("\t", limb_pos,"-->", hold_to)

            strongest, strength = preprocessing.find_strength(graph["holds"][hold_to], theta)

            distance = 0.5/((distance-0.5)**4+0.25)
            strength = (strength)**(1/2)

            tbd_pos = make_next_move(position, (limb, limb_pos, hold_to))
            if impossible(graph, tbd_pos): quality = -1; quality_matrix = [] #impossible
            else: quality, quality_matrix = find_move_quality(position, limb, limb_pos, hold_to, strength, distance, graph, weights)
            
            
            #theoretically: min(quality) = 0, max(quality) = strong_weight + dist_wight*MAX_DIST
            if quality > 0.25 * max_quality: # if quality meets threshold
                moves.append((quality, distance, strength, (limb, limb_pos, hold_to), quality_matrix)) #add (quality, distance, (limb, hold_from, hold_to)) to moves 
                #print((limb, limb_pos, hold_to), quality_matrix)
            else: print(f"qual too low {quality}")
            print("\t", quality_matrix)
            print()

    moves = sorted(moves, reverse=True)
    #print(moves[0])
    # sort moves #quality primary, distance secondary
    moves = [i[3:] for i in moves] # remove quality and distance from every hold in moves (only there to sort w/) 
    return moves[:3] # return 5 best moves

def impossible(graph, position):
    def feet_over_hands(graph, position):
        hands = position[:2]
        feet = position[-2:]

        print(hands, feet)

        for hand in hands:
            hand_y = graph["holds"][hand]["coords"][1]
            for foot in feet:
                if foot == 0: continue
                foot_y = graph["holds"][foot]["coords"][1]
                if foot_y > hand_y-0.66: print(f"f>h {foot_y}, {hand_y}"); return True
        
        return False
                

    def limbs_too_far(graph, position):
        hands = position[:2]
        feet = position[-2:]

        for hand in hands:
            hand = graph["holds"][hand]
            for foot in feet:
                foot = graph["holds"][foot]
                eucl = find_distance(foot, hand)
                if eucl > preprocessing.HEIGHT + 0.5: print("h&f too far"); return True

        if feet[0] != feet[1] and feet[0] != 0 and feet[1] != 0:
            foot1 = graph["holds"][feet[0]]
            foot2 = graph["holds"][feet[1]]
            eucl = find_distance(foot1, foot2)
            if eucl > preprocessing.HEIGHT/2: print("f&f too far"); return True

        hand1 = graph["holds"][hands[0]]
        hand2 = graph["holds"][hands[1]]
        eucl = find_distance(hand1, hand2)
        if eucl > preprocessing.HEIGHT*(3/4): print("h&h too far"); return True

        return False
    return limbs_too_far(graph, position) or feet_over_hands(graph, position)



def find_distance(hold_from, hold_to):
    if "coords" not in hold_from:
        c1 = (hold_to["coords"][0], 0)
    else: c1 = hold_from["coords"]
    c2 = hold_to["coords"]

    return ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)**(1/2)

def find_move_quality(position, limb, hold_from, hold_to, strength, distance, graph, weights):

    quality_matrix = []
    ## base quality
    strong_weight, dist_weight = weights #strength goes from 1-10, distance goes to preprocessing.MAX_DIST (1/2 height); usually around 0.75-0.9 meters
    quality = strong_weight*strength + dist_weight*distance
    quality = round(quality, 2) # quality = some function of distance and strength, rounded to nearest 0.1
    quality_matrix.append(("base", quality))

    if hold_from == 0: from_x, from_y = 0.5, 0
    else: from_x, from_y = graph["holds"][hold_from]["coords"]
    to_x, to_y = graph["holds"][hold_to]["coords"]


    ## modifiers
    if hold_from == 0: quality += 10; quality_matrix.append(("off ground", 10)) #heavily incentivize taking foot off of ground
    if graph["top"] == hold_to: quality += 1; quality_matrix.append(("top", 1)) #incentivize grabbing top / topping out
    if hold_from != 0 and to_y < from_y: quality -= 2; quality_matrix.append(("down", -2))
    if hold_to in position: quality -= 2/(10*(graph["holds"][hold_to]["size_x"])+1); quality_matrix.append(("match", -2/(10*(graph["holds"][hold_to]["size_x"])+1)))


    if limb % 2 and to_x < from_x: quality += (to_x-from_x); quality_matrix.append(("r going l", float(to_x-from_x))) #if left limb and hold is to the left
    elif not limb % 2 and to_x > from_x: quality += (from_x-to_x); quality_matrix.append(("l going r", float(from_x-to_x))) # if right limb and hold is to the right


    quality_matrix.append(("final", quality))
    return quality, quality_matrix


def make_next_move(position, move): 
    limb, hold_from, hold_to = move
    current_pos = position[limb]
    if current_pos != hold_from:
        print(f"invalid move! says limb {limb} is at position {hold_from} but is actually at {current_pos}")

    posn = (hold_to if idx == limb else elem for idx, elem in enumerate(position))

    return tuple(posn)

def find_route(graph):
    position = initial_position(graph)
    

main()