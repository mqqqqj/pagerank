import math

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
            f.write(str(src) + " "+ str(len(dest)) +" ")
            for item in dest:
                f.write(str(item) + " ")
            f.write("\n")

def split_matrix(N, K):
    from collections import defaultdict
    block_size = math.ceil(N / K)
    print("block_size is {}".format(block_size))
    blocks = []
    for i in range(K):
        blocks.append(defaultdict(lambda: []))
    with open('Sparse_Matrix.txt', 'r') as M:
        for line in M:
            line = line.split()
            src = line[0]
            dests = line[2:]
            for dest in dests:
                dest = int(dest)
                if len(blocks[math.floor(dest / block_size)][src]) == 0:
                    blocks[math.floor(dest / block_size)][src].append(line[1])
                blocks[math.floor(dest / block_size)][src].append(dest)
    split_length = []
    for i, block in enumerate(blocks):
        # print(len(block))
        split_length.append(len(block))
        with open(f'striped_matrix/striped_matrix_{K}_{i}.txt', 'w') as f:
            for src, dests in block.items():
                f.write(str(src) + " " )
                for item in dests:
                    f.write(str(item) + " ")
                f.write("\n")
    return split_length



# block base alg, all on disk
# 问题出在,计算error之前r_new就需要通过计算出delta来正则化,而要计算出delta需要遍历完一整个r_new才计算的出来,
# 这在分块算法中是做不到的用本轮的delta正则化本轮的r_new,解决方法是将这一轮的delta留给下一轮计算
def Block_BU(teleport, e, nodes, K):
    N = len(nodes)
    with open("r_old.txt", 'w') as f:
        for i in range(N):
            f.write(str(1 / N) + '\n')
    error = 1
    t = 0
    delta_new = 0
    while error > e:
        r_new_begin = 0
        error = 0
        delta_old = delta_new
        delta_new = 0
        with open('r_new.txt', 'w') as r_new:
            r_new.truncate()
        for i in range(K):
            r_new_end = min(N, r_new_begin + math.ceil(N/K))
            # print(r_new_begin, r_new_end)
            r_new_block = {}
            for j in range(r_new_begin, r_new_end):
                r_new_block[j] = (1 - teleport) / N
            # 计算[r_new_begin,r_new_end)范围内的r_new
            with open('r_old.txt', 'r') as r_old, open('Sparse_Matrix.txt', 'r') as SM:
                source = -1
                data = []
                for n in range(N):
                    r_old_i = float(r_old.readline())
                    while source < n:
                        data = SM.readline().replace('\r', '').replace('\n', '')
                        data = data.split()  # 用空格分开,返回一个列表
                        source = int(data[0])
                        degree = int(data[1])
                        dests = data[2:]
                    if source == n:  # 判断是否找到
                        for dest in dests:
                            if r_new_end > int(dest) >= r_new_begin:
                                r_new_block[int(dest)] += teleport * r_old_i / degree
            # 为了正则化使用
            delta_new += sum(r_new_block.values())
            # 计算误差
            with open('r_old.txt', 'r') as r_old:
                for j in range(r_new_begin):
                    r_old.readline()
                for j in range(r_new_begin, r_new_end):
                    r_old_i = float(r_old.readline())
                    error += abs((r_new_block[j] + (1 - delta_old) / N) - r_old_i)
            with open('r_new.txt', 'a') as r_new:
                for _, val in r_new_block.items():
                    r_new.write(str(val) + '\n')
            r_new_begin = r_new_end
        # 写回r_old
        # print(delta_new)
        with open('r_old.txt', 'w') as r_old, open('r_new.txt', 'r') as r_new:
            for i in range(N):
                r_old_i = (1 - delta_new) / N + float(r_new.readline())
                r_old.write(str(r_old_i) + '\n')
        t += 1
        print("Iteration {} , error is {}".format(t, error))
    with open('result_block_bu.txt', 'w') as r_result, open('r_old.txt', 'r') as r_old:
        for i in range(N):
            r_result.write(str(nodes[i]) + " " + r_old.readline())

# block stride update alg
def Block_SU(teleport, e, nodes, K, split_length):
    N = len(nodes)
    with open("r_old.txt", 'w') as f:
        for i in range(N):
            f.write(str(1 / N) + '\n')
    error = 1
    t = 0
    delta_new = 0
    while error > e:
        r_new_begin = 0
        error = 0
        delta_old = delta_new
        delta_new = 0
        with open('r_new.txt', 'w') as r_new:
            r_new.truncate()
        for i in range(K):
            r_new_end = min(N, r_new_begin + math.ceil(N/K))
            # print(r_new_begin, r_new_end)
            r_new_block = {}
            for j in range(r_new_begin, r_new_end):
                r_new_block[j] = (1 - teleport) / N
            # 计算[r_new_begin,r_new_end)范围内的r_new
            with open('r_old.txt', 'r') as r_old, open(f'striped_matrix/striped_matrix_{K}_{i}.txt', 'r') as SM:
                source = -1
                data = []
                isend = 0
                for n in range(N):  # 遍历r_old
                    r_old_i = float(r_old.readline())
                    if isend == split_length[i]:
                        # (lambda x, y: x - 1 if i != (K - 1) else y - 1, math.ceil(N / K), N - K * math.ceil(N / K))
                        break
                    while source < n:
                        data = SM.readline().replace('\r', '').replace('\n', '')
                        data = data.split()  # 用空格分开,返回一个列表
                        # print(n, source, data, i)
                        source = int(data[0])
                        degree = int(data[1])
                        dests = data[2:]
                        isend += 1
                        # print(isend)
                    if source == n:  # 判断是否找到
                        for dest in dests:
                            r_new_block[int(dest)] += teleport * r_old_i / degree
            # 为了正则化使用
            delta_new += sum(r_new_block.values())
            # 计算误差
            with open('r_old.txt', 'r') as r_old:
                for j in range(r_new_begin):
                    r_old.readline()
                for j in range(r_new_begin, r_new_end):
                    r_old_i = float(r_old.readline())
                    error += abs((r_new_block[j] + (1 - delta_old) / N) - r_old_i)
            with open('r_new.txt', 'a') as r_new:
                for _, val in r_new_block.items():
                    r_new.write(str(val) + '\n')
            r_new_begin = r_new_end
        # 写回r_old
        print(delta_new)
        with open('r_old.txt', 'w') as r_old, open('r_new.txt', 'r') as r_new:
            for i in range(N):
                r_old_i = (1 - delta_new) / N + float(r_new.readline())
                r_old.write(str(r_old_i) + '\n')
        t += 1
        print("Iteration {} , error is {}".format(t, error))
    with open('result_block_su.txt', 'w') as r_result, open('r_old.txt', 'r') as r_old:
        for i in range(N):
            r_result.write(str(nodes[i]) + " " + r_old.readline())