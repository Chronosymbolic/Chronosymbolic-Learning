from horndb.horndb import HornClauseDb, HornRelation, HornRule
from learner.learner_v2 import DataDrivenLearner_v2
import z3
import time
from ordered_set import OrderedSet
import copy
from utils.la_utils import *
from utils.dataset import *

import sys
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)
import eventlet


class Chronosymbolic(DataDrivenLearner_v2):
    def __init__(self, db: HornClauseDb, params, ClassDT, log_path='log.txt', file_name_suffix=''):
        super(Chronosymbolic, self).__init__(db, params, ClassDT, log_path, file_name_suffix)
        self.safe_zone = dict()
        self.unsafe_zone = dict()
        self.learner_cand_map = copy.deepcopy(self.cand_map)  # store the learner's result
        self.rel_args = dict()

        self.qe = z3.Tactic('qe-light')
        self.qe_time = 0
        self.max_len_body_and_fwd = 0
        self.len_body_and_fwd = []
        self.max_len_body_and_bwd = 0
        self.len_body_and_bwd = []
        self.total_iter = 0

        self.use_safe_zone = self.params['UseSafeZone']
        self.use_unsafe_zone = self.params['UseUnsafeZone']
        if not self.params['InitPhase']:
            self.use_safe_zone = False
            self.use_unsafe_zone = False

        self.initialized = False
        self.free_vars_prefix = 'Var_'
        # In Chornosymbolic, a new naming system must be used to adapt to the substitution for quantified expr
        self.bounded_vars_counter = 0
        # Used in renaming the bounded variables to avoid collision when substituting
        
        self.reset_zones()


    def reset_zones(self):
        for rel in self.rels:
            self.safe_zone[rel.decl()] = Z3_FALSE
            self.unsafe_zone[rel.decl()] = Z3_FALSE

    def add_exist_quantifier(self, free_vars, expr):
        new_free_vars = [z3.Const(fv.decl().name()+'!!'+str(i+self.bounded_vars_counter), fv.sort())\
                    for i, fv in enumerate(free_vars)]
        expr_sub = z3.substitute(expr, *list(zip(free_vars, new_free_vars)))
        expr_sub = z3.Exists(new_free_vars, expr_sub)
        start_time = time.time()
        expr_sub = self.qe(expr_sub).as_expr()
        self.bounded_vars_counter += len(free_vars)
        self.qe_time += time.time() - start_time
        return expr_sub

    def init_phase(self):
        """
        Reach each relation at least once forward and backward
        to get a initial safe and a unsafe zone
        """
        self.logger.info('============== Init Phase ==============')
        self.init_phase_time = time.time()
        rels_to_reach_fwd = copy.deepcopy(self.rel_decls)
        rels_to_reach_bwd = copy.deepcopy(self.rel_decls)
        updated_rels_fwd = []
        updated_rels_bwd = []

        # -------- Get initial safe zones from facts --------
        for f in self.facts:
            head = f.head()
            h_decl = head.decl()
            if h_decl in rels_to_reach_fwd:
                rels_to_reach_fwd.remove(h_decl)
            if h_decl not in updated_rels_fwd:
                updated_rels_fwd.append(h_decl)

            body_and = z3.And(f.body_cstr())  # ignore fact rels
            if len(f.body_cstr()) == 0:
                body_and = Z3_TRUE

            # substitute vars and bound free vars
            fapp_vars = get_arg_list(head)
            free_vars = get_free_vars(fapp_vars, f.vars())
            body_and = substitute_const_with_free_vars(fapp_vars, body_and)
            if len(free_vars) > 0:
                body_and = self.add_exist_quantifier(free_vars, body_and)

            self.safe_zone[h_decl] = z3.simplify(body_and) if h_decl not in self.safe_zone.keys()\
                else z3.simplify(z3.Or(self.safe_zone[h_decl], body_and))
            eq_st = time.time()
            self.safe_zone[h_decl] = self.eq_solver(self.safe_zone[h_decl]).as_expr()
            self.eq_solver_time += time.time() - eq_st
        
        self.logger.info('Find SAFE zones from Facts')
        for fdecl in updated_rels_fwd:
            self.logger.info(f'Init SAFE zone for {fdecl}: {self.safe_zone[fdecl]}')


        # -------- Get initial unsafe zones from queries --------
        for q in self.queries:
            body = q.body()
            body_pred = q.body_preds()
            assert(len(body_pred) <= 1)  # currently only support linear chcs
            if len(body_pred) == 0:
                continue
            body_pred = body_pred[0]
            b_decl = body_pred.decl()

            if q.is_query():  # ignore simple!!query -> False (head is False)
                if b_decl in rels_to_reach_fwd:
                    rels_to_reach_fwd.remove(b_decl)
                if b_decl in rels_to_reach_bwd:
                    rels_to_reach_bwd.remove(b_decl)
                continue

            if b_decl in rels_to_reach_bwd:
                rels_to_reach_bwd.remove(b_decl)
            if b_decl not in updated_rels_bwd:
                updated_rels_bwd.append(b_decl)

            body_and = z3.And(q.body_cstr())

            # substitute vars and bound free vars
            fapp_vars = get_arg_list(body_pred)
            free_vars = get_free_vars(fapp_vars, q.vars())
            body_and = substitute_const_with_free_vars(fapp_vars, body_and)
            if len(free_vars) > 0:
                body_and = self.add_exist_quantifier(free_vars, body_and)

            self.unsafe_zone[b_decl] = z3.simplify(body_and) if b_decl not in self.unsafe_zone.keys()\
                else z3.simplify(z3.Or(self.unsafe_zone[b_decl], body_and))
            eq_st = time.time()
            self.unsafe_zone[h_decl] = self.eq_solver(self.unsafe_zone[h_decl]).as_expr()
            self.eq_solver_time += time.time() - eq_st
        
        self.logger.info('Find UNSAFE zones from Queries')
        for fdecl in updated_rels_bwd:
            self.logger.info(f'Init UNSAFE zone for {fdecl}: {self.unsafe_zone[fdecl]}')


        if self.params['Expansion']['UseExpansion']:
            # -------- Unroll the rules forward to reach other relations --------
            # "Forward Expansion", can be called as a func when pos dp is scarce
            try:
                self.forward_expansion(
                    rels_to_reach_fwd,
                    updated_rels_fwd,
                    self.params['Expansion']['InitExpMinIter'],
                    self.params['Expansion']['InitExpMaxIter']
                    )
            except RuntimeError:
                self.logger.warning('Z3 Returns Unknown, skip this phase')

            # -------- Unroll the rules backward to reach other relations --------
            # "Backward Expansion"
            try:
                self.backward_expansion(
                    rels_to_reach_bwd,
                    updated_rels_bwd,
                    self.params['Expansion']['InitExpMinIter'],
                    self.params['Expansion']['InitExpMaxIter']
                    )
            except RuntimeError:
                self.logger.warning('Z3 Returns Unknown, skip this phase')

        # -------- Sample dps for zones and get initial inv --------
        for rel in self.rels:
            rel_decl = rel.decl()
            sigs = rel.sigs()
            if rel.decl() in self.query_rels:
                self.cand_map[rel_decl] = Z3_FALSE
                continue
            if rel.decl() in self.fact_rels:
                self.cand_map[rel_decl] = Z3_TRUE
                continue

            # Init self.cand_map to ~U (L=True), or init self.cand to S (L=False)
            # which is better? Or we have a better init strategy?
            self.cand_map[rel_decl] = copy.deepcopy(self.safe_zone[rel_decl])

            # No need for c5/svm to learn if one zone is empty
            if z3.is_false(self.safe_zone[rel_decl]) or \
                z3.is_false(self.unsafe_zone[rel_decl]):
                self.logger.info(f'Relation {rel_decl} has empty zone(s)')
                continue

            # S AND U is SAT, buggy
            if self.check_overlap(rel_decl, sigs):
                return False
            
            # Sample dps from both zones and learn
            if not self.sample_and_learn(rel):
                return False

        self.init_phase_time = time.time() - self.init_phase_time
        self.logger.info(f'============== Init Phase Ended, Time: {self.init_phase_time} ==============')
        return True

    def check_overlap(self, rel_decl, sigs):
        """
        Return True if safe and unsafe zone overlap
        """
        self.solver.reset()
        safe_zone_sub = substitute_vars(self.safe_zone[rel_decl], sigs, rel_decl, self.free_vars_prefix)
        unsafe_zone_sub = substitute_vars(self.unsafe_zone[rel_decl], sigs, rel_decl, self.free_vars_prefix)
        self.solver.add(safe_zone_sub)
        self.solver.add(unsafe_zone_sub)
        # self.logger.info(f'Constraint: {self.solver}')
        start_time = time.time()
        res = self.solver.check()
        self.z3_calls += 1
        self.z3_time += time.time() - start_time
        if res == z3.sat:
            self.logger.warning('Bug detected (SAFE and UNSAFE zones overlap)')
            self.init_phase_time = time.time() - self.init_phase_time
            return True
        elif res == z3.unknown:
            self.init_phase_time = time.time() - self.init_phase_time
            raise RuntimeError('Z3 returns unknown (check_overlap)')
        return False

    def forward_expansion(self, rels_to_reach_fwd, updated_rels_fwd, min_iter=3, max_iter=7):
        iter = 0
        skip_rules = []
        while len(rels_to_reach_fwd) or iter < min_iter:
            iter += 1
            if iter > max_iter:
                break
            self.logger.info(f'Forward Iteration {iter}')
            changed_rules = 0

            for r in self.rules:
                if r in self.queries or r in self.facts or\
                    r.get_idx() in skip_rules:
                    continue

                h_decl = r.head().decl()
                if z3.is_true(self.safe_zone[h_decl]) or z3.is_true(self.unsafe_zone[h_decl]):
                    # skip rels that cannot be expand anymore
                    continue
                body_pred = r.body_preds()
                assert(len(body_pred) <= 1)  # currently only support linear chcs
                body_pred = body_pred[0]
                b_decl = body_pred.decl()
                head = r.head()

                if b_decl in updated_rels_fwd:
                    # can expand
                    body_and = z3.And(r.body())
                    
                    # substitute predicate with candidate expr
                    body_and = substitute_predicate_with_expr(body_pred, body_and, self.safe_zone[b_decl], self.free_vars_prefix)
                    
                    # substitute vars and bound free vars
                    fapp_vars = get_arg_list(head)
                    # timefv = time.time()
                    free_vars = get_free_vars(fapp_vars, r.vars())
                    # timefv = time.time() - timefv
                    if len(free_vars) > self.params['Expansion']['FreeVarUB']:
                        skip_rules.append(r.get_idx())
                        self.logger.debug(f"""
                            Stop expansion at Rule {r.get_idx()},
                            len(free_vars): {len(free_vars)}""")
                        continue

                    body_and = substitute_const_with_free_vars(fapp_vars, body_and)
                    
                    if len(free_vars) > 0:
                        body_and = self.add_exist_quantifier(free_vars, body_and)
                        body_and = z3.simplify(body_and)

                    # add the result to the safe zone of head predicate
                    new_zone = body_and if h_decl not in self.safe_zone.keys()\
                        else z3.Or(self.safe_zone[h_decl], body_and)
                    
                    # decide if the expansion leads to expensive z3 operation
                    len_sexpr = len(body_and.sexpr())
                    len_nzone = len(new_zone.sexpr())
                    self.len_body_and_fwd.append((len_sexpr, len_nzone))
                    self.max_len_body_and_fwd = len_sexpr if len_sexpr > self.max_len_body_and_fwd else self.max_len_body_and_fwd
                    # self.logger.debug(f"""
                    #     updated_rel: {h_decl},
                    #     body_and: {body_and.sexpr()},
                    #     nzone: {new_zone.sexpr()}
                    #     len(body_and): {len_sexpr}, len(nzone): {len_nzone}""")
                    if not self.params['Expansion']['ForceExp']:
                        if z3.is_quantifier(body_and)\
                            or len_sexpr > self.params['Expansion']['BodyCstrExpUB']\
                            or len_nzone > self.params['Expansion']['NewZoneExpUB']:
                            # exist quantifier in zone make the computation expensive
                            # body_and = self.add_exist_quantifier(free_vars, body_and)
                            self.logger.debug(f"""
                                Stop expansion at Rule {r.get_idx()},
                                is_quantifier: {z3.is_quantifier(body_and)},
                                len(body_and): {len_sexpr}, len(nzone): {len_nzone}""")
                            skip_rules.append(r.get_idx())
                            continue
                    
                    # check identity: very expansive
                    # start_time = time.time()
                    # res = check_identity(self.safe_zone[h_decl], new_zone, self.decl_to_rel_map[h_decl].sigs(), self.solver)
                    # self.z3_calls += 1
                    # self.z3_time += time.time() - start_time
                    res = False
                    if not z3.is_false(body_and) and not res:  # update
                        eq_st = time.time()
                        self.safe_zone[h_decl] = self.eq_solver(new_zone).as_expr()
                        self.eq_solver_time += time.time() - eq_st
                        changed_rules += 1
                    else:
                        self.logger.debug(f'Safe zone for {h_decl} unchanged')
                        continue

                    if h_decl not in updated_rels_fwd:
                        updated_rels_fwd.append(h_decl)
                    # self.logger.debug(f'New safe zone for {h_decl}: {self.safe_zone[h_decl]}')

            # after one epoch, if one predicate has a safe zone, do not update it at next epoch
            for fdecl in updated_rels_fwd:
                if fdecl in rels_to_reach_fwd:
                    rels_to_reach_fwd.remove(fdecl)
            if not changed_rules:  # some rels may never be reached
                self.logger.info(f'Relation update count: {changed_rules}')
                break
            self.logger.info(f'Relation update count: {changed_rules}')

        for fdecl in updated_rels_fwd:
            self.logger.info(f'After expansion, update SAFE zone for {fdecl}')
            # self.logger.info(f'{self.safe_zone[fdecl]}')
        return

    def backward_expansion(self, rels_to_reach_bwd, updated_rels_bwd, min_iter=3, max_iter=7):
        iter = 0
        skip_rules = []
        while len(rels_to_reach_bwd) or iter < min_iter:
            iter += 1
            if iter > max_iter:
                break
            self.logger.info(f'Backward Iteration {iter}')
            changed_rules = 0

            for r in self.rules:
                if r in self.queries or r in self.facts\
                    or r.get_idx() in skip_rules:
                    continue

                h_decl = r.head().decl()
                body_pred = r.body_preds()
                assert(len(body_pred) <= 1)  # currently only support linear chcs
                if len(body_pred) == 0:
                    continue
                body_pred = body_pred[0]
                b_decl = body_pred.decl()
                b_cstr = r.body_cstr()
                if z3.is_true(self.safe_zone[b_decl]) or z3.is_true(self.unsafe_zone[b_decl]):
                    # skip rels that cannot be expand anymore
                    continue
                head = r.head()

                if h_decl in updated_rels_bwd:
                    # can expand
                    body_and = z3.And(b_cstr)
                    body_and_head = z3.And(body_and, head)
                    
                    # substitute predicate with candidate expr
                    body_and_head = substitute_predicate_with_expr(head, body_and_head, self.unsafe_zone[h_decl], self.free_vars_prefix)
                    
                    # substitute vars and bound free vars
                    fapp_vars = get_arg_list(body_pred)
                    free_vars = get_free_vars(fapp_vars, r.vars())
                    if len(free_vars) > self.params['Expansion']['FreeVarUB']:
                        skip_rules.append(r.get_idx())
                        self.logger.debug(f"""
                            Stop expansion at Rule {r.get_idx()},
                            len(free_vars): {len(free_vars)}""")
                        continue

                    body_and_head = substitute_const_with_free_vars(fapp_vars, body_and_head)
                    
                    if len(free_vars) > 0:
                        body_and_head = self.add_exist_quantifier(free_vars, body_and_head)
                        body_and_head = z3.simplify(body_and_head)
                    
                    # add the result to the unsafe zone of body predicate
                    new_zone = body_and_head if b_decl not in self.unsafe_zone.keys()\
                        else z3.Or(self.unsafe_zone[b_decl], body_and_head)
                    
                    # decide if the expansion leads to expensive z3 operation
                    len_sexpr = len(body_and_head.sexpr())
                    len_nzone = len(new_zone.sexpr())
                    self.len_body_and_bwd.append((len_sexpr, len_nzone))
                    self.max_len_body_and_bwd = len_sexpr if len_sexpr > self.max_len_body_and_bwd else self.max_len_body_and_bwd
                    # self.logger.debug(f"""
                    #     updated_rel: {b_decl},
                    #     body_and: {body_and_head.sexpr()},
                    #     nzone: {new_zone.sexpr()}
                    #     len(body_and): {len_sexpr}, len(nzone): {len_nzone}""")
                    if not self.params['Expansion']['ForceExp']:
                        if z3.is_quantifier(body_and_head)\
                            or len_sexpr > self.params['Expansion']['BodyCstrExpUB']\
                            or len_nzone > self.params['Expansion']['NewZoneExpUB']:
                            # exist quantifier in zone make the computation expensive
                            # body_and_head = self.add_exist_quantifier(free_vars, body_and_head)
                            skip_rules.append(r.get_idx())
                            self.logger.debug(f"""
                                Stop expansion at Rule {r.get_idx()},
                                is_quantifier: {z3.is_quantifier(body_and_head)},
                                len(body_and): {len_sexpr}, len(nzone): {len_nzone}""")
                            continue

                    # check identity
                    # start_time = time.time()
                    # res = check_identity(self.unsafe_zone[b_decl], new_zone, self.decl_to_rel_map[b_decl].sigs(), self.solver)
                    # self.z3_calls += 1
                    # self.z3_time += time.time() - start_time
                    res = False
                    if not z3.is_false(body_and_head) and not res:  # update
                        eq_st = time.time()
                        self.unsafe_zone[b_decl] = self.eq_solver(new_zone).as_expr()
                        self.eq_solver_time += time.time() - eq_st
                        changed_rules += 1
                    else:
                        self.logger.debug(f'Unsafe zone for {b_decl} unchanged')
                        continue

                    if b_decl not in updated_rels_bwd:
                        updated_rels_bwd.append(b_decl)
                    # self.logger.debug(f'New unsafe zone for {b_decl}: {self.unsafe_zone[b_decl]}')
            
            # after one epoch, if one predicate has an unsafe zone, do not update it at next epoch
            for fdecl in updated_rels_bwd:
                if fdecl in rels_to_reach_bwd:
                    rels_to_reach_bwd.remove(fdecl)
            if not changed_rules:
                self.logger.info(f'Relation update count: {changed_rules}')
                break
            self.logger.info(f'Relation update count: {changed_rules}')

        for fdecl in updated_rels_bwd:
            self.logger.info(f'After expansion, updated UNSAFE zone for {fdecl}')
            # self.logger.info(f'{self.unsafe_zone[fdecl]}')
        return

    def sample_and_learn(self, rel, max_sample_iter=3):
        rel_decl = rel.decl()
        sigs = rel.sigs()
        self.logger.info(f'Sample dps for {rel_decl}')
        pos_finished = False
        neg_finished = False
        sample_iter = 0
        while sample_iter < max_sample_iter:
            sample_iter += 1
            # old_cand = substitute_vars(self.cand_map[rel_decl], *sigs, rel_decl, self.free_vars_prefix)

            # sample a few dps for each relation
            if not pos_finished:
                new_pos_dps, z3_calls, z3_time = sample_dp_from_zone(
                    rel,
                    self.safe_zone[rel_decl],
                    self.pos_data_set.get_dps(rel),
                    self.params['OverflowLimit'],
                    self.logger,
                    self.solver,
                    self.params['SampleBatchSize'],
                    self.free_vars_prefix
                    )
                self.z3_calls += z3_calls
                self.z3_time += z3_time

            if not neg_finished:
                new_neg_dps, z3_calls, z3_time = sample_dp_from_zone(
                    rel,
                    self.unsafe_zone[rel_decl],
                    self.neg_data_set.get_dps(rel),
                    self.params['OverflowLimit'],
                    self.logger,
                    self.solver,
                    self.params['SampleBatchSize'],
                    self.free_vars_prefix
                    )
                self.z3_calls += z3_calls   
                self.z3_time += z3_time

            if len(new_pos_dps) < self.params['SampleBatchSize']:
                pos_finished = True
            if len(new_neg_dps) < self.params['SampleBatchSize']:
                neg_finished = True
            
            if len(new_pos_dps) <= self.params['Expansion']['InitExpMinIter'] and self.params['SampleBatchSize'] > self.params['Expansion']['InitExpMinIter'] + 1:
                self.use_safe_zone = False
            for new_pos_dp in new_pos_dps:
                self.pos_data_set.add_dp(rel, new_pos_dp)
                self.neg_data_set.clear(rel)
                if not self.sample_linear_horn_clause(rel, new_pos_dp):
                    self.logger.warning('Bug detected (extend from sampled pos dp)')
                    return False
            
            if len(new_neg_dps) <= self.params['Expansion']['InitExpMinIter'] and self.params['SampleBatchSize'] > self.params['Expansion']['InitExpMinIter'] + 1:
                self.use_unsafe_zone = False
            for new_neg_dp in new_neg_dps:
                self.neg_data_set.add_dp(rel, new_neg_dp)
                # if not self.sample_linear_horn_clause_backward(rel, new_neg_dp):
                #     self.logger.warning('Bug detected (extend from sampled neg dp)')
                #     return False
        
            self.svm_learn([rel])
            self.C5_learn([rel])
            # if S OR (L' AND ~U) <=> S OR (L AND ~U) [= self.cand_map[rel]]
            # new iter = last iter, no progress, need to sample more dps
            
            new_cand = self.cand_map[rel_decl]
            # start_time = time.time()
            # res = check_identity(new_cand, old_cand, sigs, self.solver)
            # self.z3_calls += 1
            # self.z3_time += time.time() - start_time
            res = False

            if pos_finished and neg_finished:
                self.logger.info(f'No more dps can be sampled')
                break

            if not res:
                # cand changed
                # self.logger.info(f'Candidate changed, sample finished')
                break
            self.logger.info(f'Candidate unchanged, sample more dps...')
        return True

    def cand_postprocessing(self, target=None):
        """
        Simplify(S OR (L AND ~U))
        """
        if self.params['UseSafeZone']:
            tmp = self.use_safe_zone
            self.use_safe_zone = True if eval(self.params['Strategy']['SafeZoneUsage']) else False
            if tmp != self.use_safe_zone:
                self.logger.info(f'Switch UseSafeZone to {self.use_safe_zone} at iter {self.total_iter}')
        if self.params['UseUnsafeZone']:
            tmp = self.use_unsafe_zone
            self.use_unsafe_zone = True if eval(self.params['Strategy']['UnsafeZoneUsage']) else False
            if tmp != self.use_unsafe_zone:
                self.logger.info(f'Switch UseUnsafeZone to {self.use_unsafe_zone} at iter {self.total_iter}')

        for rel in self.rels:
            if target is None or rel in target:
                rel = rel.decl()
                self.learner_cand_map[rel] = copy.deepcopy(self.cand_map[rel])
                if self.use_unsafe_zone:
                    self.cand_map[rel] = z3.And(z3.Not(self.unsafe_zone[rel]), self.cand_map[rel])
                if self.use_safe_zone:
                    self.cand_map[rel] = z3.Or(self.safe_zone[rel], self.cand_map[rel])
                eq_st = time.time()
                self.cand_map[rel] = self.eq_solver(self.cand_map[rel]).as_expr()  # simplify
                self.eq_solver_time += time.time() - eq_st
                # self.logger.info(f'Postprocessed Candidate for {rel}:\n{self.cand_map[rel]}')
        self.invalidate_queries()
        return

    def invalidate_queries(self):
        """forcing all the queries to false"""
        queries = self.query_rels
        for q in queries:
            self.cand_map[q] = Z3_FALSE
            self.learner_cand_map[q] = Z3_FALSE
            # self.logger.debug(f'{q} invalidated (candidate set to False)')
        return

    def get_rel_args(self, rel: HornRelation):
        decl = rel.decl()
        if decl in self.rel_args.keys():
            return self.rel_args[decl]
        n = decl.arity()
        args = [z3.Const(self.free_vars_prefix+str(i), decl.domain(i)) for i in range(n)]
        self.rel_args[decl] = args
        return args

    def C5_learn(self, target=None):
        self.pos_data_set.clear_updated_rels()
        self.neg_data_set.clear_updated_rels()
        super().C5_learn(target)

    def print_cand(self):
        if self.cand_counter % self.params['Verbosity']['PrintNewCandFreq'] == 0:
            for rel in self.rel_decls:
                self.logger.info(
                    f'New Candidate for {rel}:\n   {self.learner_cand_map[rel]}')
        self.cand_counter += 1

    def get_def(self, rule: HornRule, rel=None):
        if rel is None:  # substitute all rels
            body, head = substitute(rule, self.rel_decls, self.cand_map, self.free_vars_prefix)
            return body, head
        r_decl = rel.decl()
        body, head = substitute(rule, [r_decl], {r_decl: self.cand_map[r_decl]}, self.free_vars_prefix)
        return body, head

    def solve_constraints(self):
        if not self.initialized and self.params['InitPhase']:
            is_correct = self.init_phase()
            self.initialized = True
            if not is_correct:
                return False, False
            self.aux_info['max_len_exp_fwd'] = self.max_len_body_and_fwd
            self.aux_info['max_len_exp_bwd'] = self.max_len_body_and_bwd
            self.aux_info['len_exp_zone_fwd'] = self.len_body_and_fwd
            self.aux_info['len_exp_zone_bwd'] = self.len_body_and_bwd 

        is_correct, is_changed = self._solve_constraints()
        self.aux_info['QE Time'] = self.qe_time
        return is_correct, is_changed

    def _solve_constraints(self):
        is_changed = False
        work_list = self.rules[:]
        self.logger.info(
            '========== Constraint Solving of Horn Clauses ===========')

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

            if self.is_fact_rule(r):
                if not r.is_head_uninterp() or self.is_query_rel(r_head.decl()):
                    # trivial rule or fact and query simultaneously
                    self.logger.debug('This rule is a FACT (trivial)')
                    r_cand_b, r_cand_h = self.get_def(r)
                    res, model = self.solve_negated_rule(r_cand_b, r_cand_h)
                    if res == z3.sat:
                        self.logger.warning('Bug detected (trivial fact)')
                        return False, is_changed
                else:
                    if not self.use_safe_zone:
                        self.logger.debug(
                            f'Generate Positive State Samples From Fact Rule Index {r.get_idx()}')
                        i = 0
                        while True:
                            i += 1
                            self.total_iter += 1
                            self.aux_info['Total Iter'] = self.total_iter
                            self.logger.debug(
                                f'Generate Positive State Samples Iteration {i}, Total Iter {self.total_iter}')
                            run, upd = self.generate_postive_samples_from_fact(r)
                            if not run:
                                self.logger.warning('Bug detected (fact sampling)')
                                return False, is_changed
                            if not upd or i >= self.params['FactSampleMaxRound']:
                                if not upd:
                                    self.logger.info(f'Fact idx {r.get_idx()} PASSED')
                                break
                            is_changed = True
                            pos_upd = True
                            target_pos = self.pos_data_set.get_updated_rels()
                            self.C5_learn(list(target_pos))
                            self.logger.info(f'For FACT rules this round,')
                            self.logger.info(f'Updated positive datasets for {len(target_pos)} relations')
                        self.add_rule_with_given_head_in_body(work_list, r)
                    else:
                        self.logger.debug('This rule is a FACT, skipped')

            elif self.is_query_rel(r_head.decl()):
                if r.is_fact():
                    self.logger.debug('This rule is a Query (trivial)')
                    r_cand_b, r_cand_h = self.get_def(r)
                    res, model = self.solve_negated_rule(r_cand_b, r_cand_h)
                    if res == z3.sat:
                        self.logger.warning('Bug detected (trivial query)')
                        return False, is_changed
                else:
                    if not self.use_unsafe_zone:
                        self.total_iter += 1
                        self.aux_info['Total Iter'] = self.total_iter
                        self.logger.debug(
                            f'Generate Negative State Samples From Query Rule Index {r.get_idx()}')
                        i = 0
                        while True:
                            i += 1
                            self.logger.debug(
                                f'Generate Negative State Samples Iteration {i}')
                            run, upd = self.generate_negative_samples_from_query(r)
                            if not run:
                                self.logger.warning('Bug detected (query sampling)')
                                return False, is_changed
                            if not upd or i >= self.params['QuerySampleMaxRound']:
                                if not upd:
                                    self.logger.info(f'Query idx {r.get_idx()} PASSED')
                                break
                            is_changed = True
                            pos_upd = True
                            target_neg = self.neg_data_set.get_updated_rels()
                            self.C5_learn(list(target_neg))
                            self.logger.info(f'For QUERY rules this round,')
                            self.logger.info(f'Updated negative datasets for {len(target_neg)} relations')
                        self.add_rule_with_given_body_in_head(work_list, r)
                    else:
                        self.logger.debug('This rule is a Query, skipped')

            else:  # not fact or query
                while True:
                    counter += 1
                    self.total_iter += 1
                    self.aux_info['Total Iter'] = self.total_iter
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
                            if self.pos_data_set.find_dp(self.decl_to_rel_map[rel], dp) or \
                                is_in_zone(
                                    dp,
                                    self.safe_zone[rel],
                                    self.decl_to_rel_map[rel].sigs(),
                                    self.solver,
                                    rel,
                                    self.free_vars_prefix
                                    ):
                                continue
                            all_pos = False
                            break
                        
                        # if head dp is true neg dp, add new neg dps for body
                        head_neg = False
                        head_dp = self.get_dp_from_model(r_head, model)
                        if self.neg_data_set.find_dp(
                            r_head_hrel,
                            head_dp, 
                            exclude_tentative=True,
                            exclude_history=False
                            ):
                            head_neg = True
                        elif is_in_zone(
                            head_dp,
                            self.unsafe_zone[r_head.decl()],
                            self.decl_to_rel_map[r_head.decl()].sigs(),
                            self.solver,
                            r_head.decl(),
                            self.free_vars_prefix
                            ):
                            head_neg = True

                        if all_pos and head_neg:  # True -> False, Buggy
                            self.logger.warning('Bug detected (all_pos and head_neg)')
                            return False, is_changed

                        if all_pos:
                            if self.is_query_rel(r_head.decl()):  # is a query, True -> False
                                self.logger.warning('Bug detected (all pos, head is query)')
                                return False, is_changed
                            
                            is_not_dup = self.pos_data_set.add_dp(r_head_hrel, head_dp)
                            if not is_not_dup:
                                self.logger.error(f'Duplicate pos data points {head_dp} should be impossible')
                                raise RuntimeError(f'Duplicate pos data points {head_dp} should be impossible')
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
                                self.logger.warning('Bug detected (sample from pos seed)')
                                return False, is_changed
                            pos_upd = True

                        elif head_neg:
                            if self.is_fact_rule(r):  # is a fact, True -> False
                                self.logger.warning('Bug detected (head_neg and is fact rule)')
                                return False, is_changed
                            
                            for rel, dp in dps:
                                is_not_dup = self.neg_data_set.add_dp(self.decl_to_rel_map[rel], dp)
                                if self.pos_data_set.find_dp(self.decl_to_rel_map[rel], dp):
                                    self.logger.warning('Bug detected (head_neg, pos body)')
                                    return False, is_changed
                                if not is_not_dup:
                                    self.logger.error(f'Duplicate neg data points {dp} should be impossible')
                                    raise RuntimeError(f'Duplicate neg data points {dp} should be impossible')
                                self.logger.debug(f'Got Neg DP {rel}: {dp} from backward implication')

                            if self.neg_data_set.size(r_head_hrel) >= self.params['SVM']['SVMFreqPos']:
                                self.svm_learn([r_head_hrel])

                            # sample more neg dps using the seed we got just now
                            for rel, dp in dps:
                                if not self.sample_linear_horn_clause_backward(self.decl_to_rel_map[rel], dp):
                                    self.logger.warning('Bug detected (sample from neg seed)')
                                    return False, is_changed

                        else:
                            # collect neg dps
                            neg_dps = OrderedSet()  # avoid duplicate in the same round
                            for rel, dp in dps:
                                hrel = self.decl_to_rel_map[rel]
                                if self.pos_data_set.find_dp(hrel, dp) or \
                                    is_in_zone(
                                    dp,
                                    self.safe_zone[rel],
                                    self.decl_to_rel_map[rel].sigs(),
                                    self.solver,
                                    rel,
                                    self.free_vars_prefix
                                    ):
                                    continue
                                neg_dp = (rel, tuple(dp))
                                neg_dps.add(neg_dp)
                            
                            for rel, dp in neg_dps:
                                hrel = self.decl_to_rel_map[rel]
                                is_not_dup = self.neg_data_set.add_dp(hrel, dp, is_tentative=True)
                                if not is_not_dup:
                                    self.logger.error(f'Duplicate neg data points {dp} should be impossible')
                                    raise RuntimeError(f'Duplicate neg data points {dp} should be impossible')
                                self.logger.debug(f'Got Tentative Neg DP {rel}: {dp} from implication CEX')

                                if self.neg_data_set.size(hrel) >= self.params['SVM']['SVMFreqNeg'] \
                                    and self.neg_data_set.size(hrel) % self.params['SVM']['SVMFreqNeg'] == 0:
                                    self.svm_learn([hrel])


                    else:
                        self.logger.info('UNSAT, This rule is PASSED')

                    if upd:
                        target_pos = self.pos_data_set.get_updated_rels()
                        target_neg = self.neg_data_set.get_updated_rels()
                        target = target_pos.union(target_neg)
                        self.C5_learn(list(target))
                        self.logger.info(f'For IMPLICATION rules this round,')
                        self.logger.info(f'Updated positive datasets for {len(target_pos)} relations')
                        self.logger.info(f'Updated negative datasets for {len(target_neg)} relations')

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