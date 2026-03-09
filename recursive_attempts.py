import core_methods as cm

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

def route_aware_fnm(num_moves):
    ini
    return ""

def rec_route_aware_fnm(num_moves): #return quality of best path
    return 0