import io

import pysmt.environment
import pysmt.solvers.z3 as pyz3
import z3
from pysmt.smtlib.parser import SmtLibZ3Parser, Tokenizer
from utils.la_utils import get_arg_list, is_fapp_args_all_vars, substitute
from horndb.original_horndb import OriginalHornClauseDb


Z3_FALSE = z3.BoolVal(False)
Z3_TRUE = z3.BoolVal(True)


class HornRule(object): 
    def __init__(self, formula):
        self._ctx = formula.ctx
        self._formula = formula
        self._head = None  # head is fapp type
        self._body = []  # body: a list of fapps
        self._body_pred = []  # body predicates: a list of fapps, which are unknown predicates
        self._body_cstr = []  # body constraints: body \ body_pred
        self._uninterp_sz = 0  # how many unknown predicates in body
        self._bound_constants = []
        self._head_args = []
        self._index = 0
        self._sub_var_prefix = 'la_v'  # prefix for substituting vars
        # the instance should not contain vars with the name like that

        self._update()


    def _update(self):
        if not self.has_formula():
            return

        rels = list()
        find_all_uninterp_consts(self._formula, rels)
        self._rels = frozenset(rels)
        body = self._formula
        if z3.is_quantifier(body):
            body, self._bound_constants = ground_quantifier(body)

        if z3.is_implies(body):
            self._head = body.arg(1)
            body = body.arg(0)
            if z3.is_and(body):
                body = body.children()
            else:
                body = [body]
        else:
            self._head = body
            body = []

        # remove all true constants
        body = [z3.simplify(x) for x in body if not z3.is_true(x)]

        if len(body) > 0:
            self._body = body

        for i in range(len(body)):
            f = body[i]
            isapp = z3.is_app(f)
            if not z3.is_quantifier(f):
                fdecl = f.decl()
                if isapp and fdecl in self._rels:
                    self._uninterp_sz += 1
                    self._body_pred.append(f)
                else:
                    self._body_cstr.append(f)
            else:
                self._body_cstr.append(f)

        # reset _formula, it can be re-computed using mk_formula()
        # this ensures that any simplifications that are done during _update() are
        # also reflected in the formula view
        self._formula = None
        assert self._head is not None

    def rewrite(self):
        # substitute head arg list if necessary
        var_counter = 0
        if not self.is_query() and not is_fapp_args_all_vars(self._head):
            h_arg_list = get_arg_list(self._head)
            h_decl = self._head.decl()
            new_exprs = []
            new_h_args = []
            for i, h_arg in enumerate(h_arg_list):
                new_name = self._sub_var_prefix + str(var_counter)
                sort = h_decl.domain(i)
                new_h_arg = z3.Const(new_name, sort)
                new_h_args.append(new_h_arg)
                new_exprs.append(new_h_arg == h_arg)
                var_counter += 1
            self._head = h_decl(*new_h_args)
            self._body.extend(new_exprs)
            self._body_cstr.extend(new_exprs)
            self._bound_constants.extend(new_h_args)
        
        self._head_args = get_arg_list(self._head)
        
        new_body_pred = []
        new_body_cstr = self._body_cstr[:]
        new_body = self._body_cstr[:]
        for b in self._body_pred:
            if not is_fapp_args_all_vars(b):
                b_decl = b.decl()
                b_arg_list = get_arg_list(b)
                new_exprs = []
                new_b_args = []
                for i, b_arg in enumerate(b_arg_list):
                    new_name = self._sub_var_prefix + str(var_counter)
                    sort = b_decl.domain(i)
                    new_b_arg = z3.Const(new_name, sort)
                    new_b_args.append(new_b_arg)
                    new_exprs.append(new_b_arg == b_arg)
                    var_counter += 1
                b_pred = b_decl(*new_b_args)
                new_body_pred.append(b_pred)
                new_body.append(b_pred)
                new_body.extend(new_exprs)
                new_body_cstr.extend(new_exprs)
                self._bound_constants.extend(new_b_args)
            else:
                new_body_pred.append(b)
                new_body.append(b)
        self._body = new_body[:]
        self._body_pred = new_body_pred[:]
        self._body_cstr = new_body_cstr[:]

    def __str__(self):
        return str(self._body) + " -> " + str(self._head)

    def __repr__(self):
        return str(self._body) + " -> " + str(self._head)
        # return repr(self._formula)

    def used_rels(self):
        """return decl"""
        return self._rels

    def is_uninterp(self, rel):
        """if rel is an unknown predicate"""
        if z3.is_app(rel) and rel.decl() in self._rels:
            return True
        if z3.is_func_decl(rel) and rel in self._rels:
            return True
        return False

    def is_query(self):
        return z3.is_false(self._head)

    def is_head_uninterp(self):
        """return True if the head is unknown rel (like p(x, y))"""
        isapp = z3.is_app(self._head)
        fdecl = self._head.decl()
        if isapp and fdecl in self._rels:
            return True
        return False

    def is_simple_query(self):
        """
        Returns true if query is a simple.
        A simple query is an application of an uninterpreted predicate
        """
        if not self.is_query():
            return False

        if self.uninterp_size() != 1:
            return False

        predicate = self.body()[0]

        if predicate.num_args() > 0:
            return False

        _body = self.body()[1:]
        if len(_body) == 0:
            return True

        if len(_body) == 1:
            return z3.is_true(_body[0])

        _body = z3.simplify(z3.And(*_body, self._ctx))
        return z3.is_true(_body)

    # based on the following inference
    #
    # forall v :: (expr ==> false)
    #
    # equivalent to
    #
    # forall v:: ( expr ==> q ) && forall v :: ( q ==> false )
    #
    def split_query(self):
        """Split query if it is not simple into a query and a rule"""

        assert self.is_query()
        if self.is_simple_query():
            return self, None

        q = z3.Bool("simple!!query", self._ctx)
        query = HornRule(z3.Implies(q, False))
        if self._bound_constants:
            rule = HornRule(
                z3.ForAll(
                    self._bound_constants,
                    z3.Implies(z3.And(*self.body(), self._ctx), q),
                )
            )
        else:
            rule = HornRule(z3.Implies(z3.And(*self.body(), self._ctx), q))
        return query, rule

    def is_fact(self):
        return self._uninterp_sz == 0

    def is_linear(self):
        return self._uninterp_sz <= 1

    def to_ast(self):
        return self._formula

    def head(self):
        return self._head

    def body(self):
        return self._body

    def body_preds(self):
        return self._body_pred

    def body_cstr(self):
        return self._body_cstr

    def vars(self):
        return self._bound_constants
    
    def set_vars(self, vars):
        self._bound_constants = vars[:]
    
    def head_args(self):
        return self._head_args

    def uninterp_size(self):
        return self._uninterp_sz

    def has_formula(self):
        return self._formula is not None

    def get_formula(self):
        return self._formula

    def mk_formula(self):
        f = self._body
        if len(f) == 0:
            f = z3.BoolVal(True, self._ctx)
        elif len(f) == 1:
            f = f[0]
        else:
            f = z3.And(f, self._ctx)
        f = z3.Implies(f, self._head)

        if len(self._bound_constants) > 0:
            f = z3.ForAll(self._bound_constants, f)
        self._formula = f
        return self._formula

    def mk_query(self):
        assert self.is_query()
        assert len(self.body()) > 0
        _body = self.body()
        if self.is_simple_query():
            return _body[0]

        if len(_body) == 1:
            f = _body[0]
        else:
            f = z3.And(_body, self._ctx)
        if len(self._bound_constants) > 0:
            f = z3.Exists(self._bound_constants, f)
        return f

    def add_idx(self, idx):
        self._index = idx
    
    def get_idx(self):
        return self._index

    def get_ctx(self):
        return self._ctx


class HornRelation(object):
    def __init__(self, fdecl, env=None):
        self._fdecl = fdecl
        self._sig = []
        self._arg = []
        self._pysmt_sig = []
        self._lemma_parser = None
        self.not_supported = False
        if env is not None:
            self._env = env
        else:
            self._env = pysmt.environment.get_env()
        self._update()


    def _update(self):
        self._sig = []
        for i in range(self._fdecl.arity()):
            name = self._mk_arg_name(i)
            sort = self._fdecl.domain(i)
            if z3.is_array_sort(z3.Const(name, sort)):
                # print('Array sort args is not supported')
                self.not_supported = True
                return
            self._sig.append(z3.Const(name, sort))
            self._arg.append(z3.Var(i, sort))

        # compute pysmt version of the signature
        mgr = self._env.formula_manager
        converter = pyz3.Z3Converter(self._env, self.get_ctx())
        # noinspection PyProtectedMember
        self._pysmt_sig = [
            mgr.Symbol(v.decl().name(), converter._z3_to_type(v.sort()))
            for v in self._sig
        ]

    def _mk_arg_name(self, i):
        # can be arbitrary convenient name
        return "{}_{}_n".format(self.name(), i)

    def _mk_lemma_arg_name(self, i):
        # must match name used in the lemma
        return "{}_{}_n".format(self.name(), i)

    def name(self):
        return str(self._fdecl.name())

    def __str__(self):
        return repr(self)

    def __repr__(self):
        import io

        out = io.StringIO()
        out.write(str(self.name()))
        out.write("(")
        for v in self._pysmt_sig:
            out.write(str(v))
            out.write(", ")
        out.write(")")
        return out.getvalue()

    def _mk_lemma_parser(self):
        if self._lemma_parser is not None:
            return
        self._lemma_parser = SmtLibZ3Parser()
        # register symbols that are expected to appear in the lemma
        for i, symbol in enumerate(self._pysmt_sig):
            name = self._mk_lemma_arg_name(i)
            self._lemma_parser.cache.bind(name, symbol)

    def pysmt_parse_lemma(self, lemma):
        self._mk_lemma_parser()
        tokens = Tokenizer(lemma, interactive=False)
        return self._lemma_parser.get_expression(tokens)

    def get_ctx(self):
        return self._fdecl.ctx

    def decl(self):
        return self._fdecl

    def num_args(self):
        return len(self._sig)

    def args(self):
        return self._arg

    def arg(self, i):
        return self._arg[i]

    def sigs(self):
        return self._sig
    
    def sig(self, i):
        return self._sig[i]


class HornClauseDb(object):
    def __init__(self, name="horn", smtlib_str=None, simplify_queries=True, ctx=z3.main_ctx(), env=None):
        self._ctx = ctx
        self._name = name
        self._smtlib_str = smtlib_str
        self._rules = []
        self._facts = []
        self._queries = []
        self._rels_set = frozenset()
        self._rels = dict()
        self._sealed = True
        self._fp = None
        self._env = env
        self._simple_query = simplify_queries
        self._idx_count = 0
        # self.trivial_rel_names = ['verifier.error', 'main@entry']
        self.trivial_rel_names = []


    def add_rule(self, horn_rule):
        assert self._ctx == horn_rule.get_ctx()
        self._sealed = False
        if horn_rule.head().decl().name() in self.trivial_rel_names:
            # skip trivial rules
            return

        for body_app in horn_rule.body():
            if body_app.decl().name() in self.trivial_rel_names:
                horn_rule = substitute(horn_rule, HornRelation(body_app.decl()), Z3_TRUE)

        self._idx_count += 1
        horn_rule.add_idx(self._idx_count)

        if horn_rule.is_query():
            if self._simple_query and not horn_rule.is_simple_query():
                query, rule = horn_rule.split_query()
                self._rules.append(rule)
                self._queries.append(query)
            else:
                self._queries.append(horn_rule)
        elif horn_rule.is_fact():
            self._rules.append(horn_rule)
            self._facts.append(horn_rule)
        else:
            self._rules.append(horn_rule)

    def rewrite(self):
        for r in self._rules:
            r.rewrite()

    def get_rels(self):
        self.seal()
        return self._rels

    def get_rels_list(self):
        return list(self.get_rels().values())

    def get_smtlib_str(self):
        return self._smtlib_str

    def has_rel(self, rel_name):
        return rel_name in self._rels.keys()

    def get_rel(self, rel_name):
        """Return a HornRelation object"""
        return self._rels[rel_name]

    def get_rules(self):
        return self._rules

    def get_facts(self):
        return self._facts

    def get_queries(self):
        return self._queries

    def seal(self):
        if self._sealed:
            return

        rels = list()
        for r in self._rules:
            rels.extend(r.used_rels())
        for q in self._queries:
            rels.extend(q.used_rels())
        self._rels_set = frozenset(rels)  # decl
        self._sealed = True

        for rel in self._rels_set:
            self._rels[str(rel.name())] = HornRelation(rel, env = self._env)

    def __str__(self):
        out = io.StringIO()
        for r in self._rules:
            out.write(f'Index: {r.get_idx()}\nRule: {r}')
            out.write("\n")
        out.write("\n")
        for q in self._queries:
            out.write(str(q))
        return out.getvalue()

    def load_from_fp(self, fp, queries):
        assert fp.ctx == self._ctx
        self._fp = fp
        if len(queries) > 0:
            for r in fp.get_rules():
                rule = HornRule(r)
                self.add_rule(rule)
            for q in queries:
                rule = HornRule(z3.Implies(q, False))
                self.add_rule(rule)
        else:
            # fixedpoint object is not properly loaded, ignore it
            self._fp = None
            for a in fp.get_assertions():
                rule = HornRule(a)
                self.add_rule(rule)
        self.seal()

    def has_fixedpoint(self):
        return self._fp is not None

    def get_fixedpoint(self):
        return self._fp

    def mk_fixedpoint(self, fp=None):
        if fp is None:
            self._fp = z3.Fixedpoint(ctx=self._ctx)
            fp = self._fp

        fp_ctx = fp.ctx
        if fp_ctx == self._ctx:
            def trans(x):
                return x
        else:
            def trans(x):
                return x.translate(fp_ctx)

        for rel in self._rels_set:
            fp.register_relation(trans(rel))
        for r in self._rules:
            if r.has_formula():
                fp.add_rule(trans(r.get_formula()))
            else:
                fp.add_rule(trans(r.mk_formula()))

        return fp

    def get_ctx(self):
        return self._ctx

    def solve_chc_system(self):
        s = z3.Solver()
        for rule in self._rules:
            if not rule.has_formula():
                f = rule.mk_formula()
            else:
                f = rule.get_formula()
            s.add(f)

        for rule in self._queries:
            if not rule.has_formula():
                f = rule.mk_formula()
            else:
                f = rule.get_formula()
            s.add(f)

        res = s.check()
        model = None
        if res == z3.sat:
            model = s.model()
        return res, model

    def find_cex(self, rules: list=None):
        """If one of the negated rules are SAT, one cex can be found
           All the negated rules are UNSAT, the CHC system is SAT"""

        if rules is None:  # find cex in all rules, otherwise in a subset of rules
            rules = self._rules

        # shallow copy here may lead to issues, deepcopy is not available
        for rule in rules:
            s = z3.Solver()
            s.add(rule.body())
            s.add(z3.Not(rule.head()))

            for q in self._queries:  # add sq -> False as a hard constraint
                if not q.has_formula():
                    q_f = q.mk_formula()
                else:
                    q_f = q.get_formula()
                s.add(q_f)

            res = s.check()
            model = None
            if res == z3.sat:
                model = s.model()
                break
        
        return res, model


class DoubleChecker:
    """
    Double check the result of the learner
    """
    def __init__(self, file_name, logger):
        self.solver = z3.Solver()
        self.solver.set(timeout=120000)
        db = load_horn_db_from_file(file_name, original=True)
        self.rules = list(reversed(db.get_rules()))  # "query" is always trivial
        self.rels = list(reversed(db.get_rels_list()))
        self.rel_decls = [r.decl() for r in self.rels]
        self.logger = logger
        self.free_vars_prefix = 'Var_'  # None for v1 and v2


    def get_def(self, rule, cand_map, rel=None):
        """Substitute rels in rule with expressions in self.cand_map
           rel: HornRelation"""
        from utils.la_utils import substitute
        if rel is None:  # substitute all rels
            body, head = substitute(rule, self.rel_decls, cand_map, self.free_vars_prefix)
            return body, head
        r_decl = rel.decl()
        body, head = substitute(rule, [r_decl], {r_decl: cand_map[r_decl]}, self.free_vars_prefix)
        return body, head

    def solve_negated_rule(self, rule_body, rule_head):
        """Solve negated rule to get cex"""
        self.solver.reset()
        self.solver.add(rule_body)
        self.solver.add(z3.Not(rule_head))
        
        res = self.solver.check()
        model = None
        if res == z3.sat:
            model = self.solver.model()

        return res, model
    
    def check(self, cand_map):
        is_correct = True
        for r in self.rules:
            r_cand_b, r_cand_h = self.get_def(r, cand_map)
            res, _ = self.solve_negated_rule(r_cand_b, r_cand_h)
            if res == z3.sat:
                self.logger.warning(f'Rule Index {r.get_idx()} is problematic')
                is_correct = False
            elif res == z3.unknown:
                is_correct = False
                raise RuntimeError('Z3 returns unknown (DoubleChecker solve_negated_rule)')
        return is_correct


def ground_quantifier(qexpr):
    body = qexpr.body()

    var_list = list()
    for i in reversed(range(qexpr.num_vars())):
        vi_name = qexpr.var_name(i)
        vi_sort = qexpr.var_sort(i)
        vi = z3.Const(vi_name, vi_sort)
        var_list.append(vi)

    body = z3.substitute_vars(body, *var_list)
    return body, var_list


def find_all_uninterp_consts(formula, res):
    """
    find applications like "itp(Var(0), Var(1))" and extract decl like "itp" 
    """
    if z3.is_quantifier(formula):  # remove quantifier
        formula = formula.body()

    worklist = []
    if z3.is_implies(formula):
        worklist.append(formula.arg(1))
        arg0 = formula.arg(0)
        if z3.is_and(arg0):
            worklist.extend(arg0.children())
        else:
            worklist.append(arg0)
    else:
        worklist.append(formula)

    for t in worklist:
        if z3.is_app(t) and t.decl().kind() == z3.Z3_OP_UNINTERPRETED:
            res.append(t.decl())


def load_horn_db_from_file(fname='tests/code2inv-nl/nl-1-chc.smt2',
                           context=z3.main_ctx(), env=None, original=False):
    f = open(fname)
    smtlib_str = f.read()
    if smtlib_str.find('(query false)') != -1 or len(smtlib_str) < 5:
        return None

    fp = z3.Fixedpoint(ctx = context)
    queries = fp.parse_file(fname)
    if not original:
        db = HornClauseDb(fname, smtlib_str, ctx = context, env = env)
    else:
        db = OriginalHornClauseDb(fname, ctx = context, env = env)
    db.load_from_fp(fp, queries)
    # print("Queries:")
    # print(queries)
    return db


def solve_substituted_chc_system(expr, rel_name='itp', file="tests/code2inv-nl/nl-1-chc.smt2"):
    """
    Substitute unknown predicate with an expr and solve the CHC system
    """
    db = load_horn_db_from_file(file, z3.main_ctx())
    # print("db", db)
    # print("db_get_rels", db.get_rels())
    # print("db_rels", db._rels)
    # print("db_rules", db.get_rules())
    rel = db.get_rel(rel_name)

    db_sub = HornClauseDb()
    rules = db.get_rules()
    queries = db.get_queries()
    for rule in rules:
        new_rule = substitute(rule, rel, expr)
        db_sub.add_rule(new_rule)
    
    for rule in queries:
        new_rule = substitute(rule, rel, expr)
        db_sub.add_rule(new_rule)
    
    res, model = db_sub.find_cex()
    return res, model