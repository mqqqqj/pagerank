from Basic import *
from Block_Based import *



if __name__ == '__main__':
    # 读入有向图，存储边
    f = open('Data.txt', 'r')
    edges = [line.strip('\n').split(' ') for line in f]
    # 根据边获取节点的集合
    nodes = []
    for edge in edges:
        if edge[0] not in nodes:
            nodes.append(edge[0])
        if edge[1] not in nodes:
            nodes.append(edge[1])
    # 便于后续用矩阵处理，将节结点编号为从 0 到 N - 1
    node2num = {} #dict
    i = 0
    for node in nodes:
        node2num[node] = i
        i += 1
    for edge in edges:
        edge[0] = node2num[edge[0]]
        edge[1] = node2num[edge[1]]

    e = 1e-06
    teleport = 0.85
    K = 10
    N = len(nodes)
    Alg = ['all_in_mem', 'basic']
    ##四种算法
    ##1. All_in_mem 所有数据都在内存中,稀疏矩阵就以二维数组的形式存储.
    # r = All_in_mem(teleport, e, edges, nodes)
    ##2. basic 允许r_new在内存中, 稀疏矩阵(以字典形式存储)和r_old在磁盘上
    # encode sparse matrix
    # SMatrix2dict(edges, nodes)
    # r = basic(teleport, e, N)
    # with open(f'result_{Alg[1]}.txt',"w") as outfile:
    #     for i in range (len(r)):
    #         outfile.write(str(nodes[i]) + " " + str(r[i])+ '\n')
    ##3. Block_BU r_new也不允许在内存中
    # Block_BU(teleport, e, nodes, K)
    ##4. BLock_SU 把矩阵分成条带
    split_length = split_matrix(N, K)
    # print(split_length)
    Block_SU(teleport, e, nodes, K, split_length)

