import numpy as np
from Block_Based import *
import time

# 最简单的做法,直接矩阵乘,认为所有的数据(r_new,matrix,r_old)都可保存在内存中
def All_in_mem(teleport, e, edges, nodes):
    N = len(nodes)
    M = np.zeros([N,N], dtype=float)
    for edge in edges:
        M[edge[1],edge[0]] = 1
    for i in range(N):
        degree_i = sum(M[:,i])
        if degree_i != 0:
            for j in range (N):
                M[j,i] /= degree_i
    start_time = time.time()
    error = 1
    t = 0
    r_old = np.full(N,1/N,dtype=float).T # r_old.shape is [N,1]
    r_new = np.zeros(N).T
    # print(r_old.shape,r_new.shape)
    # r_new = teleport * M * r_old + [(1 - teleport)/ N]
    while error > e:
        r_new = teleport * np.dot(M,r_old)+(1-teleport)/N
        # Now re-insert the leaked PageRank
        S = sum(r_new[:])
        r_new = r_new + (1 - S) / N
        # print(sum(r_new[:]))
        error = sum(np.absolute(r_new - r_old)[:])
        r_old = r_new.copy()
        t += 1
        print("Iteration {} , error is {}".format(t, error))
    end_time = time.time()
    print("====== Basic PageRank Algorithm ======")
    print("Total Iterations: "+str(t))
    print("Total running time: " + str(end_time - start_time) + "s")
    print("Number of reads during the process: "+str(0))
    print("Number of writes during the process: "+str(0))
    return r_new

# 将稀疏矩阵以字典的形式存储的basic算法, 假设r_new足够保存在内存中
def basic(teleport, e, N):
    start_time = time.time()
    read_count = 0
    write_count = 0
    with open("r_old.txt", 'w') as f:
        for i in range(N):
            f.write(str(1 / N) + '\n')
            write_count +=1
    r_new = np.full(N, (1 - teleport) / N)  # r_new的初始化
    error = 1   #r_new和r_old的误差
    error_list = []
    t = 0   # 迭代次数
    while error > e:
        r_new = np.full(N, (1 - teleport) / N)
        with open('r_old.txt', 'r') as r_old, open('Sparse_Matrix.txt', 'r') as SM:
            source = -1
            data = []
            for i in range(N):
                r_old_i = float(r_old.readline())
                while source < i:
                    data = SM.readline().replace('\r', '').replace('\n', '')
                    read_count +=1
                    data = data.split() # 用空格分开,返回一个列表
                    source = int(data[0])
                    degree = int(data[1])
                    dests = data[2:]
                if source == i:  # 判断是否找到
                    for dest in dests:
                        r_new[int(dest)] += teleport * r_old_i / degree
        # print(sum(r_new))
        r_new = r_new + (1 - sum(r_new)) /N
        # 计算error
        error = 0
        with open('r_old.txt', 'r') as r_old:
            for i in range(N):
                r_old_i = float(r_old.readline())
                read_count +=1
                error += abs(r_new[i] - r_old_i)
        # 写回r_old
        with open('r_old.txt', 'w') as r_old:
            for r_new_i in r_new:
                r_old.write(str(r_new_i) + '\n')
                write_count += 1
        t += 1
        error_list.append(error)
        print("Iteration {} , error is {}".format(t, error))
    end_time = time.time()
    print("== Basic PageRank algorithm with sparse matrix ==")
    print("Total Iterations: " + str(t))
    print("Total running time: " + str(end_time - start_time) + "s")
    print("Number of reads during the process: "+str(read_count))
    print("Number of writes during the process: "+str(write_count))
    draw_error_curve(error_list, 'basic')
    return r_new

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
    N = len(nodes)
    Alg = ['all_in_mem', 'basic']
    #1. All_in_mem 所有数据都在内存中,稀疏矩阵就以二维数组的形式存储.
    r = All_in_mem(teleport, e, edges, nodes)
    with open(f'result_{Alg[0]}.txt',"w") as outfile:
        for i in range (len(r)):
            outfile.write(str(nodes[i]) + " " + str(r[i])+ '\n')
    Top100("result_all_in_mem")
    ##2. basic 允许r_new在内存中, 稀疏矩阵(以字典形式存储)和r_old在磁盘上
    # encode sparse matrix
    SMatrix2dict(edges, nodes)
    r = basic(teleport, e, N)
    with open(f'result_{Alg[1]}.txt',"w") as outfile:
        for i in range (len(r)):
            outfile.write(str(nodes[i]) + " " + str(r[i])+ '\n')

    Top100("result_basic")