import os
import sys
from datetime import datetime
import time
import z3
from ordered_set import OrderedSet
from horndb.horndb import HornRelation

class SVMWrapper:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.logger = parent.logger
        self.params = parent.params
        self.OCT = self.params['OCT']
        self.rels = parent.rels
        self.eq_solver = parent.eq_solver
        self.mod_nums = parent.mod_nums
        self.div_nums = parent.div_nums
        self.svm_name_to_expr_map = parent.svm_name_to_expr_map
        self.svm_name_to_coeff_map = parent.svm_name_to_coeff_map  # {svm_name: [coeff]}
        self.svm_name_to_str_map = parent.svm_name_to_str_map  # for C5 "*.names" input
        self.rel_to_c5_rel_map = parent.rel_to_c5_rel_map
    
    def get_rel_args(self, rel: HornRelation):
        return self.parent.get_rel_args(rel)


class LibSVMLearner(SVMWrapper):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.file_name = parent.file_name
        if sys.platform == 'linux':
            self.svm_exec_path = 'utils/svm/libsvm/svm-invgen'
            # self.svm_exec_path = '/dev/shm/svm-invgen'
        elif sys.platform == 'darwin':
            self.svm_exec_path = 'utils/svm/libsvm/svm-invgen-macos'
        else:
            self.svm_exec_path = 'utils/svm/libsvm/svm-invgen'
    
    def learn(self, pos_data_set, neg_data_set, target=None):
        if target is None:
            self.svm_name_to_expr_map.clear()
            self.svm_name_to_str_map.clear()
            self.svm_name_to_coeff_map.clear()
        else:  # delete all keys that is related to rels in target 
            rel_names = [self.rel_to_c5_rel_map[t.decl()] for t in target]
            ks = list(self.svm_name_to_expr_map.keys())
            for rel_name in rel_names:
                self.svm_name_to_coeff_map.pop(rel_name, 0)
                for k in ks:
                    if rel_name in k:
                        # self.logger.debug(f'Attr {k} for rel {rel_name} purged')
                        self.svm_name_to_expr_map.pop(k, 0)  # if pop fails, default val = 0
                        self.svm_name_to_str_map.pop(k, 0)

        svm_calls = 0
        for rel in self.rels:
            if target is None or rel in target:
                args = self.get_rel_args(rel)
                num_svm_vars = 0
                for i, arg in enumerate(args):
                    # if z3.is_bool(arg) or self.unknowns[rel.decl()][i]:
                    if z3.is_bool(arg):
                        continue
                    num_svm_vars += 1

                if len(args) == 0:  # skip trivial rels
                    continue
                if num_svm_vars >= 69:
                    self.logger.error('Too many vars, SVM does not support')
                    continue

                svm_str = ''
                pn = nn = 0
                C5_rel_name = self.rel_to_c5_rel_map[rel.decl()]
                dp_no_bool_dataset_p = OrderedSet()
                dp_no_bool_dataset_n = OrderedSet()
                if pos_data_set.is_empty(rel) or neg_data_set.is_empty(rel):
                    # only pos/neg dps are inputted
                    # self.logger.error('SVM skipped')
                    continue

                for dp in pos_data_set.get_dps(rel):
                    dp_no_bool = []
                    for i, d in enumerate(dp):
                        # if not isinstance(d, bool) and not self.unknowns[rel.decl()][i]:
                        if not isinstance(d, bool):
                            dp_no_bool.append(d)
                    dp_no_bool_dataset_p.add(tuple(dp_no_bool))

                for dp in neg_data_set.get_dps(rel):
                    dp_no_bool = []
                    for i, d in enumerate(dp):
                        # if not not isinstance(d, bool) and not self.unknowns[rel.decl()][i]:
                        if not isinstance(d, bool):
                            dp_no_bool.append(d)
                    dp_no_bool_dataset_n.add(tuple(dp_no_bool))
                
                for dp in dp_no_bool_dataset_p:
                    if dp in dp_no_bool_dataset_n:
                    # except for bool and unknowns, other vars are the same, no need for SVM to learn
                        self.logger.info(f'Rel: {rel.decl()} dp: {dp} conflict, no need for SVM to learn')
                        maps = (self.svm_name_to_expr_map, self.svm_name_to_str_map, self.svm_name_to_coeff_map)
                        return svm_calls, maps

                # a[:, ~np.all(a[1:] == a[:-1], axis=0)]
                pn = len(dp_no_bool_dataset_p)
                nn = len(dp_no_bool_dataset_n)
                for dp in dp_no_bool_dataset_p:
                    svm_str += '1'
                    for d in dp:
                        svm_str += ' ' + str(d)
                    svm_str += '\n'

                for dp in dp_no_bool_dataset_n:
                    svm_str += '0'
                    for d in dp:
                        svm_str += ' ' + str(d)
                    svm_str += '\n'

                f_svm = open(self.file_name+'.svm.data', 'w')
                f_svm.write(svm_str)
                f_svm.close()

                if self.parent.cand_counter % self.params['Verbosity']['PrintNewCandFreq'] == 0:
                    self.logger.debug(f'SVM data input:\n{svm_str}')

                cmd = self.svm_exec_path + \
                        " -c " + str(self.params['SVM']['SVMCParameter']) + \
                        " -t " + str(self.params['SVM']['SVMCoeffBound']) + \
                        " -a " + str(self.params['SVM']['SVMAHyperplane']) + \
                        " -v " + str(num_svm_vars) + \
                        " -p " + str(pn) + \
                        " -n " + str(nn) + \
                        " -g " + str(self.params['LC']) + \
                        " -f " + C5_rel_name + ' ' + self.file_name + '.svm.data' + ' 2>&1'

                self.logger.info(f'SVM cmd: {cmd}')

                p = os.popen(cmd, 'r')
                if p is None:
                    self.logger.error("popen failed!")
                    raise Exception("popen failed!")
                buf = p.read()
                p.close()
                self.logger.debug(f'SVM out buffer: {buf}')
                # f = open('tmp/svm_temp', 'w+')
                # f.write(buf)
                # f.close()
                if buf.find('Segmentation fault') != -1 or buf.find('Kill') != -1:
                    self.logger.error('SVM does not properly execute')
                    continue        
                svm_calls += 1

                f = open(self.file_name + '.attr', 'r')
                svm_out_lines = f.read().splitlines()
                f.close()
                self.logger.debug(f'SVM data output:\n{svm_out_lines}')

                svm_i = 0
                self.svm_name_to_coeff_map[C5_rel_name] = []
                # self.logger.debug(f'svm_name_to_coeff_map {C5_rel_name} purged')
                for line_num, line in enumerate(svm_out_lines):
                    if line == 'true' or line == 'false':
                        continue

                    coeff_args = []
                    expr_line = None
                    str_line = ''
                    thetas = line.split(' ')[1:]  # skip the first output of each line
                    i = 0
                    for j, arg in enumerate(args):
                        if z3.is_bool(arg):
                        # if z3.is_bool(arg) or self.unknowns[rel.decl()][j]:  # skip boolean/unknown variables in SVM learning
                            continue
                        
                        if i >= len(thetas):
                            raise IndexError(f'list index {i} out of range {len(thetas)} at iter {j}, \
                                               len(args):{len(args)},\nthetas:{thetas},\nargs:{args}')
                        theta = thetas[i]
                        
                        if int(theta) == 0:  # skip coeff = 0 cases
                            i += 1  # non-bool args
                            continue
                        
                        expr = int(theta) * arg
                        coeff_args.append(expr)
                        expr_line = expr if expr_line is None else expr_line + expr
                        str_line += '(' + theta + '*' + \
                                      C5_rel_name + '!V_' + str(j) + ')+'
                        i += 1
                    str_line = str_line[:-1]

                    if len(coeff_args) > 1:  # Non-octogon
                        name = C5_rel_name + '!SVM_' + str(svm_i)
                        self.svm_name_to_expr_map[name] = expr_line
                        self.svm_name_to_str_map[name] = str_line
                        self.svm_name_to_coeff_map[C5_rel_name].append(thetas)
                        self.logger.debug(
                            f"SVM inferred a hyperlane for rel {C5_rel_name}({rel.decl()}): {str(str_line)}")
                        svm_i += 1

        maps = (self.svm_name_to_expr_map, self.svm_name_to_str_map, self.svm_name_to_coeff_map)
        return svm_calls, maps