import preprocessing as prp
import recursive_attempts as rec
import core_methods as cm

prp.preprocess_images(r"H:\My Drive\Alwood-SeniorResearch\Code\testing_images") # add 3 climbs to test here

graphs = prp.make_graphs("H:\My Drive\Alwood-SeniorResearch\Code\testing_data_one.csv") # data for climbs used to test
first = True


for graph in graphs:

    simple_route = cm.find_route(graph) #do simple for first climb
    cm.describe_route(simple_route) # display route
    if first:
        cm.show_route(graph, route) # show route
        first = False

    route = rec.route_aware_find_route(graph, 5) # get route
    cm.describe_route(route) # display route
    cm.show_route(graph, route) # show route



# REMEMBER:
# record climber beta
# record suggested route
# get gif for suggested route