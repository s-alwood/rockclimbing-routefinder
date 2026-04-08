import preprocessing as prp
import recursive_attempts as rec
import core_methods as cm

prp.preprocess_images(r"H:\My Drive\Alwood-SeniorResearch\Code\testing_images") # add climbs to test here


file = r"H:\My Drive\Alwood-SeniorResearch\Code\testing_data_one.csv" #your file path goes here
graphs = prp.make_graphs(file) # data for climbs used to test
first = True


for graph in graphs:

    simple_route = cm.find_route(graph) #do simple for first climb
    cm.describe_route(simple_route) # display route
    if first:
        cm.show_route(graph, route) # show route
        first = False

    route = rec.route_aware_find_route(graph, 5) # get route
    cm.describe_route(route) # output text form of route
    cm.show_route(graph, route) # show route (pops up mpl with moves, close window for next move.)



# REMEMBER:
# record climber beta
# record suggested route
# get gif for suggested route