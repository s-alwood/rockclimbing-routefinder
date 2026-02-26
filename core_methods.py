import preprocessing
import matplotlib.pyplot as plt

## main
def main(): #assumes data is already processed and saved in "all_data_wc.csv"
    graphs = preprocessing.make_graphs("all_data_wc.csv") # make graphs


    graph = graphs[0]
    
    route = find_route(graph)
    describe_route(route)
    show_route(graph, route)
    

    #alt_route = find_alternate_route(graph, (20, 21, 2, 6), [(3, 6, 7)])
    #describe_route(alt_route)
    #show_route(graph, alt_route)
    
    # for graph in graphs:
    #     #graph = graphs[4] # fetch graph
    #     go_up(graph)

## display
def display_position(graph, position, show_connections): # shows graph using plt with hand/foot positions. show_connections (T) = edges are shown

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


    ## position display

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
        odd = not odd
        

    plt.scatter(limb_x, limb_y, c="red", s = 30)


    ## title & show
    plt.title(f"{graph["name"][0]} taken on {graph["name"][1]} @ {position}")
    plt.grid(True)
    plt.show()
    return

## calculations / determinations
def initial_position(graph): #fetches initial position (both feet on floor, hands on start[s]); (lh, rh, lf, rf)
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

def find_distance(hold_from, hold_to): # returns euclidean distance
    if "coords" not in hold_from:
        c1 = (hold_to["coords"][0], 0)
    else: c1 = hold_from["coords"]
    c2 = hold_to["coords"]

    return ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)**(1/2)

## individual moves
def find_moves(graph, position): # returns 5 best moves found at given position
    moves = []

    weights = [0.7, 0.5, 0.8] #strong_weight, dist_weight, benefit and penalty weight
    max_base_quality = weights[0]*3 + weights[1]*((preprocessing.MAX_DIST)**0.5) # w/ height = 1.68, strong_weight + 0.84*dist_weight --> 1.42
    for limb, limb_pos in enumerate(position):
        for distance, hold_to, theta in graph["holds"][limb_pos]["nbrs"]:
            strongest, strength = preprocessing.find_strength(graph["holds"][hold_to], theta) # get chosen region

            distance = 0.75/(((distance-0.75)**6)+0.25) # transform (invert) distance
            strength = (strength)**(1/2) # transform strength

            tbd_pos = make_move(position, (limb, limb_pos, hold_to))
            if impossible(graph, tbd_pos): quality = -1; quality_matrix = [] #impossible, never consider
            else: quality, quality_matrix = find_move_quality(position, limb, limb_pos, hold_to, strength, distance, graph, weights) # if not impossible, find the quality
            
            considered = False
            if quality > 0.5 * max_base_quality: # if quality meets threshold
                moves.append((quality, distance, strength, (limb, limb_pos, hold_to), quality_matrix)) #add (quality, distance, (limb, hold_from, hold_to)) to moves
                considered = True
            #else: print(f"qual too low {quality}") # otherwise move too poor to consider

            print(limb_pos,"-->", hold_to, f"{considered}\t",quality_matrix) # print information about the move
            print()

    moves = sorted(moves, reverse=True)
    #print(moves[0])
    # sort moves #quality primary, distance secondary
    moves = [i[3:] for i in moves] # remove quality and distance from every hold in moves (only there to sort w/) 
    return moves[:5] # return 3 best moves

def make_move(position, move): # returns position updated with a given move

    limb, hold_from, hold_to = move #unpack move
    current_pos = position[limb] #get current pos of limb


    if current_pos != hold_from: #if move is not valid from position
        print(f"invalid move! says limb {limb} is at position {hold_from} but is actually at {current_pos}")
        exit(0)

    posn = (hold_to if idx == limb else elem for idx, elem in enumerate(position)) #update position

    return tuple(posn) #return updated position

# quality
def find_move_quality(position, limb, hold_from, hold_to, strength, distance, graph, weights): # returns quality and quality matrix of the move defined by (limb, hold_from, hold_to)

    quality_matrix = []
    ## base quality
    strong_weight, dist_weight, bp_weight = weights #strength goes from 1-10, distance goes to preprocessing.MAX_DIST (1/2 height); usually around 0.75-0.9 meters
    quality = strong_weight*strength + dist_weight*distance
    quality = round(quality, 2) # quality = some function of distance and strength, rounded to nearest 0.1
    quality_matrix.append(("base", quality)) # add base quality to quality_matrix

    ben_and_pens, quality_matrix = ben_and_pen(quality_matrix, position, limb, hold_from, hold_to, graph) # get rewards and penalties, update quality matrix as needed
    ben_and_pens *= bp_weight # weight rewards and penalties
    quality += ben_and_pens # apply rewards and penalties to quality


    quality_matrix.append(("final", quality))
    return quality, quality_matrix

def impossible(graph, position): # returns T if a move is impossible (feet less than 0.5m below next lowest hand OR any pair of limbs too far from one another)
    def feet_over_hands(graph, position):
        hands = position[:2]
        feet = position[-2:]

        ## check hand/foot pairings
        for hand in hands: #for each hand
            hand_y = graph["holds"][hand]["coords"][1] #get its y coordinate
            for foot in feet: #for each foot
                if foot == 0: continue #if it's on the floor, ignore
                foot_y = graph["holds"][foot]["coords"][1] #get its y coordinate
                if foot_y > hand_y-0.5: print(f"f>h {foot_y}, {hand_y}"); return True #if the foot is less than 0.5 meters below the hand, it's impossible
        
        return False #none were impossible
                

    def limbs_too_far(graph, position):
        hands = position[:2]
        feet = position[-2:]

        ## check hand/foot pairings
        for hand in hands: #for each hand
            hand = graph["holds"][hand] #get its attributes
            for foot in feet: #for each foot
                foot = graph["holds"][foot] #get its attributes
                eucl = find_distance(foot, hand) #find their distance
                if eucl > preprocessing.HEIGHT*1.25: print("h&f too far"); return True # if they're more than height * 1.3 apart, impossible

        ## check feet
        if feet[0] != feet[1] and feet[0] != 0 and feet[1] != 0:
            foot1 = graph["holds"][feet[0]]
            foot2 = graph["holds"][feet[1]]
            eucl = find_distance(foot1, foot2)
            if eucl > preprocessing.HEIGHT*0.75: print("f&f too far"); return True # if they're more than height * 0.66 apart, impossible

        ## check hands
        hand1 = graph["holds"][hands[0]]
        hand2 = graph["holds"][hands[1]]
        eucl = find_distance(hand1, hand2)
        if eucl > preprocessing.HEIGHT*0.7: print("h&h too far"); return True # if they're more than height * 0.75 apart, impossible

        return False #if none were impossible
    
    return feet_over_hands(graph, position) or limbs_too_far(graph, position) #if impossible in either of these ways

def ben_and_pen(quality_matrix, position, limb, hold_from, hold_to, graph): # applies rewards and penalties for certain attributes of the move
    quality = 0

    from_x, from_y = graph["holds"][hold_from]["coords"]
    to_x, to_y = graph["holds"][hold_to]["coords"]


    ## modifiers
    if hold_from == 0: quality += 20; quality_matrix.append(("off ground", 20)) #heavily incentivize taking foot off of ground
    if graph["top"] == hold_to: quality += 1; quality_matrix.append(("top", 1)) #incentivize grabbing top / topping out
    if hold_from != 0 and to_y < from_y: quality -= 2; quality_matrix.append(("down", -2)) #MODIFY THIS VALUE 
    if hold_to in position: quality -= 2/(10*(graph["holds"][hold_to]["size_x"])+1); quality_matrix.append(("match", -2/(10*(graph["holds"][hold_to]["size_x"])+1))) #max penalty 2 @ size = 0. avg penalty (based on data as of 2/6/26) ~ 1


    tbd_pos = make_move(position, (limb, hold_from, hold_to))
    #check if right limb is further right than left counterpart
    if limb % 2 == 0: # left 
        l_x, l_y = to_x, to_y
        r_x, r_y = graph["holds"][tbd_pos[limb+1]]["coords"]

    else: #right 
        r_x, r_y = to_x, to_y
        l_x, l_y = graph["holds"][tbd_pos[limb-1]]["coords"]

    if l_x > r_x: quality -= (l_x-r_x)*5; quality_matrix.append(("left more right than right", -(l_x-r_x)*5)) # subtract 10 * dx * dy from quality (more penalty if further apart)

    hand_x = (graph["holds"][tbd_pos[0]]["coords"][0] + graph["holds"][tbd_pos[1]]["coords"][0])/2
    foot_x = (graph["holds"][tbd_pos[2]]["coords"][0] + graph["holds"][tbd_pos[3]]["coords"][0])/2

    quality -= (1.5*abs(hand_x-foot_x))**2; quality_matrix.append(("unbalanced", 0.5*(abs(hand_x-foot_x)**2)))

    return quality, quality_matrix

# whole or partial routefinding
def go_up(graph): # navigates climb from start; displays at each step

    pos = initial_position(graph) # get initial position

    display_position(graph, pos, True) # show graph w/ start position and edges

    while not(pos[0] == pos[1] == graph["top"]): #while not topped out

        print(f"~~~")

        moves = find_moves(graph, pos) # find moves

        print("\n".join(str(i) for i in moves)) #moves returned (w/ quality matrices)

        move, quality_matrix = moves[0] #always pick best move
        print(interpret_move(move), quality_matrix) #print chosen move

        pos = make_move(pos, move) #update position

        display_position(graph, pos, False) #display updated w/o edges (for visibility)

def find_route(graph): # navigates climb from start; returns route of form [initial_pos, move1, move2...moveN]
    pos = initial_position(graph) # get initial position

    route = find_partial_route(graph, pos)

    return route

def find_partial_route(graph, pos): # navigates climb starting at a given position; returns route of form [initial_pos, move1, move2...moveN]
    route = [pos]
    fatigue = [0, 0, 0, 0]

    while not(pos[0] == pos[1] == graph["top"]): #while not topped out

        moves = find_moves(graph, pos) # find moves

        adjusted_moves = []
        last_move = route[-1]

        if len(last_move) == 3:
            last_limb = last_move[0]
            fatigue[last_limb] += 0.1

            for move, quality_matrix in moves: # move is form (limb, from, to)
                quality = quality_matrix[-1][-1]
                if move[0] == last_limb:
                    quality -= 1
                adjusted_moves.append((quality-fatigue[move[0]], move))
        else: 
            for move, quality_matrix in moves:
                quality = quality_matrix[-1][-1]
                adjusted_moves.append((quality-fatigue[move[0]], move))

        adjusted_moves.sort(reverse = True)

        quality, move = adjusted_moves[0] #always pick best move
        route.append(move)

        pos = make_move(pos, move) #update position

    #print(fatigue)
    return route

def find_alternate_route(graph, position, tried_moves): #UNFINISHED return route starting position having already tried some number of moves from position
    position = make_move(position, find_alternate_move(graph, position, tried_moves))

    route = find_partial_route(graph, position)
    return route

def find_alternate_move(graph, position, tried_moves): #UNFINISHED return next move having already tried some number of moves from position
    possible_moves = find_moves(graph, position)
    moves = [m for m, quality_matrix in possible_moves if not m in tried_moves]
    return moves[0]

## interpretability

def interpret_move(move): # returns a readable string describing move
    limb, hold_f, hold_t = move #unpack move
    limb = {0:"left hand", 1:"right hand", 2:"left foot", 3:"right foot"}[limb] #interpret limb

    if hold_f == 0: hold_f = "ground" #interpret hold going from
    else: hold_f = f"hold {hold_f}"

    return f"{limb} from {hold_f} to hold {hold_t}" #return string

def encode_move(move_str): #UNFINISHED takes a string of format "[limb] from [hold [#]/ground] to hold [#]" and turns it into (limb, hold_from, hold_to)
    words = move_str.split(" ")

    words = [w for w in words if w not in ["from", "hold", "to"]]

    #l_h = 0, r_h = 1, l_f = 2, r_f = 3
    limb_ls = words[:2]
    limb = 0
    if "foot" in limb_ls: limb += 2
    if "right" in limb_ls: limb += 1

    if "ground" in words: hold_from = 0
    else: hold_from = int(words[-2])

    hold_to = int(words[-1])
    return (limb, hold_from, hold_to)

def interpret_position(pos):
    return f"left hand @ hold {pos[0]} / right hand @ hold {pos[1]} / left foot {f"@ hold{pos[2]}" if pos[2] != 0 else "on ground"} / right foot {f"@ hold{pos[3]}" if pos[3] != 0 else "on ground"}"

def show_route(graph, route): #UNFINISHED display each step of a given route of form [initial_pos, move1, move2...moveN]
    
    pos = route[0]
    display_position(graph, pos, True)

    for move in route[1:]:
        pos = make_move(pos, move)
        display_position(graph, pos, False)
    return
    
def describe_route(route):

    print(f"starting: {interpret_position(route[0])}")
    pos = route[0]

    for i, move in enumerate(route[1:]):
        pos = make_move(pos, move)
        print(i, ":", interpret_move(move), f"  [ {pos} ]")
    print("top")


main()