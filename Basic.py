import numpy as np

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
    error = 1
    t = 0
    r_old = np.full(N,1/N,dtype=float).T # r_old.shape is [N,1]
    r_new = np.zeros(N).T
    # print(r_old.shape,r_new.shape)
    # r_new = teleport * M * r_old + [(1 - teleport)/ N]
    while error > e:
        r_new = teleport * M.dot(r_old)
        # Now re-insert the leaked PageRank
        r_new = r_new + (1 - sum(r_new[:])) / N
        # print(sum(r_new[:]))
        error = sum(np.absolute(r_new - r_old)[:])
        r_old = r_new.copy()
        t += 1
        print("Iteration {} , error is {}".format(t, error))
    return r_new

# 将稀疏矩阵以字典的形式存储的basic算法, 假设r_new足够保存在内存中
def basic(teleport, e, N):
    with open("r_old.txt", 'w') as f:
        for i in range(N):
            f.write(str(1 / N) + '\n')
    r_new = np.full(N, (1 - teleport) / N)  # r_new的初始化
    error = 1   #r_new和r_old的误差
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
                error += abs(r_new[i] - r_old_i)
        # 写回r_old
        with open('r_old.txt', 'w') as r_old:
            for r_new_i in r_new:
                r_old.write(str(r_new_i) + '\n')
        t += 1
        print("Iteration {} , error is {}".format(t, error))
    return r_new

