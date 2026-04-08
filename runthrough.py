import preprocessing as prp
import recursive_attempts as rec
import core_methods as cm


file = r"H:\My Drive\Alwood-SeniorResearch\Code\all_data_wc.csv" #your file path goes here
graphs = prp.make_graphs(file) # data for climbs used to test
first = True


for graph in graphs:
    route = rec.route_aware_find_route(graph, 5) # get route
    cm.describe_route(route) # output text form of route
    cm.show_route(graph, route) # show route (pops up mpl with moves, close window for next move.)
