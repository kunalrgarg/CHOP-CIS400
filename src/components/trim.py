
import json

def shortify(name):
    return name[:25] + '...' if len(name) > 28 else name
        

fp_r = open('2019MeshTreeOriginal.json', 'r')
fp_w = open('2019MeshTree.json', 'w')

tree = json.load(fp_r)
tree_new = {'name': shortify(tree['name'])}
tree_depth = 5

curr, nxt = [], [(tree, tree_new)]

for i in range(tree_depth):
    curr, nxt = nxt, []
    for (old_node, new_node) in curr:
        if 'children' in old_node and i != tree_depth - 1:
            new_node['children'] = []
            children = old_node['children']
            children = sorted([c for c in children], key=lambda x: len(x['name']))
            for old_child_node in children[:30]:
                new_child_node = {'name': shortify(old_child_node['name'])}
                nxt.append((old_child_node, new_child_node))
                new_node['children'].append(new_child_node)
        else:
            new_node['value'] = 1


json.dump(tree_new, fp_w)

# import ipdb; ipdb.set_trace()

