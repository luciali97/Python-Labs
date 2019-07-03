# NO IMPORTS ALLOWED!

import json

def did_x_and_y_act_together(data, actor_id_1, actor_id_2):
    for a1, a2, film in data:
        if (a1 == actor_id_1 and a2 == actor_id_2) or (a1 == actor_id_2 and a2 == actor_id_1):
            return True
    return False

def get_actors_with_bacon_number(data, n):
    
    # return the set of actor id's who have worked with a given actor id 
    act_together = {}
    
    # return the bacon number of a given actor id; -1 if he/she doesn't have a bacon number
    bnum_by_id = {}
    
    # create act_together and initialize bnum_by_id to -1
    for a1, a2, film in data:
        if a1 != a2:
            if a1 not in act_together.keys():
                act_together.update({a1: set()})
                bnum_by_id.update({a1:-1})               
            act_together[a1].update({a2})
            if a2 not in act_together.keys():
                act_together.update({a2: set()})
                bnum_by_id.update({a2:-1})               
            act_together[a2].update({a1})       
    bnum_by_id[4724] = 0 
    
    # return the list of actor id's with a given bacon number n 
    bnum_by_n = [{4724}]
    
    for i in range(1, n+1):
        bnum_i = set()
        prev = bnum_by_n[i-1]
        if len(prev) == 0:
            return set()
        for a1 in prev:
            for a2 in act_together[a1]:
                if bnum_by_id[a2] == -1:
                    bnum_by_id[a2] = i
                    bnum_i.update({a2})
        bnum_by_n.append(bnum_i)            
    return bnum_by_n[n]

def get_bacon_path(data, actor_id):
    return get_path(data,4724,actor_id)

def get_path(data, actor_id_1, actor_id_2):
    if actor_id_1 == actor_id_2:
        return [actor_id_1]
    # construct a graph (represented as adjacency lists) where each edge represents a movie that connects two actors
    g = {}
    for a1, a2, film in data:
        # we don't include self-loops
        if a1 != a2:
            if a1 in g:
                g[a1].add(a2)
            else:
                g[a1] = set([a2])
            if a2 in g:
                g[a2].add(a1)
            else:
                g[a2] = set([a1])
   
    # if it's not in the database, then return None
    if actor_id_2 not in g.keys():
        return None
    
    visited = set([actor_id_1])
    q = [[actor_id_1]]
    i = 0
    
    while i < len(q):
        bacon_path = q[i]
        a = bacon_path[-1]
        # if the last actor in this path is who we're looking for, then return
        if a == actor_id_2:
            return bacon_path
        # for all actors who have acted with the last actor in bacon_path
        for nghb in g[a]:
            # if this is the first time that he/she is visited, then add him/her to bacon_path, add this new path to q, and mark him/her as visited
            if nghb not in visited:
                init_path = bacon_path[:]
                init_path.append(nghb)
                q.append(init_path)
                if nghb == actor_id_2:
                    return init_path
                visited.add(nghb)
        i += 1
    return None

def get_movie_path(data, actor_id_1, actor_id_2):
    # return the set of tuples (actor id, film) of people who have worked with a given actor id 
    act_together = {}   
    # return the bacon number of a given actor id; initialized to -1
    bnum_by_id = {}   
    # if visited, then visited[actor_id] = True
    visited = {}    
    # return the movie path as a list for a given actor_id
    movie_path = {}
    
    # compute act_together and initialize bnum_by_id to -1, visited to False, and bacon_path to []
    for a1, a2, film in data:
        if a1 != a2:
            if a1 not in act_together.keys():
                act_together.update({a1: set()})
                bnum_by_id.update({a1:-1})
                visited.update({a1:False})
                movie_path.update({a1:[]})
            act_together[a1].update({(a2,film)})
            if a2 not in act_together.keys():
                act_together.update({a2: set()})
                bnum_by_id.update({a2:-1})
                visited.update({a2:False})
                movie_path.update({a2:[]})
            act_together[a2].update({(a1,film)})  
    if actor_id_1 not in act_together or actor_id_2 not in act_together:
        return None
    bnum_by_id[actor_id_1] = 0    
    bnum_by_n = [{actor_id_1}]
    
    completed = False
    i = 1
    while not completed:
        bnum_i = set()
        prev = bnum_by_n[i-1]
        completed = True
        # for all actors with bnum = i-1
        for a1 in prev:
            # prev_path is the list of films that get to a1
            prev_path = movie_path[a1]
            for a2,film in act_together[a1]:
                if not visited[a2]:
                    completed = False
                if bnum_by_id[a2] == -1:
                    new_path = movie_path[a2]+prev_path+[film]
                    movie_path[a2] = new_path
                    bnum_by_id[a2] = i
                    bnum_i.update({a2})
            visited[a1] = True
        bnum_by_n.append(bnum_i)
        i += 1
   
      # if the actor is not reachable from Bacon, return None
    if len(movie_path[actor_id_2]) == 0:
        return None
    return movie_path[actor_id_2]

def ids_to_names(data, ids):
    # data are keyed by names 
    
    # id_to_name is keyed by ids
    id_to_name = {}
    for name, i in data.items():
        id_to_name.update({i:name})
    names = []
    for i in ids:
        names.append(id_to_name[i])
    return names

if __name__ == '__main__':

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
