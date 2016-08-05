#-*- coding=utf-8 -*-

#-----------------------
# Named:    Decision tree
# Created:  2016-08-04
# @Author:  Qianfeng
#-----------------------


# 示例数据[来源网站、位置、是否阅读过FAQ、浏览网页数、选择服务类型]
my_data=[['slashdot','USA','yes',18,'None'],
        ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]


class DecisionNode:
    """DecisionNode for all node of tree.(include interal_node and leaf_node)"""
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb


# 在某一列上对数据集合进行拆分，能够处理数值型数据或名词性数据
def divideSet(rows, column, value):
    # column 为列索引
    # 定义一个函数，令其高速我们数据行属于第一组（返回值为true)还是第二组（返回值为false）
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value
    else:
        split_function = lambda row: row[column] == value

    # 将数据集拆分成两个集合，并返回
    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return (set1, set2)

# 对各种可能的结果进行计数（每一行数据的最后一列记录了这一计数结果）
def uniqueCounts(rows):
    results = {}
    for row in rows:
        # 计数结果在最后一列
        r = row[len(row)-1]
        results[r] = results.get(r, 0) + 1
    return results

def results(rows):
    # 概率形式输出结果
    labelProb = {}
    for row in rows:
        labelProb.setdefault(row[-1],[0,0])
        labelProb[row[-1]][0] += 1
    for key in labelProb.keys():
        labelProb[key][1] = float(labelProb[key][0])/len(rows)
    return labelProb


# Gini Impurity
# 基尼不纯度：Gini = p*(1-p)-->二分类时（产生二叉树）
# 当为多叉树时，下面函数使用，体现了普适性
def giniImpurity(rows):
    total = len(rows)
    counts = uniqueCounts(rows)
    imp = 0
    for k1 in counts:
        p1 = float(counts[k1])/total
        for k2 in counts:
            if k1 == k2:
                continue
            p2 = float(counts[k2])/total
            imp += p1 * p2
    return imp


        
 # Information Entropy
def entropy(rows):
    from math import log
    log2 = lambda x: log(x)/log(2)
    results = uniqueCounts(rows)
    # 计算熵值
    ent = 0.0
    for r in results.keys():
        p = float(results[r])/len(rows)
        ent = ent-p * log2(p)
    return ent


# 递归构建树
def buildTree(rows, scoref=entropy, mingain=0.0):
    if len(rows) == 0:
        return DecisionNode()
    current_score = scoref(rows)

    # 定义一些变量以记录最佳拆分条件
    best_gain = mingain
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(column_count): # 对每列进行测试
        column_values = {}
        for row in rows: # 遍历列中所有值
            column_values[row[col]] = 1

        for value in column_values.keys():
            (set1, set2) = divideSet(rows, col, value)

            # 信息增益
            p = float(len(set1))/len(rows)
            gain = current_score - p*scoref(set1) - (1-p)*scoref(set2)

            if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)

    # 创建分支
    print best_gain
    if best_gain > mingain:
        trueBranch = buildTree(best_sets[0],mingain=mingain)
        falseBranch = buildTree(best_sets[1],mingain=mingain)
        return DecisionNode(col=best_criteria[0], value=best_criteria[1],
            tb=trueBranch, fb=falseBranch)
    else:
        return DecisionNode(results=results(rows))


def printTree(tree, indent=''):
    if tree.results!=None:
        print tree.results
    else:
        #打印判断条件
        print str(tree.col)+':'+str(tree.value)+'? '

        # 打印分支
        print indent+'T->',
        printTree(tree.tb, indent+' ')
        print indent+'F->',
        printTree(tree.fb, indent+' ')




'''
# ===================================================
# 图形显示树
def getWidth(tree):
    if tree.tb == None and tree.fb == None:
        return 1
    return getWidth(tree.tb) + getWidth(tree.fb)

# 一个分支的深度等于其最长子分支的总深度加1
def getDepth(tree):
    if tree.tb == None and tree.fb == None:
        return 0
    return max(getDepth(tree.tb), getDepth(tree.fb)) + 1

from PIL import Image, ImageDraw
def drawtree(tree, jpeg='tree.jpg'):
    w = getWidth(tree) * 100
    h = getDepth(tree) * 100 + 120

    img = Image.new('RGB', (w,h), (255,255,255))
    draw = ImageDraw.Draw(img)

    drawNode(draw, tree, w/2, 20)
    img.save(jpeg, 'JPEG')

def drawNode(draw, tree, x, y):
    if tree.results == None:
        # 得到每个分支的宽度
        w1 = getWidth(tree.fb) * 100
        w2 = getWidth(tree.tb) * 100

        # 确定此节点所要占据的总空间
        left = x - (w1+w2)/2
        right = x - (w1+w2)/2

        # 绘制判断条件字符串
        draw.text((x-20, y-10), str(tree.col)+':'+str(tree.value), (0,0,0))

        # 绘制到分支的连线
        draw.line((x,y,left+w1/2,y+100).fill(255,0,0))
        draw.line((x,y,right+w2/2,y+100).fill(255,0,0))

        # 绘制分支的节点
        drawNode(draw, tree.fb, left+w1/2, y+100)
        drawNode(draw, tree.tb, right+w2/2, y+100)
    else:
        txt = ' \n'.join(['%s:%d' % v for v in tree.results.items()])
        draw.text((x-20,y),txt,(0,0,0))
'''

# ============================
def classify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        if isinstance(v, int) or isinstance(v, float):
            if v >= tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        else:
            if v == tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
    return classify(observation, branch)


def mdclassify(observation, tree):
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        if v == None:
            # 二叉树两边都有，同时向下遍历
            tr, fr = mdclassify(observation, tree.tb), mdclassify(observation,tree.fb)
            # 做归一化，因为左右分支合并成为一个整体，对各分支计数进行加权
            # 权重即为数据项位于各分支的比例
            tcount = sum(tr.values())
            fcount = sum(fr.values())
            tw = float(tcount)/(tcount + fcount)
            fw = float(fcount)/(tcount + fcount)
            result = {}
            for k, v in tr.items():
                result[k] = v * tw
            for k, v in fr.items():
                result[k] = result.get(k,0) + v * fw
                # result.setdefault(k,0)
                # result[k] += v * fw
            return result
        else:
            if isinstance(v, int) or isinstance(v,float):
                if v >= tree.value:
                    branch = tree.tb
                else:
                    branch = tree.fb
            else:
                if v == tree.value:
                    branch = tree.tb
                else:
                    branch = tree.fb
            return mdclassify(observation, branch)



#===================================
# 树剪枝
def prune(tree, mingain):
    # mingain is the entropy threshold.
    # 如果不是叶节点，则进行递归剪枝操作
    if tree.tb.results == None:
        prune(tree.tb, mingain)
    if tree.fb.results == None:
        prune(tree.fb, mingain)

    # 如果两个分支都是 leaf_node,判断是否需要合并
    if tree.tb.results != None and tree.fb.results != None:
        # 构造合并后的数据集
        tb, fb = [],[]
        for v, c in tree.tb.results.items():
            tb += [[v]] * c[0]
        for v, c in tree.fb.results.items():
            fb += [[v]] * c[0]

        # 检查熵的减少情况
        delta = entropy(tb + fb) - (entropy(tb) + entropy(fb)/2)
        if delta < mingain:
            # 合并分支
            tree.tb, tree.fb = None, None
            tree.results = results(tb+fb)


# ==========================
# 回归树--处理连续型label
def variance(rows):
    if len(rows) == 0:
        return 0
    data = [float(row[len(row)-1]) for row in rows]
    # 如果使用numpy 数组，可采用 flat OR flatten
    mean = sum(data)/len(data)
    variance = sum([(d - mean)**2 for d in data])/len(data)
    # E(x**2)-(E(x))**2
    # mean2 = sum([d**2 for d in data])/len(data)
    # mean = sum(data)/len(data)
    # variance = mean2 - mean
    return variance

# 对住房价格进行建模






