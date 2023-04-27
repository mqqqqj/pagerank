from Basic import *
# from Block_Based import *

def SMatrix2dict(edges,nodes):
    N = len(nodes)
    print("The number of nodes is {}".format(N))
    M = {}
    for edge in edges:
        if edge[0] not in M.keys():
            M[edge[0]] = [edge[1]]
        else :
            M[edge[0]].append(edge[1])
    M = dict(sorted(M.items(),key=lambda item:item[0]))
    with open('Sparse_Matrix.txt', 'w') as f:
        for src, dest in M.items():
            f.write(str(src) + " ")
            for item in dest:
                f.write(str(item) + " ")
            f.write("\n")

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
    Alg = ['all_in_mem', 'basic', 'block_bu', 'block_su']
    ##四种算法
    ##1. All_in_mem 所有数据都在内存中,稀疏矩阵就以二维数组的形式存储.
    # r = All_in_mem(teleport, e, edges, nodes)
    ##2. basic 允许r_new在内存中, 稀疏矩阵(以字典形式存储)和r_old在磁盘上
    # encode sparse matrix
    # SMatrix2dict(edges, nodes)
    r = basic(teleport, e, N)
    ##3. Block_BU r_new也不允许在内存中
    # r = Block_BU(teleport, e, N, K)
    ##4. BLock_SU 把矩阵分成条带
    # r = Block_SU(teleport, e, N, K)
    with open(f'result_{Alg[1]}.txt',"w") as outfile:
        for i in range (len(r)):
            outfile.write(str(nodes[i]) + " " + str(r[i])+ '\n')
