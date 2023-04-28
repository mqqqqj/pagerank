import copy
import math
import time
import matplotlib.pyplot as plt
import os
def Top100(result_file):
    res = {}
    with open(f'{result_file}.txt', 'r') as f:
        for line in f:
            line = line.split()
            res[line[0]] = float(line[1])
    res = sorted(res.items(), key=lambda item:item[1],reverse=True)[:100]
    with open(f'{result_file}_Top100.txt', 'w') as f:
        for key, val in res:
            f.write(key + " " + str(val) + '\n')

def draw_error_curve(errs, alg):
    plt.switch_backend('Agg')  # 后端设置'Agg' 参考：https://cloud.tencent.com/developer/article/1559466
    plt.plot(errs, 'b', label='error')  # epoch_losses 传入模型训练中的 loss[]列表,在训练过程中，先创建loss列表，将每一个epoch的loss 加进这个列表
    plt.ylabel('error')
    plt.xlabel('iteration')
    plt.savefig(os.path.join('./error_curves', f"{alg}.png"))  # 保存图片 路径：/imgPath/


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
    for j in range(K):
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
            for src, degree_and_dests in block.items():
                f.write(str(src) + " " )
                for item in degree_and_dests:
                    f.write(str(item) + " ")
                f.write("\n")
    return split_length



# block base alg, all on disk
# 问题出在,计算error之前r_new就需要通过计算出delta来正则化,而要计算出delta需要遍历完一整个r_new才计算的出来,
# 这在分块算法中是做不到的用本轮的delta正则化本轮的r_new,解决方法是将这一轮的delta留给下一轮计算
def Block_BU(teleport, e, nodes, K):
    start_time = time.time()
    N = len(nodes)
    read_count = 0
    write_count = 0
    with open("r_old.txt", 'w') as f:
        for i in range(N):
            f.write(str(1 / N) + '\n')
            write_count+=1
    error = 1
    error_list = []
    t = 0
    delta_new = 0
    # while t == 0:
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
                for n in range(N):
                    r_old_i = float(r_old.readline())
                    read_count+=1
                    while source < n:
                        data = SM.readline().replace('\r', '').replace('\n', '')
                        read_count+=1
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
                    read_count+=1
                for j in range(r_new_begin, r_new_end):
                    r_old_i = float(r_old.readline())
                    read_count+=1
                    error += abs((r_new_block[j] + (1 - delta_old) / N) - r_old_i)
            with open('r_new.txt', 'a') as r_new:
                for _, val in r_new_block.items():
                    r_new.write(str(val) + '\n')
                    # write_count+=1
            r_new_begin = r_new_end
        # 写回r_old
        with open('r_old.txt', 'w') as r_old, open('r_new.txt', 'r') as r_new:
            for i in range(N):
                r_old_i = (1 - delta_new) / N + float(r_new.readline())
                read_count+=1
                r_old.write(str(r_old_i) + '\n')
                write_count+=1
        t += 1
        error_list.append(error)
        print("Iteration {} , error is {}".format(t, error))
    end_time = time.time()
    print("===== Block-based Update Algorithm =====")
    print("Total Iterations: " + str(t))
    print("Total running time: " + str(end_time - start_time) + "s")
    print("Number of reads during the process: " + str(read_count))
    print("Number of writes during the process: " + str(write_count))
    with open('result_block_bu.txt', 'w') as r_result, open('r_old.txt', 'r') as r_old:
        for i in range(N):
            r_result.write(str(nodes[i]) + " " + r_old.readline())
    draw_error_curve(error_list, 'block_bu')

# block stride update alg
def Block_SU(teleport, e, nodes, K, split_length):
    start_time = time.time()
    N = len(nodes)
    read_count = 0
    write_count = 0
    with open("r_old.txt", 'w') as f:
        for i in range(N):
            f.write(str(1 / N) + '\n')
            write_count += 1
    error = 1
    error_list = []
    t = 0
    delta_new = 0
    while error > e:
        r_new_begin = 0
        error = 0
        delta_old = delta_new
        delta_new = 0
        with open('r_new.txt', 'w') as r_new:
            r_new.truncate()
        for i in range(K):  # K个块
            r_new_end = min(N, r_new_begin + math.ceil(N/K))    #块里的节点范围
            r_new_block = {}    #保存r_new
            for j in range(r_new_begin, r_new_end): #赋初值
                r_new_block[j] = (1 - teleport) / N
            # 计算[r_new_begin,r_new_end)范围内的r_new
            with open('r_old.txt', 'r') as r_old, open(f'striped_matrix/striped_matrix_{K}_{i}.txt', 'r') as SM:
                # print("open matrix {}".format(i))
                source = -1
                isend = 0   #保证SM读取到最后一行之后直接跳出
                for n in range(N):  # 遍历r_old
                    r_old_i = float(r_old.readline())   #获取r_old[i]
                    read_count+=1
                    if isend == split_length[i]:    #判断是否跳出
                        # (lambda x, y: x - 1 if i != (K - 1) else y - 1, math.ceil(N / K), N - K * math.ceil(N / K))
                        break
                    while source < n:   #只要SM当前行的source小于r_old下标,就需要一直读取
                        data = SM.readline()
                        read_count+=1
                        data = data.split()  # 用空格分开,返回一个列表
                        # print(n, source, data, i)
                        source = int(data[0])
                        degree = int(data[1])
                        dests = data[2:]
                    if source == n:  # 直到找到r_old和SM的对应项
                        isend += 1
                        for dest in dests:  #根据dest更新r_new
                            r_new_block[int(dest)] += teleport * r_old_i / degree
            # 为了正则化使用
            delta_new += sum(r_new_block.values()) #delta_new记录r_new所有成员的pagerank之和
            # 计算误差
            with open('r_old.txt', 'r') as r_old:
                for j in range(r_new_begin):
                    r_old.readline()
                    read_count+=1
                for j in range(r_new_begin, r_new_end):
                    r_old_i = float(r_old.readline())
                    read_count+=1
                    error += abs((r_new_block[j] + (1 - delta_old) / N) - r_old_i)
            with open('r_new.txt', 'a') as r_new:
                for _, val in r_new_block.items():
                    r_new.write(str(val) + '\n')
                    # write_count+=1
            r_new_begin = r_new_end
        # 写回r_old
        with open('r_old.txt', 'w') as r_old, open('r_new.txt', 'r') as r_new:
            for i in range(N):
                r_old_i = (1 - delta_new) / N + float(r_new.readline())
                read_count+=1
                r_old.write(str(r_old_i) + '\n')
                write_count+=1
        t += 1
        error_list.append(error)
        print("Iteration {} , error is {}".format(t, error))
    end_time = time.time()
    print("===== Block-Stripe Update Algorithm =====")
    print("Total Iterations: " + str(t))
    print("Total running time: " + str(end_time - start_time) + "s")
    print("Number of reads during the process: " + str(read_count))
    print("Number of writes during the process: " + str(write_count))
    with open('result_block_su.txt', 'w') as r_result, open('r_old.txt', 'r') as r_old:
        for i in range(N):
            r_result.write(str(nodes[i]) + " " + r_old.readline())
    draw_error_curve(error_list, 'block_su')


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
    node2num = {}  # dict
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
    ##3. Block_BU r_new也不允许在内存中
    SMatrix2dict(edges, nodes)
    Block_BU(teleport, e, nodes, K)
    Top100("result_block_bu")

    ##4. BLock_SU 把矩阵分成条带
    split_length = split_matrix(N, K)
    print(split_length)
    Block_SU(teleport, e, nodes, K, split_length)
    Top100("result_block_su")

