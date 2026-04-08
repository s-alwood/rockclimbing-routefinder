import pandas as pd
import numpy as np
import image_processing
import math, statistics
import matplotlib.pyplot as plt
import random

U, R, D, L = "Up", "Right", "Down", "Left"
swaps = [0, 0, 0, 0, 0, 0, 0, 0, 0]
kinda_swaps = [0, 0, 0] #01, 12, 23


HEIGHT = 1.68 #meters

MAX_DIST = HEIGHT/2 #meters
MIN_STRENGTH = 6 # strength score (immediate return)
ABS_MIN_STRENGTH = 4.5 # strength score (won't ignore option)
flatness_threshold = math.pi/3 #radians; theta max value to be considered 2d movement MORE THAN just vertical

image_path = r"H:\My Drive\Alwood-SeniorResearch\Code\Images"
#unprocessed_image_path = r"H:\My Drive\Alwood-SeniorResearch\Code\Images\do_processing"

## BEFORE PROCESSING ##
def preprocess_images(folder_path): # to overlay grid before drawing enclosing rects
    image_processing.overlay_folder(folder_path)

## df HANDLING ##
def open_csvfile(name): #opens and does initial processing on raw data
    df = pd.read_csv(name)
    #print(df.head())
    #df.columns = df.iloc[0] # set headers to first row
    #df = df[1:] # drop row w/ headers
    df = df.drop('s1', axis=1) #remove intermed strength values
    df = df.drop('s2', axis=1)
    df = df.drop('s3', axis=1)
    df = df.drop('Strength', axis=1)

    df['x'] = np.nan
    df['y'] = np.nan
    #df['z'] = np.nan
    df['size_x'] = np.nan
    df['size_y'] = np.nan

    print(df.columns)
    
    return df

def groupby_climb(df): #groups climbs in the dataframe into a dict with keys (climb code, date)
    df = df.groupby(["Climb", "Date"])
    return df, list(df.groups.keys())   

## GENERAL PROCESSING ##
def process_data(image_folder_path): #overarching method. runs open_csvfile, groupby_climb, process_climbs
    data = open_csvfile("all_data.csv")

    grouped_data, climb_labels = groupby_climb(data)

    data, group_indices = process_climbs(data, grouped_data, climb_labels, image_folder_path)

    return data

def process_climbs(df, g_df, c_labels, foldername): #processes images and associates correct manually-taken data with coordinates. saves data as all_data_wc.csv
    print("\n","~"*10)
    print(f"processing climbs in {foldername}\n")
    
    imagedata = image_processing.process_images(foldername)

    climbs_imageprocessed = imagedata.keys()

    #climbs_imageprocessed = [((i_spl:=i.split("~"))[1], "/".join(i_spl[0].split("_"))) for i in climbs_imageprocessed]
    print(climbs_imageprocessed)

    climb_labels = set(c_labels)&set(climbs_imageprocessed)

    print("\tmissing image data for", set(c_labels)-climb_labels)
    print("\tmissing manual data for", set(climbs_imageprocessed)-climb_labels)

    climb_labels = list(climb_labels)

    print("\nlabels being processed: ",climb_labels)

    group_indices = g_df.indices

    for label in climb_labels:
        print(label)
        process_climb(df, list(group_indices[label]), imagedata[label])

    print(".\n.\n.\nSuccessfully processed.\n","~"*10)

    df.to_csv("all_data_wc.csv")

    return df, group_indices

def process_climb(df, climb_indices, blocks): #processes a single climb
    for i, block in enumerate(blocks):
        i = climb_indices[i]
        df.loc[i,"x"] = block["x"]
        df.loc[i,"y"] = block["y"]
        df.loc[i,"z"] = 0
        df.loc[i,"size_x"] = block["size_x"]
        df.loc[i,"size_y"] = block["size_y"]

    #print(df[climb_indices[0]:climb_indices[-1]+1]) #debug: print rows that should have been updated
    return df

## CALCULATIONS ##
def find_distance(hold_from, hold_to): #finds distance between two holds
        x_from = hold_from["x"]
        x_to = hold_to["x"]

        y_from = hold_from["y"]
        y_to = hold_to["y"]

        dx, dy = x_to-x_from, y_to-y_from

        return dx, dy, math.sqrt((dx**2)+(dy**2))

def find_strength(hold_to, theta, randomizer=12): #finds strength of a destination hold (region based on theta)
    def swap(prio, i1, i2):
        prio[i1], prio[i2] = prio[i2], prio[i1]
        return prio
    
    if 0 < theta < flatness_threshold: 
        prio = [U, R, D, L] # dx was pos, not obtuse enough to be up/down first
    elif 0 > theta > -flatness_threshold: 
        prio = [U, L, D, R] #dx was neg, not obtuse enough to be up/down first
    elif theta > 0: 
        prio = [U, D, R, L] #dx was pos, obtuse enough to be up/down first
    else: 
        prio = [U, D, L, R] #dx was neg, obtuse enough to be up/down first

    random.seed(randomizer)
    swap_counter = 0

    randomness_threshold = .05
    while (th:=random.random()) < randomness_threshold: #adding randomness to priority
        swap_counter += 1
        #print("random indecision", th)
        if th < 0.5 * randomness_threshold:
            swap(prio, 0, 1)
            kinda_swaps[0] += 1
            #print(0, 1)
        elif th < 0.75*randomness_threshold:
            swap(prio, 1, 2)
            kinda_swaps[1] += 1
            #print(1, 2)
        else: 
            swap(prio, 2, 3)
            kinda_swaps[2] += 1
            #print(2, 3)

        #randomness_threshold -= 0.01

    #print(kinda_swaps)
    #swaps[swap_counter] += 1
    #if swap_counter > 1: print(prio)

    strongest = ""
    strength = -1
    for direction in prio:
        dir_strength = hold_to["regions"][direction]
        if dir_strength > MIN_STRENGTH: #ADJUST LATER --> TEMPORARY HARD CUTOFF
            return direction, dir_strength
        if dir_strength > strength:
            strongest = direction
            strength = dir_strength

    return strongest, strength

## GRAPH CODE ##
def make_graphs(filename): #makes graphs for every climb
    graphs = []

    df = pd.read_csv(filename)

    grouped_data, climb_labels = groupby_climb(df)

    climb_indices = {(label, date): list(df.index[df["Climb"] == label]) for label, date in climb_labels}

    for label, date in climb_labels:
        graphs.append(create_graph(df, (label, date), climb_indices))

    return graphs

def create_graph(df, climb_label, climb_indices): #makes a graph for the climb with climb_label 
    graph = {
        "name" : climb_label,
        "start" : [],
        "top" : df.iloc[climb_indices[climb_label][-1]]["Hold #"], # assuming last hold is top for now
        "holds" : {} 
    }

    graph["holds"][0]= {"nbrs": []}

    for i in set(climb_indices[climb_label]):
        hold_from = df.iloc[i]
        graph["holds"][int(hold_from["Hold #"])] = { "regions":{ U:hold_from["Up Strength"], D:hold_from["Down Strength"], L:hold_from["Left Strength"], R:hold_from["Right Strength"] }, "coords": (hold_from["x"],hold_from["y"]), "size_x":hold_from["size_x"], "size_y":hold_from["size_y"], "nbrs":[] }
        if hold_from["Start?"] == True: graph["start"].append(hold_from["Hold #"])

        if hold_from["y"] < MAX_DIST*0.66: graph["holds"][0]["nbrs"].append((hold_from["y"], int(hold_from["Hold #"]), math.pi/2))

        other_holds = set(climb_indices[climb_label])-set([int(i)])

        for j in other_holds:
            hold_to = df.iloc[j]

            dx, dy, eucl_dist = find_distance(hold_from, hold_to)
            #print()
            #print("\t", dx, dy, eucl_dist)
            if dx == 0:
                if dy > 0: theta = math.pi
                else: theta = -math.pi
            else: theta = math.atan(dy/dx)
            if dy < -.1 or eucl_dist > MAX_DIST: continue
            if np.isnan(eucl_dist): print(f"{climb_label} nan distance value for {i}, {j}"); return {}
            #print(i, j, eucl_dist,"--> added nbr")

            graph["holds"][int(hold_from["Hold #"])]["nbrs"].append((eucl_dist, int(hold_to["Hold #"]), theta)) # add tuple containing distance, the index of hold_to, and theta to "nbrs" dictionary for hold_from (of index i)


    starts = graph["start"]
    x_feet = statistics.mean([graph["holds"][hold]["coords"][0] for hold in starts])
    
    graph["holds"][0]["coords"] = (x_feet, 0)

    return graph

def display_graph(graph): #uses matplotlib to display a graph 
    x_coords = []; y_coords = []; labels = []; connections = []
    for hold in graph["holds"]:
        x_coords.append(graph["holds"][hold]["coords"][0])
        y_coords.append(graph["holds"][hold]["coords"][1])
        r_text = str(hold)
        labels.append(r_text)

        for n in graph["holds"][hold]["nbrs"]:
            coords = graph["holds"][n[1]]["coords"]
            connections.append(([x_coords[-1],coords[0]], [y_coords[-1], coords[1]]))

    plt.figure(figsize=(4, 10)) #create the plot

    plt.scatter(x_coords, y_coords)
    for ln in connections:
        plt.plot(ln[0], ln[1], marker='x', linestyle='-', color='black') 

    # add labels to each point
    for i, label in enumerate(labels): #add labels to each point
        plt.annotate(label, (x_coords[i], y_coords[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.title(f"{graph["name"][0]} taken on {graph["name"][1]}")
    plt.grid(True)
    plt.show()

# graphs = make_graphs("all_data_wc.csv")
# display_graph(graphs[4])