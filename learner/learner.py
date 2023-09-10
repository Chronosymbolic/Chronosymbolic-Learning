from operator import is_not, mod
from re import sub
import sys
import os
import time
import datetime
import logging
import z3
from collections import deque
from colorlog import ColoredFormatter
from utils.dt.dt import SklearnDT, C5DT
from utils.svm.svm import LibSVMLearner

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)

from ordered_set import OrderedSet
from utils.la_utils import *
from utils.dataset import Dataset
from horndb.horndb import *


class DataDrivenLearner:
    def __init__(self, db: HornClauseDb, params, ClassDT, log_path='log.txt', file_name_suffix=''):
        # hyperparams loading
        self.params = params

        self.logger_level = logging.DEBUG
        self.log_path = log_path

        # stat
        self.svm_calls = 0
        self.dt_calls = 0
        self.z3_calls = 0
        self.svm_time = 0
        self.dt_time = 0
        self.z3_time = 0
        self.eq_solver_time = 0
        self.init_phase_time = 0
        self.arg_num = 0
        self.cand_counter = 0
        self.cex_counter = 0
        self.aux_info = {}  # additional stats can be put here as strs

        # C5 and SVM binary
        if sys.platform == 'linux':
            self.svm_exec_path = 'utils/svm/libsvm/svm-invgen'
            # self.svm_exec_path = '/dev/shm/svm-invgen'
        elif sys.platform == 'darwin':
            self.svm_exec_path = 'utils/svm/libsvm/svm-invgen-macos'
        else:
            self.svm_exec_path = 'utils/svm/libsvm/svm-invgen'

        # init
        self.set_logger()
        self.solver = z3.Solver()
        # self.solver = z3.Then(z3.Tactic('simplify'), z3.Tactic('smt')).solver()
        self.eq_solver = z3.Then(
            # z3.Tactic('purify-arith'),  # will do (maybe incorrect) qe
            # z3.Tactic('simplify'),
            # z3.Tactic('sat-preprocess'),
            # z3.Tactic('solve-eqs'),  # lead to some wrong result
            # z3.Tactic('solver-subsumption'),  # propagate-ineqs does this
            z3.Tactic('propagate-ineqs'),
            z3.Tactic('simplify'),
            # z3.Tactic('skip')
            )  # expr simplifier
        z3.set_param(timeout=self.params['Z3_Global_Timeout'])
        self.solver.set(timeout=self.params['Z3_Solver_Timeout'])

        self.pos_data_set = Dataset(self.logger, self.params, 'positive')
        self.neg_data_set = Dataset(self.logger, self.params, 'negative')
        self.db = db
        self.db.rewrite()
        self.file_name = self.params['FILE_NAME'] + file_name_suffix  # avoid clash
        # put trivial rel/rules in front, rels: HornRelation
        self.rels = list(reversed(db.get_rels_list()))
        self.rules = list(reversed(db.get_rules()))
        self.facts = list(reversed(db.get_facts()))
        self.queries = list(reversed(self.db.get_queries()))
        self.cand_map = {}
        self.rel_to_c5_rel_map = {}
        self.c5_rel_to_rel_map = {}
        # self.arg_name_to_expr_map = {}
        self.svm_name_to_expr_map = {}
        self.svm_name_to_coeff_map = {}  # {svm_name: [coeff]}
        self.svm_name_to_str_map = {}  # for C5 "*.names" input
        self.decl_to_rel_map = {}
        self.unknowns = {}
        self.mod_nums = OrderedSet(self.params['MOD'])
        self.div_nums = OrderedSet(self.params['DIV'])
        if not os.path.exists('tmp'):
            os.makedirs('tmp')

        # information output
        self.logger.warning(f'Hyperparameters:\n{yaml.dump(self.params, default_flow_style=False)}')
        self.logger.warning(f'Rule number: {len(self.rules)}')
        self.logger.warning(f'Relation number: {len(self.rels)}')
        self.logger.warning(f'Horn Relations:\n{self.rels}')

        self.is_not_supported = False
        if len(self.rels) > self.params['RelationUpperBound']:
            self.is_not_supported = True
            self.logger.warning(f'RelationUpperBound exceeded')
            return

        # build map
        for i, rel in enumerate(self.rels):
            if rel.not_supported:  # if there is array arg
                self.is_not_supported = True
                self.logger.warning(f'Array arg found')
                return

            r_decl = rel.decl()
            self.arg_num += rel.num_args()
            self.c5_rel_to_rel_map['PRED_'+str(i)] = rel
            # keys must be decl type to prevent collision!
            self.rel_to_c5_rel_map[r_decl] = 'PRED_'+str(i)
            self.cand_map[r_decl] = Z3_FALSE  # init with False
            self.decl_to_rel_map[r_decl] = rel
        self.rel_decls = list(self.decl_to_rel_map.keys())
        # self.extract_unknown()

        self.db_str = str(self.db)
        if self.params['MODFind']:
            self.mod_nums = self.mod_nums.union(extract_mod_nums(self.db.get_smtlib_str()))
            self.logger.debug(f'Mod Features:\n{self.mod_nums}')
        if self.params['DIVFind']:
            self.div_nums = self.div_nums.union(extract_div_nums(self.db.get_smtlib_str()))
            self.logger.debug(f'Div Features:\n{self.div_nums}')
        
        self.dt = ClassDT(self)
        self.svm = LibSVMLearner(self)
        self.logger.warning(f'Var number: {self.arg_num}')
        self.logger.debug(f'C5 name to Relation name map:\n{self.c5_rel_to_rel_map}')
        self.logger.warning(f'Horn Rules:\n{self.db_str}')


    def set_logger(self):
        self.logger = logging.getLogger(self.log_path)
        # same name triggers the same logger object
        self.logger.setLevel(self.logger_level)

        if self.params['LOGGING']:
            # create a handler, write to log file
            # logging.FileHandler(self, filename, mode='a', encoding=None, delay=0)
            # A handler class which writes formatted logging records to disk files
            fh = logging.FileHandler(self.log_path, mode='w')
            fh.setLevel(self.logger_level)

            # create another handler, for stdout in terminal
            # A handler class which writes logging records to a stream
            sh = logging.StreamHandler()
            sh.setLevel(logging.INFO)

            # set formatter
            formatter = logging.Formatter(
                fmt='%(asctime)s - line:%(lineno)d - %(message)s',
                datefmt='%H:%M:%S',
                )
            s_frmt = ColoredFormatter(
                fmt='%(log_color)s%(asctime)s - line:%(lineno)d - %(message)s',
                datefmt='%H:%M:%S',
                )
            fh.setFormatter(formatter)
            sh.setFormatter(s_frmt)

            # add handler to logger
            self.logger.addHandler(fh)
            self.logger.addHandler(sh)
        else:
            self.logger.disabled = True
        self.logger.info(f'{self.__class__.__name__} - by Ray Luo')
        self.logger.info('Date: ' + str(datetime.date.today()))
        self.logger.info('========Information========')

    def set_db(self, db: HornClauseDb):
        self.db = db

    def solve_negated_rule(self, rule_body, rule_head, additional_constraint=None):
        """Solve negated rule to get cex"""
        debug = self.params['Verbosity']['PrintCstr']
        start_time = time.time()
        self.solver.reset()
        self.solver.add(rule_body)
        self.solver.add(z3.Not(rule_head))
        
        if additional_constraint is not None:
            self.solver.add(additional_constraint)
        # self.logger.info('Z3 called')
        if debug:
            self.logger.debug(f'Constraint: {self.solver}')
        res = self.solver.check()
        model = None
        if res == z3.sat:
            model = self.solver.model()

        self.z3_time += time.time() - start_time
        self.z3_calls += 1
        if debug:
            self.logger.debug(f'Res: {res}, Model: {model}, Time: {time.time()-start_time}s')
        if res == z3.unknown:
            raise RuntimeError('Z3 returns unknown (solve_negated_rule)')
        return res, model

    def get_def(self, rule: HornRule, rel=None):
        """Substitute rels in rule with expressions in self.cand_map
           rel: HornRelation"""
        if rel is None:  # substitute all rels
            body, head = substitute(rule, self.rel_decls, self.cand_map)
            return body, head
        r_decl = rel.decl()
        body, head = substitute(rule, [r_decl], {r_decl: self.cand_map[r_decl]})
        return body, head

    def get_rel_args(self, rel: HornRelation):
        return rel.args()

    def invalidate_queries(self):
        """forcing all the queries to false"""
        for q in self.queries:
            q_decl = list(q.used_rels())[0]
            self.cand_map[q_decl] = Z3_FALSE
            # self.logger.debug(f'{q_decl} invalidated (candidate set to False)')

    def cand_postprocessing(self, target=None):
        self.invalidate_queries()

    def extract_unknown(self):
        for r in self.rules:
            for b_app in r.body():  # body
                if b_app.decl() in self.rel_decls:
                    arg_unknw = []
                    for i in range(b_app.num_args()):
                        if is_unknown(b_app.arg(i)):
                            arg_unknw.append(True)
                        else:
                            arg_unknw.append(False)
                    if b_app.decl() not in self.unknowns.keys():
                        self.unknowns[b_app.decl()] = arg_unknw
                    else:  # rel appears multiple of times, True only when the arg is unknown every single time
                        self.unknowns[b_app.decl()] = [arg_unknw[i] and self.unknowns[b_app.decl()][i] for i in range(len(arg_unknw))]
            
            arg_unknw = []
            for i in range(r.head().num_args()):  # head
                if is_unknown(r.head().arg(i)):
                    arg_unknw.append(True)
                else:
                    arg_unknw.append(False)
            if r.head().decl() not in self.unknowns.keys():
                self.unknowns[r.head().decl()] = arg_unknw
            else:  # rel appears multiple of times, True only when the arg is unknown every single time
                self.unknowns[r.head().decl()] = [arg_unknw[i] and self.unknowns[r.head().decl()][i] for i in range(len(arg_unknw))]

    def C5_learn(self, target=None):
        if isinstance(self.dt, C5DT):
            self._C5_learn(target)
        else:
            self._sklearn_dt_learn(target)
        self.print_cand()

    def _C5_learn(self, target=None):
        """
        target is None or []: all rels
        """
        if target is not None and len(target) != 0:  # add a query as a padding stuff
            if len(target) == 1:
                queries = self.db.get_queries()
                if len(queries) > 0:
                    q_rel_decl = list(queries[0].used_rels())[0]
                    q_rel = self.decl_to_rel_map[q_rel_decl]
                    if q_rel not in target:
                        target.insert(0, q_rel)  # put in front
                    else:  # only one query in target
                        return
            else:
                for rel in target:
                    self._C5_learn([rel])
                return
        else:  # C5_learn all predicates
            for rel in self.rels:
                self._C5_learn([rel])
            return

        assert(len(target) == 2)
        # cases that no need for C5 leaning
        if self.pos_data_set.is_empty(target[1])\
             and self.neg_data_set.is_empty(target[1]):
             return
        elif self.pos_data_set.is_empty(target[1]):
            tar_rel_decl = target[1].decl()
            self.cand_map[tar_rel_decl] = Z3_FALSE
            self.logger.info(
                f'New Candidate for {self.rel_to_c5_rel_map[tar_rel_decl]}:\n   False (dataset all False)')
            self.cand_postprocessing(target)
            return
        elif self.neg_data_set.is_empty(target[1]):
            tar_rel_decl = target[1].decl()
            self.cand_map[tar_rel_decl] = Z3_TRUE
            self.logger.info(
                f'New Candidate for {self.rel_to_c5_rel_map[tar_rel_decl]}:\n   True (dataset all True)')
            self.cand_postprocessing(target)
            return

        start_time = time.time()
        cand = self.dt.learn(self.pos_data_set,
                             self.neg_data_set,
                             target)
        self.dt_calls += 1
        self.cand_map[target[1].decl()] = cand
        self.cand_postprocessing(target)

        # print(f'C5 DT expr for relation {target[1]}: {cand}')

        self.logger.debug(str(self.pos_data_set))
        self.logger.debug(str(self.neg_data_set))
        # print(f'C5 DT time: {time.time()-start_time}')
        self.dt_time += time.time() - start_time
        self.logger.debug(f'DT Calls: {self.dt_calls}, Total DT time: {self.dt_time}')
        return

    def _sklearn_dt_learn(self, target=None):
        if target is not None and len(target) != 0:  # add a query as a padding stuff
            if len(target) == 1:
                queries = self.db.get_queries()
                if len(queries) > 0:
                    q_rel_decl = list(queries[0].used_rels())[0]
                    q_rel = self.decl_to_rel_map[q_rel_decl]
                    if q_rel not in target:
                        target.insert(0, q_rel)  # put in front
                    else:  # only one query in target
                        return
            else:
                for rel in target:
                    self._sklearn_dt_learn([rel])
                return
        else:  # dt_learn all predicates
            for rel in self.rels:
                self._sklearn_dt_learn([rel])
            return

        assert(len(target) == 2)
        # cases that no need for dt leaning
        if self.pos_data_set.is_empty(target[1])\
             and self.neg_data_set.is_empty(target[1]):
             return
        elif self.pos_data_set.is_empty(target[1]):
            tar_rel_decl = target[1].decl()
            self.cand_map[tar_rel_decl] = Z3_FALSE
            self.logger.info(
                f'New Candidate for {self.rel_to_c5_rel_map[tar_rel_decl]}:\n   False (dataset all False)')
            self.cand_postprocessing(target)
            return
        elif self.neg_data_set.is_empty(target[1]):
            tar_rel_decl = target[1].decl()
            self.cand_map[tar_rel_decl] = Z3_TRUE
            self.logger.info(
                f'New Candidate for {self.rel_to_c5_rel_map[tar_rel_decl]}:\n   True (dataset all True)')
            self.cand_postprocessing(target)
            return

        start_time = time.time()
        # dt_learn(self.pos_data_set.get_dps(rel), self.neg_data_set.get_dps(rel))
        for rel in target:
            rel_name_svm = self.rel_to_c5_rel_map[rel.decl()]
            svm_exprs = [expr for svm_name, expr in self.svm_name_to_expr_map.items() \
                            if svm_name.split('!')[0] == rel_name_svm]  # get rel's svm feats
            svm_exprs_str = [expr for svm_name, expr in self.svm_name_to_str_map.items() \
                            if svm_name.split('!')[0] == rel_name_svm]
            svm_exprs_coeff = self.svm_name_to_coeff_map.get(rel_name_svm, [])
            dt_expr = self.dt.learn(svm_exprs,
                                    svm_exprs_str,
                                    svm_exprs_coeff,
                                    self.mod_nums,
                                    self.div_nums,
                                    self.pos_data_set.get_dps(rel),
                                    self.neg_data_set.get_dps(rel),
                                    rel,
                                    rel_name_svm
                                    )

            if dt_expr is not None:
                self.dt_calls += 1
                # print(f'Pos Data: {str(self.pos_data_set)}')
                # print(f'Neg Data: {str(self.neg_data_set)}')
                # print(f'CART DT expr for relation  {rel}: {dt_expr}')
                # print(f'CART DT time: {time.time()-start_time}')
                self.cand_map[rel.decl()] = dt_expr
            else:  # fail()
                self.cand_map[rel.decl()] = Z3_FALSE

        self.cand_postprocessing(target)
        self.dt_time += time.time() - start_time

    def print_cand(self):
        if self.cand_counter % self.params['Verbosity']['PrintNewCandFreq'] == 0:
            for rel in self.rel_decls:
                self.logger.info(
                    f'New Candidate for {rel}:\n   {self.cand_map[rel]}')
        self.cand_counter += 1

    def generate_postive_samples_from_fact(self, rule):
        """sample pos dp seeds from fact"""
        assert(rule.is_head_uninterp()
               )  # pos samples cannot be induced by a non-fact rule
        
        r_head = rule.head()
        r_head_hrel = self.decl_to_rel_map[r_head.decl()]

        r_cand_b, r_cand_h = self.get_def(rule)
        res, model = self.solve_negated_rule(r_cand_b, r_cand_h)
        if res == z3.unsat:
            return True, False

        if is_query_rel(r_head.decl(), self.db):  # fact and query simutaneously
            # and sat, that means True -> False, buggy
            return False, False

        dp = self.get_dp_from_model(r_head, model)

        self.pos_data_set.add_dp(r_head_hrel, dp)
        self.neg_data_set.del_dp(r_head_hrel, dp)
        if self.neg_data_set.size(r_head_hrel) >= self.params['SVM']['SVMFreqPos']:
            self.svm_learn([r_head_hrel])
        self.neg_data_set.clear(r_head_hrel)
        # self.neg_data_set.clear()
        run = self.sample_linear_horn_clause(r_head, dp)
        return run, True

    def sample_linear_horn_clause(self, head, dp: list):
        """
        initialize some data structures for sampling pos dp
        head: fapp
        """
        unrol_count = {}
        rel_to_pos_state_map = {}
        equations = []
        for i, d in enumerate(dp):
            var_i = head.arg(i)
            assert(isinstance(d, int) or isinstance(d, bool))
            equations.append(var_i == d)

        if len(equations) == 0:
            state_assignment = Z3_TRUE
        else:
            state_assignment = z3.And(equations) if len(
                equations) > 1 else equations[0]

        if head.decl() not in rel_to_pos_state_map.keys():
            rel_to_pos_state_map[head.decl()] = [state_assignment]
        else:
            rel_to_pos_state_map[head.decl()].append(state_assignment)

        if not self.find_available_rules(
            unrol_count,
            rel_to_pos_state_map,
            head,
            dp
        ):
            return False

        self.logger.debug('Sampled positive states in this round:')
        for k, v in rel_to_pos_state_map.items():
            self.logger.debug(f'Rel: {k}, DP: {v}')
        return True

    def find_available_rules(self, unrol_count, rel_to_pos_state_map, rel, dp):
        """
        rel is from head (fapp)
        here we check if it matches one rel in body (only linear CHC supported)
        """
        for rule in self.rules:
            if rule in unrol_count.keys() and unrol_count[rule] >= self.params['RuleSampleLen']:
                continue

            if not rule.is_linear():
                self.logger.debug(
                    'Sampling positive dp by unwinding is not supported for non-linear CHCs')
                continue

            r_body_preds = rule.body_preds()
            if len(r_body_preds) == 0:
                continue
            assert(len(r_body_preds) == 1)
            if r_body_preds[0].decl() == rel.decl():
                equations = []
                for i, d in enumerate(dp):
                    var_i = r_body_preds[0].arg(i)
                    assert(isinstance(d, int) or isinstance(d, bool))
                    equations.append(var_i == d)

                if len(equations) == 0:
                    state_assignment = Z3_TRUE
                else:
                    state_assignment = z3.And(equations) if len(
                        equations) > 1 else equations[0]

                if not self.get_rule_head_state(
                    unrol_count,
                    rel_to_pos_state_map,
                    rule,
                    state_assignment
                ):
                    return False

        return True

    def get_rule_head_state(self, unrol_count, rel_to_pos_state_map, rule, state_assignment):
        """unroll the rule, get state assignment of a given rule's head"""
        start_time = time.time()
        self.solver.reset()
        self.solver.add(state_assignment)
        body_sub = rule.body_cstr()
        self.solver.add(z3.And(body_sub))
        # substitude unknown predicate with True, add other body constraints
        # p(x, y) => True and x=.., y=..
        # self.logger.info('Z3 called')  # this is called too many times
        res = self.solver.check()
        self.z3_time += time.time() - start_time
        self.z3_calls += 1

        iter = 0
        while res == z3.sat:
            r_head = rule.head()
            if is_query_rel(r_head.decl(), self.db):
            # if r_head.num_args() == 0:  # True -> False, original LinArb implementation
                return False

            model = self.solver.model()
            equations = []
            n_eq = []
            dp = []
            for i in range(r_head.num_args()):
                var_i = r_head.arg(i)
                value_i = model.eval(var_i)
                # assert(z3.is_int_value(value_i) or z3.is_bool(value_i))

                if z3.is_bool(value_i) and (z3.is_true(value_i) or z3.is_false(value_i)):
                    value_i = True if z3.is_true(value_i) else False
                elif is_uncertain(value_i):  # uncertain value
                    self.logger.debug(f'Uncertain Value: {value_i}')
                    if z3.is_bool(value_i):
                        value_i = False  # specify a random value
                    else:
                        value_i = 0  # specify a random value
                elif abs(value_i.as_long()) >= self.params['OverflowLimit']:
                    self.logger.warning(f'Overflow Value: {value_i}')
                    # value_i = 0  # specify a random value
                    raise RuntimeError(f'Overflow Value: {value_i}')
                else:
                    assert(z3.is_int_value(value_i))
                    value_i = value_i.as_long()
                
                equations.append(var_i == value_i)
                n_eq.append(var_i != value_i)
                dp.append(value_i)
            
            if len(equations) == 0:
                state_assignment_head = Z3_TRUE
            else:
                state_assignment_head = z3.And(equations) if len(
                    equations) > 1 else equations[0]

            r_head_hrel = self.decl_to_rel_map[r_head.decl()]

            is_not_duplicate = self.pos_data_set.add_dp(r_head_hrel, dp)
            self.neg_data_set.del_dp(r_head_hrel, dp)
            self.neg_data_set.clear(r_head_hrel)
            # self.neg_data_set.clear()  # better?


            if is_not_duplicate:
                if r_head.decl() not in rel_to_pos_state_map.keys():
                    rel_to_pos_state_map[r_head.decl()] = [state_assignment_head]
                else:
                    rel_to_pos_state_map[r_head.decl()].append(
                        state_assignment_head)

                if rule not in unrol_count.keys():
                    unrol_count[rule] = 1
                else:
                    unrol_count[rule] += 1

                if not self.find_available_rules(
                    unrol_count,
                    rel_to_pos_state_map,
                    r_head,
                    dp
                ):
                    return False

                unrol_count[rule] -= 1

            iter += 1
            if iter >= self.params['RuleSampleWidth']:
                break

            if len(n_eq) == 0:
                break
            not_again = z3.Or(n_eq) if len(n_eq) > 1 else n_eq[0]

            start_time = time.time()
            self.solver.add(not_again)
            # self.logger.info('Z3 called')
            res = self.solver.check()
            self.z3_time += time.time() - start_time
            self.z3_calls += 1
        return True

    def svm_learn(self, target=None):
        if not self.params['SVM']['EnableSVM']:
            return
        start_time = time.time()
        # if target is None:
        #     self.svm_name_to_expr_map.clear()
        #     self.svm_name_to_str_map.clear()
        #     self.svm_name_to_coeff_map.clear()
        # else:  # delete all keys that is related to rels in target 
        #     rel_names = [self.rel_to_c5_rel_map[t.decl()] for t in target]
        #     ks = list(self.svm_name_to_expr_map.keys())
        #     for rel_name in rel_names:
        #         self.svm_name_to_coeff_map.pop(rel_name, 0)
        #         for k in ks:
        #             if rel_name in k:
        #                 # self.logger.debug(f'Attr {k} for rel {rel_name} purged')
        #                 self.svm_name_to_expr_map.pop(k, 0)  # if pop fails, default val = 0
        #                 self.svm_name_to_str_map.pop(k, 0)

        # for rel in self.rels:
        #     if target is None or rel in target:
        #         args = self.get_rel_args(rel)
        #         num_svm_vars = 0
        #         for i, arg in enumerate(args):
        #             # if z3.is_bool(arg) or self.unknowns[rel.decl()][i]:
        #             if z3.is_bool(arg):
        #                 continue
        #             num_svm_vars += 1

        #         if len(args) == 0:  # skip trivial rels
        #             continue
        #         if num_svm_vars >= 69:
        #             self.logger.error('Too many vars, SVM does not support')
        #             continue

        #         svm_str = ''
        #         pn = nn = 0
        #         C5_rel_name = self.rel_to_c5_rel_map[rel.decl()]
        #         dp_no_bool_dataset_p = OrderedSet()
        #         dp_no_bool_dataset_n = OrderedSet()
        #         if self.pos_data_set.is_empty(rel) or self.neg_data_set.is_empty(rel):
        #             # only pos/neg dps are inputted
        #             continue

        #         for dp in self.pos_data_set.get_dps(rel):
        #             dp_no_bool = []
        #             for i, d in enumerate(dp):
        #                 # if not isinstance(d, bool) and not self.unknowns[rel.decl()][i]:
        #                 if not isinstance(d, bool):
        #                     dp_no_bool.append(d)
        #             dp_no_bool_dataset_p.add(tuple(dp_no_bool))

        #         for dp in self.neg_data_set.get_dps(rel):
        #             dp_no_bool = []
        #             for i, d in enumerate(dp):
        #                 # if not not isinstance(d, bool) and not self.unknowns[rel.decl()][i]:
        #                 if not isinstance(d, bool):
        #                     dp_no_bool.append(d)
        #             dp_no_bool_dataset_n.add(tuple(dp_no_bool))
                
        #         for dp in dp_no_bool_dataset_p:
        #             if dp in dp_no_bool_dataset_n:
        #             # except for bool and unknowns, other vars are the same, no need for SVM to learn
        #                 self.logger.info(f'Rel: {rel.decl()} dp: {dp} conflict, no need for SVM to learn')
        #                 return

        #         # a[:, ~np.all(a[1:] == a[:-1], axis=0)]
        #         pn = len(dp_no_bool_dataset_p)
        #         nn = len(dp_no_bool_dataset_n)
        #         for dp in dp_no_bool_dataset_p:
        #             svm_str += '1'
        #             for d in dp:
        #                 svm_str += ' ' + str(d)
        #             svm_str += '\n'

        #         for dp in dp_no_bool_dataset_n:
        #             svm_str += '0'
        #             for d in dp:
        #                 svm_str += ' ' + str(d)
        #             svm_str += '\n'

        #         f_svm = open(self.file_name+'.svm.data', 'w')
        #         f_svm.write(svm_str)
        #         f_svm.close()

        #         if self.cand_counter % self.params['Verbosity']['PrintNewCandFreq'] == 0:
        #             self.logger.debug(f'SVM data input:\n{svm_str}')

        #         cmd = self.svm_exec_path + \
        #                 " -c " + str(self.params['SVM']['SVMCParameter']) + \
        #                 " -t " + str(self.params['SVM']['SVMCoeffBound']) + \
        #                 " -a " + str(self.params['SVM']['SVMAHyperplane']) + \
        #                 " -v " + str(num_svm_vars) + \
        #                 " -p " + str(pn) + \
        #                 " -n " + str(nn) + \
        #                 " -g " + str(self.params['LC']) + \
        #                 " -f " + C5_rel_name + ' ' + self.file_name + '.svm.data' + ' 2>&1'

        #         self.logger.info(f'SVM cmd: {cmd}')

        #         p = os.popen(cmd, 'r')
        #         if p is None:
        #             self.logger.error("popen failed!")
        #             raise Exception("popen failed!")
        #         buf = p.read()
        #         p.close()
        #         self.logger.debug(f'SVM out buffer: {buf}')
        #         # f = open('tmp/svm_temp', 'w+')
        #         # f.write(buf)
        #         # f.close()
        #         if buf.find('Segmentation fault') != -1 or buf.find('Kill') != -1:
        #             self.logger.error('SVM does not properly execute')
        #             continue        
        #         self.svm_calls += 1

        #         f = open(self.file_name + '.attr', 'r')
        #         svm_out_lines = f.read().splitlines()
        #         f.close()
        #         self.logger.debug(f'SVM data output:\n{svm_out_lines}')

        #         svm_i = 0
        #         self.svm_name_to_coeff_map[C5_rel_name] = []
        #         # self.logger.debug(f'svm_name_to_coeff_map {C5_rel_name} purged')
        #         for line_num, line in enumerate(svm_out_lines):
        #             if line == 'true' or line == 'false':
        #                 continue

        #             coeff_args = []
        #             expr_line = None
        #             str_line = ''
        #             thetas = line.split(' ')[1:]  # skip the first output of each line
        #             i = 0
        #             for j, arg in enumerate(args):
        #                 if z3.is_bool(arg):
        #                 # if z3.is_bool(arg) or self.unknowns[rel.decl()][j]:  # skip boolean/unknown variables in SVM learning
        #                     continue
                        
        #                 if i >= len(thetas):
        #                     raise IndexError(f'list index {i} out of range {len(thetas)} at iter {j}, \
        #                                        len(args):{len(args)},\nthetas:{thetas},\nargs:{args}')
        #                 theta = thetas[i]
                        
        #                 if int(theta) == 0:  # skip coeff = 0 cases
        #                     i += 1  # non-bool args
        #                     continue
                        
        #                 expr = int(theta) * arg
        #                 coeff_args.append(expr)
        #                 expr_line = expr if expr_line is None else expr_line + expr
        #                 str_line += '(' + theta + '*' + \
        #                               C5_rel_name + '!V_' + str(j) + ')+'
        #                 i += 1
        #             str_line = str_line[:-1]

        #             if len(coeff_args) > 1:  # Non-octogon
        #                 name = C5_rel_name + '!SVM_' + str(svm_i)
        #                 self.svm_name_to_expr_map[name] = expr_line
        #                 self.svm_name_to_str_map[name] = str_line
        #                 self.svm_name_to_coeff_map[C5_rel_name].append(thetas)
        #                 self.logger.debug(
        #                     f"SVM inferred a hyperlane for rel {C5_rel_name}({rel.decl()}): {str(str_line)}")
        #                 svm_i += 1

        calls, maps = self.svm.learn(self.pos_data_set, self.neg_data_set, target)
        self.svm_calls += calls
        self.svm_name_to_expr_map, self.svm_name_to_str_map, self.svm_name_to_coeff_map = maps

        self.svm_time += time.time() - start_time
        # self.logger.debug(str(self.pos_data_set))
        # self.logger.debug(str(self.neg_data_set))
        self.logger.debug(f'SVM Calls: {self.svm_calls}, Total SVM time: {self.svm_time}')

    def add_rule_with_given_head_in_body(self, work_list, rule):
        """
        Given a rule head, extract all rules using it in body (excluding itself),
        then add all such rules to the beginning of worklist
        """
        desired_head_decl = rule.head().decl()
        for r in self.rules:
            if r.get_idx() == rule.get_idx():
                continue
            for body_app in r.body():
                if body_app.decl() == desired_head_decl:
                    work_list.append(r)
                    break

    def add_rule_with_given_body_in_head(self, work_list, rule):
        """
        Given a rule body, extract all rules using it in head (excluding itself),
        then add all such rules to the beginning of worklist
        """
        desired_body_decl = []
        for body_app in rule.body():
            if body_app.decl() not in self.rel_decls or body_app.num_args() <= 0:
                continue
            desired_body_decl.append(body_app.decl())

        for r in self.rules:
            if r.get_idx() == rule.get_idx():
                continue
            if rule.head().decl() in desired_body_decl:
                work_list.append(r)

    def solve_constraints(self):
        """
        Return 2 bool vars: is_safe, is_changed
        """
        is_changed = False
        work_list = self.rules[:]
        self.logger.info(
            "========== Constraint Solving of Horn Clauses ===========")
        while work_list:
            self.logger.debug(f'Work list size: {len(work_list)}')
            r = work_list.pop()
            self.logger.info(f'VERIFY Horn Rule Index {r.get_idx()}')

            upd = False
            pos_upd = False
            counter = 0
            r_body = r.body()
            r_head = r.head()
            r_head_hrel = self.decl_to_rel_map[r_head.decl()]

            if r.is_fact():
                self.logger.debug('This rule is a FACT')
                if not r.is_head_uninterp():
                    self.logger.debug('This FACT rule is trivial')
                    res, model = self.db.find_cex([r])
                    if res != z3.unsat:
                        self.logger.warning('Bug detected')
                        return False, is_changed
                else:
                    self.logger.debug(
                        'Generate Initial Program State Samples From Fact')
                    while True:
                        run, upd = self.generate_postive_samples_from_fact(r)
                        if not run:
                            self.logger.warning('Bug detected')
                            return False, is_changed
                        if not upd:
                            break
                        # target = [r_head_hrel]
                        is_changed = True
                        pos_upd = True
                        self.C5_learn()

                    # Extend work list as we just go through a strengthening loop
                    self.add_rule_with_given_head_in_body(work_list, r)

            else:  # not fact
                while True:
                    counter += 1
                    upd = False
                    # solve the negated rule
                    self.logger.info(f'Rule Index {r.get_idx()} Verification Round {counter}')
                    r_cand_b, r_cand_h = self.get_def(r)
                    res, model = self.solve_negated_rule(r_cand_b, r_cand_h)

                    if res == z3.sat:
                        upd = True
                        is_changed = True

                        # print the cex
                        self.print_cex(r, model)

                        # collect datapoints
                        dps = []  # [(rel_decl, dp), ...]
                        for body_app in r_body:
                            if body_app.decl() not in self.rel_decls or body_app.num_args() <= 0:
                                continue
                            dp = self.get_dp_from_model(body_app, model)
                            dps.append((body_app.decl(), dp))
                        
                        # if dps are all pos dp, add a new pos dp for head, otherwise add neg dps
                        all_pos = True
                        for rel, dp in dps:
                            if self.pos_data_set.find_dp(self.decl_to_rel_map[rel], dp) or self.match_fact(rel, dp):
                                continue
                            all_pos = False
                            break
                        
                        if all_pos:
                            if r_head.num_args() <= 0:  # is a query, True -> False
                                self.logger.warning('Bug detected')
                                return False, is_changed
                            
                            dp = self.get_dp_from_model(r_head, model)
                            is_not_dup = self.pos_data_set.add_dp(r_head_hrel, dp)
                            if not is_not_dup:
                                self.logger.error('Duplicate pos data points should be impossible')
                                raise RuntimeError('Duplicate pos data points should be impossible')
                            self.neg_data_set.del_dp(r_head_hrel, dp)
                            self.logger.debug(f'Got Pos DP {r_head}: {dp} from implication')

                            if self.neg_data_set.size(r_head_hrel) >= self.params['SVM']['SVMFreqPos']:
                                self.svm_learn([r_head_hrel])

                            self.neg_data_set.clear(r_head_hrel)
                            # --- clear neg dps for body apps as well ---
                            if self.params['ClearBodyAppsDP']:
                                for body_app in r_body:  
                                    if body_app.decl() not in self.rel_decls or body_app.num_args() <= 0:
                                        continue
                                    self.neg_data_set.clear(self.decl_to_rel_map[body_app.decl()])

                            # sample more pos dps using the seed we got just now
                            if not self.sample_linear_horn_clause(r_head, dp):
                                return False, is_changed
                            pos_upd = True
                        else:
                            # collect body dps as neg dps
                            neg_dps = OrderedSet()  # avoid duplicate in the same round
                            for rel, dp in dps:
                                hrel = self.decl_to_rel_map[rel]
                                if self.pos_data_set.find_dp(hrel, dp) or self.match_fact(rel, dp):
                                    continue
                                neg_dp = (rel, tuple(dp))
                                neg_dps.add(neg_dp)
                            
                            for rel, dp in neg_dps:
                                hrel = self.decl_to_rel_map[rel]
                                is_not_dup = self.neg_data_set.add_dp(hrel, dp)
                                if not is_not_dup:
                                    self.logger.error('Duplicate neg data points should be impossible')
                                    raise RuntimeError('Duplicate neg data points should be impossible')

                                if self.neg_data_set.size(hrel) >= self.params['SVM']['SVMFreqNeg'] \
                                    and self.neg_data_set.size(hrel) % self.params['SVM']['SVMFreqNeg'] == 0:
                                    self.svm_learn([hrel])
                    else:
                        self.logger.debug('UNSAT, This rule is passed')

                    if upd:
                        self.C5_learn()
                        if self.params['ValIterMode']:
                            # only one iter of updating a rule each time
                            counter += 1
                            break
                    else:
                        break

                if counter > 1:
                    if pos_upd:
                        self.add_rule_with_given_head_in_body(work_list, r)
                    else:
                        self.add_rule_with_given_body_in_head(work_list, r)

        self.logger.info('==================================')
        return True, is_changed

    def get_dp_from_model(self, fapp, model, check_uncrt=True, check_ovfl=True):
        """Return a dp given an fapp and a model"""
        dp = []
        for i in range(fapp.num_args()):
            arg_i = fapp.arg(i)
            arg_i_val = model.eval(arg_i)

            if z3.is_bool(arg_i_val) and (z3.is_true(arg_i_val) or z3.is_false(arg_i_val)):  # Boolean value
                arg_i_val = True if z3.is_true(arg_i_val) else False 
            elif check_uncrt and is_uncertain(arg_i_val):  # uncertain value
                self.logger.debug(f'Uncertain Value: {arg_i_val}')
                if z3.is_bool(arg_i_val):
                    arg_i_val = False  # specify a random value
                else:
                    arg_i_val = 0  # specify a random value
            elif check_ovfl and abs(arg_i_val.as_long()) >= self.params['OverflowLimit']:
                self.logger.warning(f'Overflow Value: {arg_i_val}')
                # arg_i_val = 0  # specify a random value
                raise RuntimeError(f'Overflow Value: {arg_i_val}')
            else:
                assert(z3.is_int_value(arg_i_val))
                arg_i_val = arg_i_val.as_long()

            dp.append(arg_i_val)
        return dp

    def print_cex(self, rule, model):
        """print counterexample given a rule and its model"""
        if self.cex_counter % self.params['Verbosity']['PrintCex']:
            self.cex_counter += 1
            return
        self.cex_counter += 1
        r_head = rule.head()
        r_body = rule.body()
        cex_str = ''

        for body_app in r_body:  # print body
            if body_app.decl() not in self.rel_decls or body_app.num_args() <= 0:
                continue
            cex_str += f'{body_app.decl().name()}('
            for i in range(body_app.num_args()):
                arg_i = body_app.arg(i)
                arg_i_val = model.eval(arg_i)
                cex_str += f'{arg_i_val}, '
            cex_str += '); '
        cex_str += f'-> {r_head.decl().name()}('

        for i in range(r_head.num_args()):  # print head
            arg_i = r_head.arg(i)
            arg_i_val = model.eval(arg_i)
            cex_str += f'{arg_i_val}, '
        cex_str += ') '
        self.logger.info(f'SAT, CEX: {cex_str}')
        return

    def match_fact(self, rel: HornRelation, dp):
        """
        Return True when a dp corresponds to a fact
        This could help accelerate collecting positive dps
        Different from the original code base of LinArb
        """
        if not self.params['EnableMatchFact']:
            return False

        for fact in self.facts:
            head = fact.head()
            self.solver.reset()
            if head.decl() == rel:
                for i in range(head.num_args()):
                    arg_i = head.arg(i)
                    self.solver.add(arg_i == dp[i])
                self.solver.add(fact.body())

                start_time = time.time()
                # self.logger.info('Z3 called')
                res = self.solver.check()
                self.z3_time  += time.time() - start_time
                self.z3_calls += 1

                if res == z3.sat:
                    self.logger.debug(f'DP {dp} matched fact {fact}')
                    return True
        return False
