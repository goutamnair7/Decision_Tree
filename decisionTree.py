import sys
import math

class DTree():

    def __init__(self, name, d, idx):
        self.name = name.strip()
        self.idx = idx

        keys = d.keys()
        self.left_val = keys[0]
        self.right_val = keys[1]
        self.left_pos = d[keys[0]]['+']
        self.left_neg = d[keys[0]]['-']
        self.right_pos = d[keys[1]]['+']
        self.right_neg = d[keys[1]]['-']

        self.left = None
        self.right = None


def entropy_calc(count_pos, count_neg):

    if count_pos == 0 or count_neg == 0:
        return None

    total = count_pos + count_neg
    prob_pos = (count_pos * 1.0) / total
    prob_neg = (count_neg * 1.0) / total

    I1 = math.log(1.0/prob_pos) / math.log(2)
    I2 = math.log(1.0/prob_neg) / math.log(2)

    entropy = prob_pos * I1 + prob_neg * I2
    return entropy

def info_gain_calc(entropy_root, d, total):

    pt2 = 0
    for (k, v) in d.items():
        t = 0
        for j in d[k].keys():
            t += d[k][j]
        num = 0
        for j in d[k].keys():
            p1 = (d[k][j] * 1.0)/t
            I1 = math.log(1.0/p1) / math.log(2)
            num += p1 * I1

        p2 = (t * 1.0)/total * num
        pt2 += p2
    
    info_gain = entropy_root - pt2
    return info_gain

def next_best_attr(root_keys, side, root_entropy, root_total, lines, train_attr, root_idx):

    max_info = 0.0
    for attr in train_attr:
        idx = train_attr.index(attr)
        if idx == root_idx:
            continue
        d = {}
        for line in lines:
            prev_key_value = line.strip().split(",")[root_idx]
            if side == "left":
                if prev_key_value != root_keys[0]:
                    continue
            else:
                if prev_key_value != root_keys[1]:
                    continue

            value = line.strip().split(",")[idx]  
            class_ = line.strip().split(",")[-1].lower()  
            if class_ == "democrat" or class_ == "a" or class_ == "yes":
                class_ = '+'
            else:
                class_ = '-'
              
            if d.has_key(value):
                if d[value].has_key(class_):
                    d[value][class_] += 1
                else:
                    d[value][class_] = 1
            else:
                 d[value] = {}
                 d[value][class_] = 1
        
        info_gain = info_gain_calc(root_entropy, d, root_total)
        
        if info_gain > max_info:
            max_info = info_gain
            max_idx = idx
            max_attr = attr
            max_d = d
    
    values = []
    for line in lines:
        val = line.strip().split(",")[max_idx]
        values.append(val)
    values = set(values)
    
    keys = max_d.keys()
    if len(keys) < 2:
        diff_key = values.difference(set(keys)).pop()
        max_d[diff_key] = {'+':0, '-':0}
    else:
        s = set(['+','-'])
        for i in max_d.keys():
            k = max_d[i].keys()
            if len(k) < 2:
                diff_key = s.difference(set(k)).pop()
                max_d[i][diff_key] = 0
                
    if max_info >= 0.1:
        return (max_attr, max_idx, max_d)
    else:
        return (None, None, None)

def calc_error(lines, root):

    count = 0
    total_count = 0

    for line in lines:
        total_count += 1

        test_class = line.strip().split(",")[-1].lower()
        if test_class == "democrat" or test_class == "a" or test_class == "yes":
            test_class = '+'
        else:
            test_class = '-'

        val1 = line.strip().split(",")[root.idx]
        if val1 == root.left_val:
            node = root.left
            if node is None:
                if root.left_pos > root.left_neg:
                    pred_class = '+'
                else:
                    pred_class = '-'
            else:
                val2 = line.strip().split(",")[node.idx]
                if val2 == node.left_val:
                    if node.left_pos > node.left_neg:
                        pred_class = '+'
                    else:
                        pred_class = '-'
                else:
                    if node.right_pos > node.right_neg:
                        pred_class = '+'
                    else:
                        pred_class = '-'
        else:
            node = root.right
            if node is None:
                if root.right_pos > root.right_neg:
                    pred_class = '+'
                else:
                    pred_class = '-'
            else:
                val2 = line.strip().split(",")[node.idx]
                if val2 == node.left_val:
                    if node.left_pos > node.left_neg:
                        pred_class = '+'
                    else:
                        pred_class = '-'
                else:
                    if node.right_pos > node.right_neg:
                        pred_class = '+'
                    else:
                        pred_class = '-'
        
        if pred_class == test_class:
            count += 1
        
    error_count = total_count - count
    error = (error_count * 1.0) / total_count

    return error

def main():
    
    train_file = sys.argv[1]
    #train_file = "education_train.csv"

    f = open(train_file, "r")
    lines = f.readlines()
    f.close()
    
    train_attr = lines[0].strip().split(",")[:-1]
    del lines[0]

    count_pos = 0
    count_neg = 0
    for line in lines:
        train_class = line.strip().split(",")[-1].lower()
        if train_class == "democrat" or train_class == "a" or train_class == "yes":
            count_pos += 1
        else:
            count_neg += 1

    entropy_root = entropy_calc(count_pos, count_neg)

    max_info = 0.0
    for attr in train_attr:
        idx = train_attr.index(attr)
        d = {}
        for line in lines:
            value = line.strip().split(",")[idx]
            class_ = line.strip().split(",")[-1].lower()
            if class_ == "democrat" or class_ == "a" or class_ == "yes":
                class_ = '+'
            else:
                class_ = '-'

            if d.has_key(value):
                if d[value].has_key(class_):
                    d[value][class_] += 1
                else:
                    d[value][class_] = 1
            else:
                d[value] = {}
                d[value][class_] = 1
    
        info_gain = info_gain_calc(entropy_root, d, count_pos+count_neg)
        
        if info_gain > max_info:
            max_info = info_gain
            max_attr = attr
            max_idx = idx
            max_d = d
    
    values = []
    for line in lines:
        val = line.strip().split(",")[max_idx]
        values.append(val)
    values = set(values)
    
    keys = max_d.keys()
    if len(keys) < 2:
        diff_key = values.difference(set(keys)).pop()
        max_d[diff_key] = {'+':0, '-':0}
    else:
        s = set(['+','-'])
        for i in max_d.keys():
            k = max_d[i].keys()
            if len(k) < 2:
                diff_key = s.difference(set(k)).pop()
                max_d[i][diff_key] = 0
    
    root = DTree(max_attr, max_d, max_idx)
    
    root_attr = max_attr
    root_attr_idx = max_idx
    root_keys = max_d.keys()
    root_d = max_d
   
    #print root_attr, " ", root_attr_idx

    root_entropy_left = entropy_calc(root_d[root_keys[0]]['+'], root_d[root_keys[0]]['-'])
    if root_entropy_left is None:
        root.left = None
    else:
        root_total_left = root_d[root_keys[0]]['+'] + root_d[root_keys[0]]['-']
        (max_attr, max_idx, max_d) = next_best_attr(root_keys, "left", root_entropy_left, root_total_left, lines, train_attr, root_attr_idx)
        if max_attr is None:
            root.left = None
        else:
            dtree_left = DTree(max_attr, max_d, max_idx)
            root.left = dtree_left
    
    root_entropy_right = entropy_calc(root_d[root_keys[1]]['+'], root_d[root_keys[1]]['-'])
    if root_entropy_right is None:
        root.right = None
    else:
        root_total_right = root_d[root_keys[1]]['+'] + root_d[root_keys[1]]['-']
        (max_attr, max_idx, max_d) = next_best_attr(root_keys, "right", root_entropy_right, root_total_right, lines, train_attr, root_attr_idx)
        if max_attr is None:
            root.right = None
        else:
            dtree_right = DTree(max_attr, max_d, max_idx)
            root.right = dtree_right

    
    print "[%s+/%s-]" % (count_pos, count_neg)
    print "%s = %s: [%s+/%s-]" % (root.name, root.left_val, root.left_pos, root.left_neg)
    left = root.left
    if left is not None:
        print "| %s = %s: [%s+/%s-]" % (left.name, left.left_val, left.left_pos, left.left_neg)
        print "| %s = %s: [%s+/%s-]" % (left.name, left.right_val, left.right_pos, left.right_neg)
    
    print "%s = %s: [%s+/%s-]" % (root.name, root.right_val, root.right_pos, root.right_neg)
    right = root.right
    if right is not None:
        print "| %s = %s: [%s+/%s-]" % (right.name, right.left_val, right.left_pos, right.left_neg)
        print "| %s = %s: [%s+/%s-]" % (right.name, right.right_val, right.right_pos, right.right_neg)


    error_train = calc_error(lines, root)
    print "error(train): ", error_train

    test_file = sys.argv[2]
    #test_file = "education_test.csv"

    f = open(test_file, "r")
    lines = f.readlines()
    f.close()
    
    del lines[0]
    
    error_test = calc_error(lines, root)
    print "error(test): ", error_test

if __name__ == "__main__":
    main()
