import core_methods as cm
import preprocessing as prp


## attempt 1

level_iters = [0 for i in range(25)]
def explore_routes(graph):
    pos = cm.initial_position(graph)
    routes = recursive_explore(graph, pos, 0, False)
    print(routes)
    
def recursive_explore(graph, pos, level, stop):
    if pos[0] == pos[1] and pos [0] == graph["top"]: return "top"
    if stop: return []
    moves = [m[0] for m in cm.find_moves(graph, pos)[:2]]
    routes = []
    for move in moves:
        #print(move)
        p_pos = cm.make_move(pos, move)
        r = recursive_explore(graph, p_pos, level + 1, stop)
        if not r: continue
        if r == "top": return [move, r]
        if "top" in r: stop = True
        #print([move]+[i for i in (r[0] if len(r) == 1 else r)])
        routes.append([move]+[i for i in (r[0] if len(r) == 1 else r)])
    level_iters[level] += 1; print(level_iters)
    return min_len_items(routes)

def min_len_items(ls):
    if not ls: return ls
    shortest, ln = ls[0], len(ls[0])

    short = []
    for i in ls:
        if not i: continue
        if (l:=len(i)) < ln:
            shortest = i; ln = l
            short = [i]

        if l == ln: short.append(i)
    return short


## attempt 2

def route_aware_fnm(graph, num_moves, pos=()):
    if not pos: pos = cm.initial_position(graph) #if not given a position, set it to initial position

    moves = cm.find_moves(graph, pos)
    qualities = []

    for move, quality_matrix in moves:
        qual = quality_matrix[-1][-1]

        potential_pos = cm.make_move(pos, move)
        qualities.append((qual +rec_route_aware_fnm(graph, potential_pos, num_moves-1), move))

    print(qualities)
    return max(qualities)[-1]

def rec_route_aware_fnm(graph, pos, num_moves): #return quality of best path
    if num_moves == 0: return 0 #if we're past the # of moves we want to check, don't add to quality

    moves = cm.find_moves(graph, pos)
    qualities = [-100]
    level_iters[num_moves] += 1; print(level_iters)
    for move, quality_matrix in moves:
        qual = quality_matrix[-1][-1]

        potential_pos = cm.make_move(pos, move)
        qualities.append(qual +rec_route_aware_fnm(graph, potential_pos, num_moves-1))

    return max(qualities)


graphs = prp.make_graphs("all_data_wc.csv")
graph = graphs[4]

print(route_aware_fnm(graph, 10))