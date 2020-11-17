# python3 create_graph.py 100 10000 5

import networkx as nx
import random
import sys

num_node = int(sys.argv[1])
#fg = open('graph.pg', "w")
fn = open('node.csv', "w")
fe = open('edge.csv', "w")

Graph = nx.gnp_random_graph(num_node, 0.1, directed=False)
print('Avg num of destination nodes:', Graph.number_of_edges() * 2 / Graph.number_of_nodes())

labels = ['House', 'School', 'Restaurant', 'Cafe', 'Hospital', 'Station', 'Supermarket']
for node in range(num_node):
    label = labels[node % len(labels)]
    #fg.write(str(id_node) + '\t:' + label + '\n')
    fn.write(str(node) + ',' + label + '\n')

for node in range(num_node):
    neighbors = list(Graph.neighbors(node))
    random.seed(node)
    num_edge = random.choice([5,6,7,8,9,10])
    for edge in range(num_edge):
        node_src = node
        random.seed(edge)
        node = random.choice(neighbors)
        #fg.write('\t'.join([str(node_old), '->', str(node), ':transfer_to', 'txn_id:' + str(id_node) + '_' + str(id_edge)]) + '\n')
        fe.write(','.join([str(node_src), str(node), 'transfer_to', str(node_src) + '_' + str(edge)]) + '\n')
