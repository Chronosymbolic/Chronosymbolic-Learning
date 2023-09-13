import z3
import time
import copy
import yaml
import re
from ordered_set import OrderedSet


Z3_FALSE = z3.BoolVal(False)
Z3_TRUE = z3.BoolVal(True)


def load_yaml(config_path):
    with open(config_path) as f:
        params = yaml.load(f, Loader=yaml.SafeLoader)
    return params

def double_check(file_name, logger, cand_map, learner_cand_map=None, free_vars_prefix='Var_'):
    from horndb.horndb import DoubleChecker
    double_checker = DoubleChecker(file_name, logger, free_vars_prefix)
    res = False
    try:
        logger.warning('\n************** Double Check **************')
        res = double_checker.check(cand_map)
    except RuntimeError:
        logger.warning('CHC System Double Check ERROR/TIMEOUT')
    except KeyboardInterrupt:
        logger.warning('CHC System Double Check KILLED')

    if res:
        logger.warning('CHC System Double Check PASSED')
    else:
        logger.warning('CHC System Double Check FAILED')
    
    if learner_cand_map is not None:
        l_res = False
        try:
            l_res = double_checker.check(learner_cand_map)
        except RuntimeError:
            logger.warning('CHC System Double Check (Learner\'s Result) TIMEOUT')
        except KeyboardInterrupt:
            logger.warning('CHC System Double Check (Learner\'s Result) KILLED')

        if l_res:
            logger.warning('\nLearner\'s Result is also CORRECT:')
            for rel, cand in learner_cand_map.items():
                logger.warning(f'\nRelation: {rel}, \nCandidate: {cand}')
        else:
            logger.warning('Learner\'s Result FAILED')
    return res

def is_uncertain(arg_val):
    if z3.is_int_value(arg_val):
        return False
    if z3.is_bool(arg_val) and (z3.is_true(arg_val) or z3.is_false(arg_val)):
        return False
    return True

def is_unknown(arg, enable=True):
    """
    Return True means this arg can be ignored 
    """
    if not enable:
        return False

    arg_name = str(arg)
    if arg_name.find("@unknown") != -1 or arg_name.find("_nondet_") != -1:
        return True
    else:
        return False

def is_query_rel(rel_decl, db):
    queries = db.get_queries()
    for q in queries:
        body = q.body()
        body_decls = []
        for b in body:
            b_decl = b.decl()
            body_decls.append(b_decl)
        if rel_decl in body_decls:
            return True
    return False

def is_fapp_args_all_vars(fapp):
    """
    Return True if fapp args are all 'free'
    e.g. p(x, x+1) returns False, p(x, y+1) returns False, p(x, x) returns False
        p(x, y) returns True
    """
    arg_list = []
    for i in range(fapp.num_args()):
        arg_i = fapp.arg(i)
        if not is_var_arg(arg_i) or not z3.is_const(arg_i):
            return False
        arg_list.append(arg_i)
    arg_set = set(arg_list)
    if len(arg_list) != len(arg_set):
        return False
    return True

def substitute(rule, rels, exprs, free_vars_prefix=None):
    """
    Substitute relations in a rule with their solution (expr),
    nested relations like And(p1(x, y), p2(z)) are not supported!

    Return body and head z3 expression
    rule: HornRule, rels: fdecls, exprs: cand_map (k: rels, v: z3 exprs)
    """
    # assert(z3.is_expr(expr))
    atoms = rule.body()  # atoms
    f = []  # new atoms
    head = rule.head()

    rels_str = []
    for rel in rels:
        rels_str.append(rel.name())

    for atom in atoms:  # substitute body
        a_decl = atom.decl()
        if z3.is_app(atom) and a_decl.name() in rels_str:
            var_list = get_arg_list(atom)
            expr_sub = substitute_vars(exprs[a_decl], var_list, a_decl, free_vars_prefix)
            f.append(expr_sub)
        else:
            f.append(atom)

    h_decl = head.decl()
    if z3.is_app(head) and  h_decl.name() in rels_str:  # substitute head
        var_list = get_arg_list(head)
        expr_sub = substitute_vars(exprs[h_decl], var_list, h_decl, free_vars_prefix)
        head = copy.deepcopy(expr_sub)


    if len(f) == 0:
        f = Z3_TRUE
    elif len(f) == 1:
        f = f[0]
    else:
        f = z3.And(f)
    return f, head

def substitute_vars(expr, var_list, atom_decl=None, free_vars_prefix=None):
    """
    If free_vars_prefix is None, use z3.substitute_vars
    Otherwise, vars are renamed, use z3.substitute
    """
    if free_vars_prefix is None:
        expr_sub = z3.substitute_vars(expr, *var_list)
    else:
        arg_var_list = []
        for i, arg in enumerate(var_list):
            var_i = z3.Const(free_vars_prefix+str(i), atom_decl.domain(i))
            arg_var_list.append((var_i, arg))
        expr_sub = z3.substitute(expr, *arg_var_list)
    return expr_sub

def find_query_rel(db):
    """
    Return a list of query decl (where the query rels evaluate to False)
    """
    query_rels = set()
    expand = set()
    queries = db.get_queries()
    for q in queries:
        body = q.body()
        for b in body:
            b_decl = b.decl()
            if q.is_uninterp(b):
                query_rels.add(b_decl)
                expand.add(b_decl)

    rules = db.get_rules()
    while True:
        expand_next = set()
        for r in rules:
            r_head_decl = r.head().decl()
            if r_head_decl in expand:
                if len(r.body()) == 1 and r.is_uninterp(r.body()[0].decl()):
                    # p() -> Query rel
                    expand_next.add(r.body()[0].decl())
                    query_rels.add(r.body()[0].decl())
        if len(expand_next) == 0:
            break
        expand = copy.deepcopy(expand_next)
    
    return list(query_rels)

def find_fact_rel(db):
    """
    Return a list of fact decl (where the fact rels evaluate to True)
    """
    fact_rels = set()
    expand = set()
    facts = db.get_facts()
    for f in facts:
        h_decl = f.head().decl()
        body_and = z3.And(f.body())
        if len(f.body()) == 0:
            body_and = Z3_TRUE
        # if f.is_uninterp(h_decl) and is_fapp_args_all_vars(f.head()) and z3.is_true(body_and):
        if f.is_uninterp(h_decl) and z3.is_true(body_and):
            # is_fapp_args_all_vars: prevent cases like True -> p(1)
            fact_rels.add(h_decl)
            expand.add(h_decl)

    rules = db.get_rules()
    while True:
        expand_next = set()
        for r in rules:
            if len(r.body()) == 1:
                r_body_decl = r.body()[0].decl()
                if r_body_decl in expand:
                    # if r.is_uninterp(r.head().decl()) and is_fapp_args_all_vars(r.head()):
                    if r.is_uninterp(r.head().decl()):
                        # Fact rel -> p()
                        expand_next.add(r.head().decl())
                        fact_rels.add(r.head().decl())
        if len(expand_next) == 0:
            break
        expand = copy.deepcopy(expand_next)
    
    return list(fact_rels)

def substitute_predicate_with_expr(fapp, expr_to_sub, sub_expr, free_vars_prefix=None):
    """
    Substitute fapp in expr_to_sub with sub_expr
    e.g. use x>y to replace p(x,y) 
    """
    assert(z3.is_app(fapp))
    var_list = get_arg_list(fapp)
    sub_expr_var = substitute_vars(sub_expr, var_list, fapp.decl(), free_vars_prefix)
    res = z3.substitute(expr_to_sub, (fapp, sub_expr_var))
    return res
 
def get_arg_list(fapp):
    """
    fapp -> arg_list
    """
    assert(z3.is_app(fapp))
    var_list = list()
    for i in range(fapp.num_args()):
        var_list.append(fapp.arg(i))
    return var_list

def get_rel_args(rel, free_vars_prefix):
    """
    HornRelation -> arg_list as Z3_Const
    """
    decl = rel.decl()
    n = decl.arity()
    args = [z3.Const(free_vars_prefix+str(i), decl.domain(i)) for i in range(n)]
    return args

def is_var_arg(arg):
    """
    Return False if arg is an int/bool const
    """
    if z3.is_int_value(arg) or z3.is_true(arg) or z3.is_false(arg):
        return False
    return True

def generate_not_again_expr(dps, sigs):
    exprs = []
    for dp in dps:
        expr = Z3_FALSE
        for i, d in enumerate(dp):
            # if not is_var_arg(d):
                # is constant, not uncertain (uncertain: -inf ~ +inf)
            expr = z3.Or(expr, sigs[i] != d)
        exprs.append(z3.simplify(expr))
    return exprs

def sample_dp_from_zone(rel, zone, dps, ovfl_val, logger, s, n: int = 1, free_vars_prefix=None, additional_cstr=None):
    """
    Sample n dps in zone
    (exclude dps in dataset)
    rel: HornRelation
    """
    sigs = rel.sigs()
    s.reset()
    zone_sub = substitute_vars(zone, sigs, rel.decl(), free_vars_prefix)
    s.add(zone_sub)

    # do not sample dps in dataset again
    not_again_expr = generate_not_again_expr(dps, sigs)
    s.add(not_again_expr)
    
    new_dps = []
    z3_time = 0
    z3_calls = 0
    for i in range(n):
        start_time = time.time()
        res = s.check()
        z3_time += time.time() - start_time
        z3_calls += 1

        if res == z3.sat:
            model = s.model()
        else:
            break

        dp = []
        for sig in sigs:
            val = model.eval(sig)
            if z3.is_bool(val) and (z3.is_true(val) or z3.is_false(val)):  
                # Boolean value
                val = True if z3.is_true(val) else False 
            elif is_uncertain(val):  # uncertain value
                logger.debug(f'Uncertain Value: {val}')
                if z3.is_bool(val):
                    val = False  # specify a random value
                else:
                    val = 0  # specify a random value
            elif abs(val.as_long()) >= ovfl_val:
                logger.warning(f'Overflow Value: {val}')
                raise RuntimeError(f'Overflow Value: {val}')
            else:
                assert(z3.is_int_value(val))
                val = val.as_long()
            dp.append(val)

        not_again_expr = generate_not_again_expr([tuple(dp)], sigs)
        s.add(not_again_expr)
        new_dps.append(tuple(dp))
    
    return new_dps, z3_calls, z3_time

def get_distinguished_vars_map(r):
    """
    r: HornRule
    Return [(A, A_1), ...] (1 is the idx of the rule)
    """
    r_vars = r.vars()
    vmap = []
    for rv in r_vars:
        new_name = str(rv) + '_' + str(r.get_idx())
        new_var = z3.Const(new_name, rv.sort())
        vmap.append((rv, new_var))
    return vmap

def check_identity(expr_a, expr_b, sigs, s, decl=None, free_vars_prefix=None):
    """
    Return True if expr_a <=> expr_b
    """
    a = substitute_vars(expr_a, sigs, decl, free_vars_prefix)
    b = substitute_vars(expr_b, sigs, decl, free_vars_prefix)
    s.reset()
    # s.add(z3.ForAll(sigs, z3.Implies(a, b)))
    # s.add(z3.ForAll(sigs, z3.Implies(b, a)))  # invalid because we have other vars other than sigs
    s.add(z3.Not(a == b))
    res = s.check()
    if res == z3.unknown:
        raise RuntimeError('Z3 returns unknown (check_identity)')
    elif res == z3.unsat:
        # equivalence hold
        return True
    return False

def is_in_zone(dp, zone, sigs, s, decl=None, free_vars_prefix=None):
    """
    Return True if dp in zone
    """
    s.reset()

    if free_vars_prefix is None:
        z = substitute_vars(zone, sigs, decl, free_vars_prefix)
        s.add(z)
        for i, d in enumerate(dp):
            s.add(sigs[i] == d)
    else:
        s.add(zone)
        for i, d in enumerate(dp):
            var_i = z3.Const(free_vars_prefix+str(i), decl.domain(i))
            s.add(var_i == d)
    
    res = s.check()
    if res == z3.unknown:
        raise RuntimeError('Z3 returns unknown (is_in_zone)')
    elif res == z3.sat:
        return True
    return False

def get_pred_eval_expr(pred, vars):
    """
    pred: fapp
    convert pred(x, x+1) to expr: 
        Var(0) == x AND Var(1) == x + 1
    """
    expr = Z3_TRUE
    for i in range(pred.num_args()):
        arg_i = pred.arg(i)
        expr = z3.And(expr, vars[i] == arg_i)
    return z3.simplify(expr)

def substitute_const_with_free_vars(consts, expr, free_vars_prefix='Var_'):
    sub_list = []
    for i, c in enumerate(consts):
        sub_list.append((c, z3.Const(free_vars_prefix+str(i), c.sort())))
    res = z3.substitute(expr, *sub_list)
    return res

def get_free_vars(fapp_vars, vars):
    free_vars = []
    fapp_vars_str = []
    for fv in fapp_vars:
        fapp_vars_str.append(fv.sexpr())

    for i, v in enumerate(vars):
        if v.sexpr() not in fapp_vars_str:
            free_vars.append(v)
    return free_vars

def rename_vars(expr, decl, free_vars_prefix):
    """
    Var(0) + Var(1) => Var_0 + Var_1 (const)
    """
    arity = decl.arity()
    free_vars_renamed = [z3.Const(free_vars_prefix+str(i), decl.domain(i)) for i in range(arity)]
    res = z3.substitute_vars(expr, *free_vars_renamed)
    return res

def extract_mod_nums(db_str):
    # res = re.findall('[^@]%\d+', db_str)
    # mod_nums = [int(r[2:]) for r in res]
    res = re.findall('\(mod [^ ]+ \d+\)', db_str)
    mod_nums = [int(r.split(' ')[-1][:-1]) for r in res]
    return OrderedSet(mod_nums)
    
def extract_div_nums(db_str):
    res = re.findall('\(div [^ ]+ \d+\)', db_str)
    div_nums = [r.split(' ')[-1][:-1] for r in res]
    return OrderedSet(div_nums)