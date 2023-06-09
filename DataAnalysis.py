import networkx as nx
import numpy as np
from igraph import Graph as IGraph

# 使用库,和自己实现的结果对比
def groundtruth(edges,teleport):
    # 创建有向图
    G = nx.DiGraph()
    # 在有向图G中添加边集合
    for edge in edges:
        G.add_edge(edge[0], edge[1])
    #有向图可视化
    # layout = nx.spring_layout(G)
    # nx.draw(G, pos=layout, with_labels=True)
    # plt.show()
    pr = nx.pagerank(G, alpha=teleport,tol=1e-06)
    # print("Result:", pr)
    with open("networkx.txt", "w") as outfile:
        for key,val in pr.items():
            outfile.write(str(key) + " " + str(val) + '\n')
    G = IGraph.TupleList(edges, directed=True, vertex_name_attr='name')
    pg = G.pagerank(implementation='power')
    pgvs = []
    for p in zip(G.vs, pg):
        pgvs.append({'name': p[0]['name'], 'pg': p[1]})
    pgvs = sorted(pgvs, key=lambda k: k['pg'], reverse=True)
    with open('igraph.txt', 'w') as outfile:
        for p in pgvs:
            outfile.write(p['name'] + " " + str(p['pg']) + '\n')

def analysis(edges):
    # 根据边获取节点的集合
    nodes = []
    in_degree = {} # 入度字典
    out_degree = {}
    for edge in edges:
        if edge[0] not in nodes:
            nodes.append(edge[0])
        if edge[1] not in nodes:
            nodes.append(edge[1])
        if edge[0] not in out_degree.keys():
            out_degree[edge[0]] = 1
        else :
            out_degree[edge[0]] += 1
        if edge[1] not in in_degree.keys():
            in_degree[edge[1]] = 1
        else :
            in_degree[edge[1]] += 1
    # 统计节点总数
    print("The number of nodes is {}".format(len(nodes)))
    # 统计deadpoint个数,deadpoint即出度为0的节点
    dead_points = []
    # 入度为0的节点
    source_points = []
    for node in nodes:
        if node not in out_degree.keys():
            dead_points.append(node)
        if node not in in_degree.keys():
            source_points.append(node)
    # 孤儿节点
    orphan_points = np.intersect1d(dead_points, source_points)
    print("The number of dead nodes is {}".format(len(dead_points)))
    print("The number of source nodes is {}".format(len(source_points)))
    print("The number of orphan nodes is {}".format(len(orphan_points)))
    with open("dead_points.txt","w") as outfile:
        for i in range (len(dead_points)):
            outfile.write(str(dead_points[i])+ '\n')
    with open("source_points.txt","w") as outfile:
        for i in range (len(source_points)):
            outfile.write(str(source_points[i])+ '\n')
    with open("orphan_points.txt","w") as outfile:
        for i in range (len(orphan_points)):
            outfile.write(str(orphan_points[i])+ '\n')

    # 统计入度最大的节点,出度最大的节点
    for key, value in in_degree.items():
        if (value == max(in_degree.values())):
            print("Node with max in degree is {}, in degree is {}".format(key, value))
    for key, value in out_degree.items():
        if (value == max(out_degree.values())):
            print("Node with max out degree is {}, out degree is {}".format(key, value))

    # 将节点按照入度大小排序,按出度大小排序
    I = dict(sorted(in_degree.items(), key=lambda item:item[1], reverse=True))
    O = dict(sorted(out_degree.items(), key=lambda item:item[1], reverse=True))
    with open('point_in_degree_sorted.txt', 'w') as f:
        for key, val in I.items():
            f.write(str(key) + " " + str(val) + '\n')
    with open('point_out_degree_sorted.txt', 'w') as f:
        for key, val in O.items():
            f.write(str(key) + " " + str(val) + '\n')



if __name__ == '__main__':
    f = open('Data.txt', 'r')
    edges = [line.strip('\n').split(' ') for line in f]
    teleport = 0.85
    groundtruth(edges, teleport)
    analysis(edges)



