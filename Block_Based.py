import numpy as np
import math
# block base alg, all on disk
def Block_BU(teleport, e, N, K):
    with open("r_old.txt", 'w') as f:
        for i in range(N):
            f.write(str(1 / N) + '\n')
    error = 1
    t = 0
    while error > e:
        r_new_begin = 0
        for i in range(K):
            r_new_end = min(N, r_new_begin + math.floor(N/K))
            r_new_block = [(1-teleport) / N] * (r_new_end - r_new_begin + 1)
            # 计算[r_new_begin,r_new_end)范围内的r_new
            with open('r_old.txt', 'r') as r_old, open('Sparse_Matrix.txt', 'r') as SM:
                while True:
                    # 遍历整个矩阵
                    data = SM.readline().replace('\r', '').replace('\n', '')
                    if not data:
                        break   # 到达文件尾,break
                    data = data.split() # 用空格分开,返回一个列表
                    src = int(data[0])  # 获得source
                    # 遍历r_old找到source的pr

                    # for j in range(1,len(data)):
                    #     if int(data[j]) < r_new_end:
                    #         while
                    #         r_new_block[int(data[j])] += teleport *









    return 0

# block stride update alg
def Block_SU(teleport, e, N):
    return 0