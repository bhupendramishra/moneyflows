# python3 create_graph.py 100 10000 5

import networkx as nx
import random
import sys
import time
import names

num_node = int(sys.argv[1])
fc = open('customer.csv', "w")
fn = open('account.csv', "w")
fe = open('transaction.csv', "w")

Graph = nx.gnp_random_graph(num_node, 0.1, seed=0, directed=False)
print('Avg num of destination nodes:', Graph.number_of_edges() * 2 / Graph.number_of_nodes())

for node in range(num_node):
    fn.write(','.join([
        str(node), # Account ID
        str(node % (int(num_node * 0.8))) # Customer ID
        ]) + '\n')

for node in range(int(num_node * 0.8)):
    fc.write(','.join([
        str(node), # Account ID
        names.get_first_name(),
        names.get_last_name()
        ]) + '\n')

def random_date(proportion):
    format = '%Y-%m-%d %H:%M:%S'
    stime = time.mktime(time.strptime("2020-11-10 9:00:00", format))
    etime = time.mktime(time.strptime("2020-11-20 9:00:00", format))
    ptime = stime + proportion * (etime - stime)
    return time.strftime(format, time.localtime(ptime))

for node in range(num_node):
    neighbors = list(Graph.neighbors(node))
    random.seed(node)
    num_edge = random.choice([5,6,7,8,9,10])
    for edge in range(num_edge):
        node_src = node
        random.seed(edge)
        node_dst = random.choice(neighbors)
        fe.write(','.join([
            str(node_src),
            str(node_dst),
            'transfer_to',
            str(node_src) + '_' + str(edge), # txn_id
            random_date(random.random()),
            str(random.randrange(100, 1000, step=100)) # amount
            ]) + '\n')