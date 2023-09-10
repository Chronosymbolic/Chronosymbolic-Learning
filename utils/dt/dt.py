import os
import sys
import pickle
import copy
import math
import json
from datetime import datetime
import time
from collections import deque
from sklearn import tree
import z3
import numpy as np
from horndb.horndb import HornRelation


Z3_TRUE = z3.BoolVal(True)
Z3_FALSE = z3.BoolVal(False)

def substitute_and_eval(expr: str, sub_list):
    for sub in sub_list:
        expr = expr.replace(sub[0], f'({str(sub[1])})')
    try:
        res = eval(expr)
    except:
        print('error')
    return res


class DecisionTreeWrapper:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.logger = parent.logger
        self.params = parent.params
        self.OCT = self.params['OCT']
        self.rels = parent.rels
        self.eq_solver = parent.eq_solver
        self.mod_nums = parent.mod_nums
        self.div_nums = parent.div_nums
    
    def get_rel_args(self, rel: HornRelation):
        return self.parent.get_rel_args(rel)


class C5DT(DecisionTreeWrapper):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        if sys.platform == 'linux':
            self.C5_exec_path = 'utils/dt/C50/c5.0.dt_entropy'
            # self.C5_exec_path = '/dev/shm/c5.0.dt_entropy'
        elif sys.platform == 'darwin':
            self.C5_exec_path = 'utils/dt/C50/c5.0.dt_entropy-macos'
        else:
            self.C5_exec_path = 'utils/dt/C50/c5.0.dt_entropy'

        self.file_name = parent.file_name
        self.seed = self.params['DT']['RNDSeed']
        self.rel_to_c5_rel_map = {}
        self.c5_rel_to_rel_map = {}
        self.decl_to_rel_map = {}
        self.arg_name_to_expr_map = {}
        self.svm_name_to_expr_map = parent.svm_name_to_expr_map
        self.svm_name_to_str_map = parent.svm_name_to_str_map  # for C5 "*.names" input
        for i, rel in enumerate(self.rels):
            r_decl = rel.decl()
            self.c5_rel_to_rel_map['PRED_'+str(i)] = rel
            # keys must be decl type to prevent collision!
            self.rel_to_c5_rel_map[r_decl] = 'PRED_'+str(i)
            self.decl_to_rel_map[r_decl] = rel

    def update_svm_maps(self):
        self.svm_name_to_expr_map = self.parent.svm_name_to_expr_map
        self.svm_name_to_str_map = self.parent.svm_name_to_str_map

    def init_C5(self, target=None):
        with open(self.file_name+'.names', 'w') as f:
            f.write('')  # clear

        with open(self.file_name+'.intervals', 'w') as f:
            f.write('')  # clear

        f_names = open(self.file_name+'.names', 'w')
        f_intervals = open(self.file_name+'.intervals', 'w')
        lower_interval = 2
        upper_interval = 2
        str_names = 'invariant.\n$pc: '
        str_intervals = ''
        self.arg_name_to_expr_map.clear()
        
        if target is None:
            target = self.rels[:]
        for i, rel in enumerate(target):
            # names of rels
            rel_name_i = self.rel_to_c5_rel_map[rel.decl()]
            if i == len(target) - 1:
                str_names += rel_name_i + '.\n'
            else:
                str_names += rel_name_i + ','

        for i, rel in enumerate(target):
            # names of args
            rel_name_i = self.rel_to_c5_rel_map[rel.decl()]
            # mod and div features
            for j, arg_j in enumerate(self.get_rel_args(rel)):
                # if self.unknowns[rel.decl()][j]:
                #     continue
                if z3.is_bool(arg_j):
                    continue
                arg_name_j = rel_name_i + '!V_' + str(j)
                str_names += arg_name_j + ": continuous.\n"
                upper_interval += 1
                self.arg_name_to_expr_map[arg_name_j] = arg_j
                
                # mod features
                if len(self.mod_nums) > 0:
                    for m_num in self.mod_nums:
                        arg_name_j_mod = arg_name_j + 'mod' + str(m_num)
                        str_names += f"{arg_name_j_mod}:= ({arg_name_j} % {m_num} + {m_num}) % {m_num}.\n"
                        upper_interval += 1
                
                # div features
                if len(self.div_nums) > 0:
                    for d_num in self.div_nums:
                        arg_name_j_div = arg_name_j + 'div' + str(d_num)
                        str_names += f"{arg_name_j_div}:= ({arg_name_j} - {arg_name_j} % {d_num}) / {d_num}.\n"
                        upper_interval += 1

            # octogon features
            if self.params['OCT']:
                for j, arg_j in enumerate(self.get_rel_args(rel)):
                    arg_name_j = rel_name_i + '!V_' + str(j)
                    for k in range(j+1, len(self.get_rel_args(rel))):
                        arg_k = rel.arg(k)
                        if not z3.is_bool(arg_j) and not z3.is_bool(arg_k):
                        # if not z3.is_bool(arg_j) and not z3.is_bool(arg_k)\
                        #     and not self.unknowns[rel.decl()][j] and not self.unknowns[rel.decl()][k]:
                            arg_name_k = rel_name_i + '!V_' + str(k)
                            str_names += arg_name_j + '+' + arg_name_k + \
                                ":=" + arg_name_j + ' + ' + arg_name_k + ".\n"
                            str_names += arg_name_j + '-' + arg_name_k + \
                                ":=" + arg_name_j + ' - ' + arg_name_k + ".\n"
                            upper_interval += 2

            # SVM features
            # self.update_svm_maps()
            for svm_name, expr in self.svm_name_to_str_map.items():
                rel_name_in_svm_name = svm_name.split('!')[0]
                if rel_name_in_svm_name == rel_name_i:
                    # this svm_name is related to this rel
                    str_names += svm_name + ":=" + expr + ".\n"
                    upper_interval += 1

            # intervals
            str_intervals += str(lower_interval) + \
                                    ' ' + str(upper_interval) + '\n'
            lower_interval = upper_interval
            upper_interval = lower_interval

        str_names += "invariant: true, false.\n"
        f_names.write(str_names)
        f_names.close()
        f_intervals.write(str_intervals)
        f_intervals.close()

        # self.logger.debug(f'C5 names file:\n{str_names}')
        return
    
    def generate_C5_data(self, pos_data_set, neg_data_set, target=None):
        with open(self.file_name+'.data', 'w') as f:
            f.write('')  # clear

        data_str = ''

        # print(self.neg_data_set)
        # print(self.parent.neg_data_set)
        if target is None:
            target = pos_data_set.get_rels()[:] + pos_data_set.get_rels()[:]
        for rel in target:
            for dp in pos_data_set.get_dps(rel):
                data_str += self.rel_to_c5_rel_map[rel.decl()] + ','
                for i, d in enumerate(dp):
                    # if self.unknowns[rel.decl()][i]:
                    #     continue
                    if isinstance(d, bool):
                        bit = '1' if d else '0'
                        data_str += bit + ','
                    else:
                        data_str += str(d) + ','
                data_str += 'true\n'

        for rel in target:
            for dp in neg_data_set.get_dps(rel):
                data_str += self.rel_to_c5_rel_map[rel.decl()] + ','
                for i, d in enumerate(dp):
                    # if self.unknowns[rel.decl()][i]:
                    #     continue
                    if isinstance(d, bool):
                        bit = '1' if d else '0'
                        data_str += bit + ','
                    else:
                        data_str += str(d) + ','
                data_str += 'false\n'

        f_data = open(self.file_name+'.data', 'w')
        f_data.write(data_str)
        f_data.close()

        if self.parent.cand_counter % self.params['Verbosity']['PrintNewCandFreq'] == 0:
            self.logger.debug(f'C5 data file:\n{data_str}')

    def construct_formula(self, stack, sub_pt):
        final_fml = []
        # leaf
        if sub_pt['children'] is None:
            classification = sub_pt['classification']
            # self.logger.debug(f'Leaf Node, {classification}')
            if classification:
                final_fml.append(list(stack))
                return final_fml
            else:
                return final_fml

        # internal
        expr = None
        attr_name = sub_pt['attribute']
        # self.logger.debug(f'Internal Node, cut attribute: {attr_name}')
        cut = int(sub_pt['cut'])

        if attr_name.find('+') != -1:
            left, right = attr_name.split('+')
            left = left.strip()
            right = right.strip()
            left_expr = self.arg_name_to_expr_map[left]
            right_expr = self.arg_name_to_expr_map[right]
            expr = left_expr + right_expr <= cut

        elif attr_name.find('-') != -1:
            left, right = attr_name.split('-')
            left = left.strip()
            right = right.strip()
            left_expr = self.arg_name_to_expr_map[left]
            right_expr = self.arg_name_to_expr_map[right]
            expr = left_expr - right_expr <= cut

        elif attr_name.find('SVM') != -1:
            self.update_svm_maps()
            svm_expr = self.svm_name_to_expr_map[attr_name]
            expr = svm_expr <= cut
        
        elif attr_name.find('mod') != -1:
            left, right = attr_name.split('mod')
            left = left.strip()
            right = right.strip()
            left_expr = self.arg_name_to_expr_map[left]
            right_expr = int(right)
            expr = left_expr % right_expr <= cut
        
        elif attr_name.find('div') != -1:
            left, right = attr_name.split('div')
            left = left.strip()
            right = right.strip()
            left_expr = self.arg_name_to_expr_map[left]
            right_expr = int(right)
            expr = left_expr / right_expr <= cut

        else:  # attributes
            attr_expr = self.arg_name_to_expr_map[attr_name]
            if not z3.is_bool(attr_expr):
                expr = attr_expr <= cut
            else:  
                # handle bool variables
                # cut could only be 0<=cut<1 (>1 doesn't make any sense), attr<=cut always eval to False
                expr = attr_expr == False

        stack.append(expr)
        children = sub_pt['children']
        final_fml_left = self.construct_formula(stack, children[0])
        stack.pop()
        stack.append(z3.Not(expr))
        final_fml_right = self.construct_formula(stack, children[1])
        stack.pop()
        final_fml = final_fml_left + final_fml_right
        return final_fml

    def parse_ptree(self, pt, target=None):
        """json parsing"""
        children = pt['children']
        candidate = None
        if children is None:  # if only have root node
            self.logger.debug('PT has no children')
            candidate = Z3_TRUE if pt['classification'] else Z3_FALSE
            for rel in self.rels:
                self.cand_map[rel.decl()] = candidate
            return

        if target is None:
            target = self.rels

        for i, child in enumerate(children):
            rel = target[i]
            C5_rel_name = self.rel_to_c5_rel_map[rel.decl()]
            # self.logger.debug(f'TAG: {C5_rel_name}')

            if child['children'] is None:
                candidate = Z3_TRUE if child['classification'] else Z3_FALSE
            else:
                stack = deque()
                stack.append(Z3_TRUE)
                final_formula = self.construct_formula(stack, child)
                disj = []
                for fml in final_formula:
                    conj = []
                    for c in fml:
                        conj.append(c)
                    d = z3.And(conj)
                    disj.append(d)

                if len(disj) == 1:
                    candidate = disj[0]
                else:
                    candidate = z3.Or(disj)

            # simplified_cand = z3.simplify(candidate)
            simplified_cand = self.eq_solver(candidate).as_expr()
        return simplified_cand

    def learn(self, pos_data_set, neg_data_set, target=None):
        """
        target is None or []: all rels
        """
        assert(len(target) == 2)
        self.init_C5(target)
        self.generate_C5_data(pos_data_set, neg_data_set, target)

        with open(self.file_name+".json", 'w') as f:
            f.write('')  # clear old json file

        cmd = self.C5_exec_path + f' -I {self.seed} -m 1 -f ' + self.file_name + ' 2>&1'
        p = os.popen(cmd, 'r')
        if p is None:
            self.logger.error("popen failed!")
            raise Exception("popen failed!")
        buf = p.read()
        # self.logger.debug(f'C5 out buffer: {buf}')
        # f = open('tmp/c5_temp', 'w+')
        # f.write(buf)
        p.close()
        # f.close()
        self.logger.info(f'C5 cmd: {cmd}')
        if buf.find('Segmentation fault') != -1 or buf.find('Kill') != -1:
            self.logger.error('C5 does not properly execute')
            raise RuntimeError('C5 does not properly execute')
            # for t in target:
            #     self.neg_data_set.clear(t)
            #     self.cand_map[t.decl()] = Z3_TRUE if random.randint(0, 1) == 1 else Z3_FALSE
            # # clear tentative dps and try again
            # self._C5_learn(target)
            # self.invalidate_queries()
            # self.cand_postprocessing()
            # self.dt_time += time.time() - start_time
            # self.logger.debug(str(self.pos_data_set))
            # self.logger.debug(str(self.neg_data_set))
            # self.logger.debug(f'DT Calls: {self.dt_calls}, Total DT time: {self.dt_time}')

        with open(self.file_name+".json") as json_f:
            json_dict = json.load(json_f)

        cand = self.parse_ptree(json_dict, target)
        return cand


class SklearnDT(DecisionTreeWrapper):
    def __init__(self, parent, save_dt=False) -> None:
        super().__init__(parent)
        self.clf = tree.DecisionTreeClassifier(random_state=self.params['DT']['RNDSeed'],
                                               max_features=None,
                                               criterion=self.params['DT']['Criterion'],
                                               splitter=self.params['DT']['Splitter'],
                                            #    class_weight='balanced',
                                               )
        self.save_dt = save_dt
        self.free_vars_prefix = 'Var_'
        self.file_idx = 0
        self.feats_expr_map = []  # feats idx as idx
        self.rel_args = dict()
        now = datetime.now()  # current date and time
        self.date_time_path = 'decision_trees/' + now.strftime("%y%m%d_%H%M%S")

        self.svm_name_to_expr_map = parent.svm_name_to_expr_map
        self.svm_name_to_coeff_map = parent.svm_name_to_coeff_map
        self.svm_name_to_str_map = parent.svm_name_to_str_map


    def update_svm_maps(self):
        self.svm_name_to_expr_map = self.parent.svm_name_to_expr_map
        self.svm_name_to_coeff_map = self.parent.svm_name_to_coeff_map
        self.svm_name_to_str_map = self.parent.svm_name_to_str_map

    def add_features(self, svm_feats, svm_feats_str, svm_exprs_coeff, mod_nums, div_nums, data, 
                     rel: HornRelation, rel_name_svm: str):
        """
        Add features to data,
        and update the feats_idx: z3 expressions map
        """
        # octogon features
        if len(data) == 0:
            return []
        args = self.get_rel_args(rel)
        feats_num = len(data[0])
        new_data = []
        new_feats_expr = copy.deepcopy(args)  # list(z3_expr)
        if self.OCT:
            for i, dp in enumerate(data):
                new_feats = []
                for j, arg_j in enumerate(dp):
                    for k in range(j+1, feats_num):
                        arg_k = dp[k]
                        # if not isinstance(arg_j, bool) and not isinstance(arg_k, bool):
                        if not z3.is_bool(args[j]) and not z3.is_bool(args[k]):
                            new_feats.append(arg_j + arg_k)
                            new_feats.append(arg_j - arg_k)
                            if i == 0:  # only add once
                                new_feats_expr.append(args[j] + args[k])
                                new_feats_expr.append(args[j] - args[k])
                new_data.append(list(dp)+new_feats)
        
        new_data_svm = []
        # svm features
        for i, dp in enumerate(data):
        #     sub_list = []
        #     # s = z3.Solver()
        #     for j in range(len(args)):
        #         # sub_list.append((args[j], z3.IntVal(dp[j])))
        #         sub_list.append((f'{rel_name_svm}!V_{str(j)}', dp[j]))
            #     s.add(args[j] == dp[j])
            # _ = s.check()
            # m = s.model()
            
            new_feats = []
            for feat in svm_exprs_coeff:
                try:
                    new_feat_d = 0
                    for k, d in enumerate(dp):
                        if not z3.is_bool(args[k]): 
                            new_feat_d += d * int(feat[k])
                    # new_feat_d = substitute_and_eval(str(feat), sub_list)
                    # new_feat_d = z3.simplify(z3.substitute(feat, *sub_list))
                    # new_feat_d = new_feat_d.as_long()
                    # new_feat_d = m.eval(feat).as_long()
                except:
                    print('error')
                new_feats.append(new_feat_d)
            assert(len(new_feats)==len(svm_feats))
            new_data_svm.append(new_data[i]+new_feats)
        new_feats_expr.extend(svm_feats)

        # mod, div features
        new_data_md = []
        for i, dp in enumerate(data):
            new_feats = []
            for j, arg_j in enumerate(dp):
                if not z3.is_bool(args[j]):
                    for m_num in mod_nums:
                        new_feats.append(arg_j % m_num)
                    for d_num in div_nums:
                        new_feats.append(arg_j / d_num)
            new_data_md.append(new_data_svm[i]+new_feats)
        mod_div_feats = []
        for arg in args:
            if not z3.is_bool(arg):
                for m_num in mod_nums:
                    mod_div_feats.append(arg % m_num)
                for d_num in div_nums:
                    mod_div_feats.append(arg / d_num) 
        new_feats_expr.extend(mod_div_feats)

        self.feats_expr_map = copy.deepcopy(new_feats_expr)
        return new_data_md

    def print_features(self):
        print(f'Features: {self.feats_expr_map}')

    def print_as_text(self, clf):
        self.print_features()
        print(tree.export_text(clf))
    
    def print_as_program(self, clf):
        self.print_features()
        left      = clf.tree_.children_left
        right     = clf.tree_.children_right
        threshold = clf.tree_.threshold
        feats = clf.tree_.feature
        value = clf.tree_.value
        def recurse(left, right, threshold, feats, node):
            # if threshold[node] != -2:
            if left[node] != right[node]:  # not leaf
                print("if ( Var_" + feats[node] + " <= " + str(threshold[node]) + " ) {")
                if left[node] != -1:
                    recurse(left, right, threshold, feats, left[node])
                print("} else {")
                if right[node] != -1:
                    recurse(left, right, threshold, feats, right[node])
                print("}")
            else:
                pass
                print("return " + str(value[node]))
        recurse(left, right, threshold, feats, 0)

    def get_expr(self, clf):
        left      = clf.tree_.children_left
        right     = clf.tree_.children_right
        threshold = clf.tree_.threshold
        feats_idx = clf.tree_.feature
        value = clf.tree_.value
        stack = deque()
        stack.append(Z3_TRUE)

        def recurse(left, right, threshold, feats_idx, node, stack):
            if left[node] == right[node]:  # leaf
                final_fml = []
                # decide if the leaf is the "true" class
                if value[node][0][1] != 0:
                    final_fml.append(list(stack))
                return final_fml
            else:
                # print("if ( " + feats_idx[node] + " <= " + str(threshold[node]) + " ) {")
                feat_expr = self.feats_expr_map[feats_idx[node]]
                if not z3.is_bool(feat_expr):
                    expr = feat_expr <= math.floor(threshold[node])  # round down
                else:
                    expr = feat_expr == False
                if left[node] != -1:
                    stack.append(expr)
                    final_fml_left = recurse(left, right, threshold, feats_idx, left[node], stack)
                    stack.pop()
                if right[node] != -1:
                    stack.append(z3.Not(expr))
                    final_fml_right = recurse(left, right, threshold, feats_idx, right[node], stack)
                    stack.pop()
                final_fml = final_fml_left + final_fml_right
                return final_fml

        candidate = None
        if left[0] == right[0]:  # only one root node
            candidate = Z3_TRUE if value[0][1] != 0 else Z3_FALSE
        else:
            final_fml = recurse(left, right, threshold, feats_idx, 0, stack)
            disj = []
            for fml in final_fml:
                conj = []
                for c in fml:
                    conj.append(c)
                d = z3.And(conj)
                disj.append(d)

            if len(disj) == 1:
                candidate = disj[0]
            else:
                candidate = z3.Or(disj)
        simplified_cand = self.eq_solver(candidate).as_expr()
        return simplified_cand
    
    def save_tree(self, clf, feats, data, label, result, rel_name='Predicate'):
        # save dt and feats for visualization
        if not os.path.exists(self.date_time_path):
            os.makedirs(self.date_time_path)
        file = open(f'{self.date_time_path}/dt_{self.file_idx}.pk', 'wb')
        pickle.dump([clf, feats, data, label, rel_name, result], file)
        print(f'---- dt_{self.file_idx}.pk saved')
        file.close()
        self.file_idx += 1

    def learn(self, svm_feats, svm_feats_str, svm_exprs_coeff,
              mod_nums, div_nums,
              pos, neg, rel: HornRelation, rel_name_svm: str):
        if len(pos) == 0 and len(neg) == 0:
            return
        X = [dp for dp in pos] + [dp for dp in neg]
        Y = [1 for _ in range(len(pos))] + [0 for _ in range(len(neg))]
        X = self.add_features(svm_feats, svm_feats_str, svm_exprs_coeff, mod_nums, div_nums, X, rel, rel_name_svm)
        self.clf = self.clf.fit(X, Y)
        fml = self.get_expr(self.clf)

        if self.save_dt:
            feats_expr_str_map = [str(expr) for expr in self.feats_expr_map]
            self.save_tree(self.clf, feats_expr_str_map, X, Y, str(fml), str(rel.decl()))
        return fml