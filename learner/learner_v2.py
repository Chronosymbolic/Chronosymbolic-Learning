from horndb.horndb import HornClauseDb, HornRelation, HornRule
from learner.learner import DataDrivenLearner
import z3
import time
from ordered_set import OrderedSet
from utils.la_utils import *
from utils.dataset import *


class DataDrivenLearner_v2(DataDrivenLearner):
    def __init__(self, db: HornClauseDb, params, ClassDT, log_path='log.txt', file_name_suffix=''):
        super(DataDrivenLearner_v2, self).__init__(db, params, ClassDT, log_path, file_name_suffix)
        self.neg_data_set = Dataset_v2(self.logger, self.params, 'negative')
        self.query_rels = find_query_rel(db)  # list[fdecl]
        self.fact_rels = find_fact_rel(db)  # list[fdecl]
        
        for r in self.rules:  # expand fact rules
            if self.is_fact_rule(r) and r not in self.db.get_facts():
                self.facts.append(r)
            elif self.is_query_rel(r.head().decl()) and r not in self.db.get_queries():
                self.queries.append(r)

        self.logger.warning(f'Facts: {self.facts}\nNum: {len(self.facts)}')
        self.logger.warning(f'Fact rels: {self.fact_rels}\nNum: {len(self.fact_rels)}')
        self.logger.warning(f'Query rels: {self.query_rels}\nNum: {len(self.query_rels)}')
        self.logger.warning(f'Queries: {self.queries}\nNum: {len(self.queries)}')

    def is_query_rel(self, rel_decl):
        if rel_decl in self.query_rels:
            return True
        return False

    def is_fact_rule(self, r):
        """
        If the uninterps in body are fixed to True, then r is also a fact
        """
        for b in r.body():
            if r.is_uninterp(b.decl()) and b.decl() not in self.fact_rels:
                return False
        return True

    def match_fact(self, rel, dp):
        """
        rel: fdecl
        Return True when a dp corresponds to a fact
        This could help accelerate collecting positive dps
        """
        if not self.params['EnableMatchFact']:
            return False

        for fact in self.facts:
            r_cand_b, _ = self.get_def(fact)
            head = fact.head()
            self.solver.reset()
            if head.decl() == rel:
                for i in range(head.num_args()):
                    arg_i = head.arg(i)
                    self.solver.add(arg_i == dp[i])
                self.solver.add(r_cand_b)

                start_time = time.time()
                # self.logger.info('Z3 called')
                res = self.solver.check()
                self.z3_time  += time.time() - start_time
                self.z3_calls += 1

                if res == z3.sat:
                    self.logger.debug(f'DP {dp} matched fact {fact}')
                    return True
        return False

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

        if self.is_query_rel(r_head.decl()):  # fact and query simutaneously
            # and sat, that means True -> False, buggy
            return False, False

        dp = self.get_dp_from_model(r_head, model)

        self.pos_data_set.add_dp(r_head_hrel, dp)
        if self.neg_data_set.find_dp(r_head_hrel, dp, exclude_tentative=True):
            return False, False
        self.neg_data_set.del_dp(r_head_hrel, dp)
        if self.neg_data_set.size(r_head_hrel) >= self.params['SVM']['SVMFreqPos']:
            self.svm_learn([r_head_hrel])
        self.neg_data_set.clear(r_head_hrel)
        
        run = self.sample_linear_horn_clause(r_head, dp)
        return run, True

    def sample_linear_horn_clause(self, head, dp: list):
        """
        initialize some data structures for sampling pos dp
        head: fapp / HornRelation
        """
        unrol_count = {}
        rel_to_pos_state_map = {}
        equations = []
        for i, d in enumerate(dp):
            var_i = head.arg(i) if not isinstance(head, HornRelation) else self.get_rel_args(head)[i]
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
        rel is from head (fapp / HornRelation)
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
                    var_i = r_body_preds[0].arg(i) if not isinstance(r_body_preds, HornRelation) else self.get_rel_args(r_body_preds)[i]
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
        body_cstr = rule.body_cstr()
        self.solver.add(z3.And(body_cstr))
        # substitude unknown predicate with True, add other body constraints
        # p(x, y) = True and x=.., y=..
        # self.logger.info('Z3 called')
        res = self.solver.check()
        self.z3_time += time.time() - start_time
        self.z3_calls += 1

        iter = 0
        while res == z3.sat:
            r_head = rule.head()
            if self.is_query_rel(r_head.decl()):
            # if r_head.num_args() == 0:  # True -> False, original LinArb implementation
                return False

            model = self.solver.model()
            equations = []
            n_eq = []
            dp = []
            for i in range(r_head.num_args()):
                var_i = r_head.arg(i) if not isinstance(r_head, HornRelation) else self.get_rel_args(r_head)[i]
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
            if self.neg_data_set.find_dp(r_head_hrel, dp, exclude_tentative=True):
                return False
            self.neg_data_set.clear(r_head_hrel)

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

    def generate_negative_samples_from_query(self, rule):
        r_head = rule.head()
        r_body = rule.body()
        assert(self.is_query_rel(r_head.decl())
               )  # neg samples cannot be induced by a non-query rule

        r_cand_b, r_cand_h = self.get_def(rule)
        
        res, model = self.solve_negated_rule(r_cand_b, r_cand_h)
        if res == z3.unsat:  # no cex
            return True, False
        
        if rule.is_fact():  # fact and query simutaneously
            # and sat, that means True -> False, buggy
            return False, False
        
        for body_app in r_body:  # TODO: non-lin not correct
            if body_app.decl() not in self.rel_decls or body_app.num_args() <= 0:
                continue
            dp = self.get_dp_from_model(body_app, model)
            body_hrel = self.decl_to_rel_map[body_app.decl()]
            self.neg_data_set.add_dp(body_hrel, dp)
            if self.pos_data_set.find_dp(body_hrel, dp):
                return False, True

            if self.neg_data_set.size(body_hrel) >= self.params['SVM']['SVMFreqPos']:
                self.svm_learn([body_hrel])

            if not self.sample_linear_horn_clause_backward(body_app, dp):
                return False, True
        return True, True
    
    def sample_linear_horn_clause_backward(self, body_app, dp: list):
        """
        initialize some data structures for sampling neg dp
        body_app: fapp / HornRelation
        """
        unrol_count = {}
        rel_to_neg_state_map = {}
        equations = []
        for i, d in enumerate(dp):
            var_i = body_app.arg(i) if not isinstance(body_app, HornRelation) else self.get_rel_args(body_app)[i]
            assert(isinstance(d, int) or isinstance(d, bool))
            equations.append(var_i == d)

        if len(equations) == 0:
            state_assignment = Z3_FALSE
        else:
            state_assignment = z3.And(equations) if len(
                equations) > 1 else equations[0]

        if body_app.decl() not in rel_to_neg_state_map.keys():
            rel_to_neg_state_map[body_app.decl()] = [state_assignment]
        else:
            rel_to_neg_state_map[body_app.decl()].append(state_assignment)

        if not self.find_available_rules_backward(
            unrol_count,
            rel_to_neg_state_map,
            body_app,
            dp
        ):
            return False

        self.logger.debug('Sampled negative states in this round:')
        for k, v in rel_to_neg_state_map.items():
            self.logger.debug(f'Rel: {k}, DP: {v}')
        return True

    def find_available_rules_backward(self, unrol_count, rel_to_neg_state_map, rel, dp):
        """
        rel is from body (fapp / HornRelation)
        here we check if it matches one rel in head (only linear CHC supported)
        """
        for rule in self.rules:
            if rule in unrol_count.keys() and unrol_count[rule] >= self.params['RuleSampleLenNeg']:
                continue

            if not rule.is_linear():
                self.logger.debug(
                    'Sampling negative dp by unwinding is not supported for non-linear CHCs')
                continue

            r_head = rule.head()
            if r_head.decl() == rel.decl():
                equations = []
                for i, d in enumerate(dp):
                    var_i = r_head.arg(i) if not isinstance(r_head, HornRelation) else self.get_rel_args(r_head)[i]
                    assert(isinstance(d, int) or isinstance(d, bool))
                    equations.append(var_i == d)

                if len(equations) == 0:
                    state_assignment = Z3_FALSE
                else:
                    state_assignment = z3.And(equations) if len(
                        equations) > 1 else equations[0]

                if not self.get_rule_body_state(
                    unrol_count,
                    rel_to_neg_state_map,
                    rule,
                    state_assignment
                ):
                    return False

        return True

    def get_rule_body_state(self, unrol_count, rel_to_neg_state_map, rule, state_assignment):
        """unroll the rule, get state assignment of a given rule's head"""
        start_time = time.time()
        self.solver.reset()
        self.solver.add(state_assignment)
        r_body_preds = rule.body_preds()
        body_cstr = rule.body_cstr()
        self.solver.add(z3.And(body_cstr))
        # substitude unknown predicate with True, add other body constraints
        # head(x, y) = False, and x=.., y=.., p(x, y) and true -> false, forcing p to be false
        # self.logger.info('Z3 called')  # this is called too many times
        res = self.solver.check()
        self.z3_time += time.time() - start_time
        self.z3_calls += 1

        iter = 0
        while res == z3.sat:
            r_body_preds = rule.body_preds()
            if rule.is_fact():
            # True -> False
                return False

            model = self.solver.model()
            n_eq = []
            dps = []
            state_assignment_body = dict()
            for r_body_app in r_body_preds:
                equations = []
                dp = []
                r_body_decl = r_body_app.decl()
                for i in range(r_body_app.num_args()):
                    var_i = r_body_app.arg(i) if not isinstance(r_body_app, HornRelation) else self.get_rel_args(r_body_app)[i]
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
            
                dps.append((r_body_decl, dp))
                if len(equations) == 0:
                    state_assignment_body[r_body_decl] = Z3_FALSE
                else:
                    state_assignment_body[r_body_decl] = z3.And(equations) if len(
                        equations) > 1 else equations[0]

            for rel, dp in dps:
                r_body_hrel = self.decl_to_rel_map[rel]

                is_not_duplicate = self.neg_data_set.add_dp(r_body_hrel, dp)
                if self.pos_data_set.find_dp(r_body_hrel, dp):
                    return False

                if is_not_duplicate:
                    if rel not in rel_to_neg_state_map.keys():
                        rel_to_neg_state_map[rel] = [state_assignment_body[rel]]
                    else:
                        rel_to_neg_state_map[rel].append(
                            state_assignment_body[rel])

                    if rule not in unrol_count.keys():
                        unrol_count[rule] = 1
                    else:
                        unrol_count[rule] += 1

                    if not self.find_available_rules_backward(
                        unrol_count,
                        rel_to_neg_state_map,
                        r_body_hrel,
                        dp
                    ):
                        return False

                    unrol_count[rule] -= 1

            iter += 1
            if iter >= self.params['RuleSampleWidthNeg']:
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

    def solve_constraints(self):
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
                        f'Generate Positive State Samples From Fact Rule Index {r.get_idx()}')
                    i = 0
                    while True:
                        i += 1
                        self.logger.debug(
                            f'Generate Positive State Samples Iteration {i}')
                        run, upd = self.generate_postive_samples_from_fact(r)
                        if not run:
                            self.logger.warning('Bug detected')
                            return False, is_changed
                        if not upd or i >= self.params['FactSampleMaxRound']:
                            break
                        # target = [r_head_hrel]
                        is_changed = True
                        pos_upd = True
                        self.C5_learn()

                    # Extend work list as we just go through a strengthening loop
                    self.add_rule_with_given_head_in_body(work_list, r)

            elif self.is_query_rel(r_head.decl()):
                self.logger.debug('This rule is a Query')
                if r.is_fact():
                    self.logger.debug('This Query rule is trivial')
                    res, model = self.db.find_cex([r])
                    if res != z3.unsat:
                        self.logger.warning('Bug detected')
                        return False, is_changed
                else:
                    self.logger.debug(
                        f'Generate Negative State Samples From Query Rule Index {r.get_idx()}')
                    i = 0
                    while True:
                        i += 1
                        self.logger.debug(
                            f'Generate Negative State Samples Iteration {i}')
                        run, upd = self.generate_negative_samples_from_query(r)
                        if not run:
                            self.logger.warning('Bug detected')
                            return False, is_changed
                        if not upd or i >= self.params['QuerySampleMaxRound']:
                            break
                        # target = [r_head_hrel]
                        is_changed = True
                        pos_upd = True
                        self.C5_learn()

                    # Extend work list as we just go through a strengthening loop
                    self.add_rule_with_given_body_in_head(work_list, r)

            else:  # not fact or query
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
                        
                        # if body dps are all pos dp, add a new pos dp for head
                        all_pos = True
                        for rel, dp in dps:
                            if self.pos_data_set.find_dp(self.decl_to_rel_map[rel], dp) or self.match_fact(rel, dp):
                                continue
                            all_pos = False
                            break
                        
                        # if head dp is true neg dp, add new neg dps for body
                        head_neg = False
                        head_dp = self.get_dp_from_model(r_head, model)
                        if self.neg_data_set.find_dp(
                            self.decl_to_rel_map[r_head.decl()], 
                            head_dp, 
                            exclude_tentative=True
                            ):
                            head_neg = True

                        if all_pos and head_neg:  # True -> False, Buggy
                            self.logger.warning('Bug detected')
                            return False, is_changed

                        if all_pos:
                            if r_head.num_args() <= 0:  # is a query, True -> False
                                self.logger.warning('Bug detected')
                                return False, is_changed
                            
                            is_not_dup = self.pos_data_set.add_dp(r_head_hrel, head_dp)
                            if self.neg_data_set.find_dp(r_head_hrel, head_dp, exclude_tentative=True):
                                self.logger.warning('Bug detected')
                                return False, is_changed
                            if not is_not_dup:
                                self.logger.error('Duplicate pos data points should be impossible')
                                raise RuntimeError('Duplicate pos data points should be impossible')
                            self.logger.debug(f'Got Pos DP {r_head}: {head_dp} from forward implication')
                            self.neg_data_set.del_dp(r_head_hrel, head_dp)

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
                            if not self.sample_linear_horn_clause(r_head, head_dp):
                                return False, is_changed
                            pos_upd = True

                        elif head_neg:
                            if r.is_fact():  # is a fact, True -> False
                                self.logger.warning('Bug detected')
                                return False, is_changed
                            
                            for rel, dp in dps:  # TODO: non-lin chc not correct
                                is_not_dup = self.neg_data_set.add_dp(self.decl_to_rel_map[rel], dp)
                                if self.pos_data_set.find_dp(self.decl_to_rel_map[rel], dp):
                                    self.logger.warning('Bug detected')
                                    return False, is_changed
                                if not is_not_dup:
                                    self.logger.error('Duplicate neg data points should be impossible')
                                    raise RuntimeError('Duplicate neg data points should be impossible')
                                self.logger.debug(f'Got Neg DP {rel}: {dp} from backward implication')

                            if self.neg_data_set.size(r_head_hrel) >= self.params['SVM']['SVMFreqPos']:
                                self.svm_learn([r_head_hrel])

                            # sample more neg dps using the seed we got just now
                            for rel, dp in dps:
                                if not self.sample_linear_horn_clause_backward(self.decl_to_rel_map[rel], dp):
                                    return False, is_changed

                        else:
                            # collect neg dps
                            neg_dps = OrderedSet()  # avoid duplicate in the same round
                            for rel, dp in dps:
                                hrel = self.decl_to_rel_map[rel]
                                if self.pos_data_set.find_dp(hrel, dp) or self.match_fact(rel, dp):
                                    continue
                                neg_dp = (rel, tuple(dp))
                                neg_dps.add(neg_dp)
                            
                            for rel, dp in neg_dps:
                                hrel = self.decl_to_rel_map[rel]
                                is_not_dup = self.neg_data_set.add_dp(hrel, dp, is_tentative=True)
                                if not is_not_dup:
                                    self.logger.error('Duplicate neg data points should be impossible')
                                    raise RuntimeError('Duplicate neg data points should be impossible')
                                self.logger.debug(f'Got Tentative Neg DP {rel}: {dp} from implication CEX')

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

    def invalidate_queries(self):
        """forcing all the queries to false"""
        queries = self.query_rels
        for q in queries:
            self.cand_map[q] = Z3_FALSE
            # self.logger.debug(f'{q} invalidated (candidate set to False)')
        return