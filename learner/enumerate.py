import os
import sys

p = os.path.abspath('.')
sys.path.insert(1, p)

import z3
import itertools
import sys
import time
from nltk.grammar import Nonterminal
from horndb.horndb import solve_substituted_chc_system


def generate(grammar, start=None, depth=None, n=None):
    """
    Generates an iterator of all sentences from a CFG.

    :param grammar: The Grammar used to generate sentences.
    :param start: The Nonterminal from which to start generate sentences.
    :param depth: The maximal depth of the generated tree.
    :param n: The maximum number of sentences to return.
    :return: An iterator of lists of terminal tokens.
    """
    if not start:
        start = grammar.start()
    if depth is None:
        depth = sys.maxsize

    iter = _generate_all(grammar, [start], depth)

    if n:
        iter = itertools.islice(iter, n)

    return iter


def _generate_all(grammar, items, depth):
    if items:
        try:
            if len(items) > 1 and (items[1].__str__() == "Bop"):
                Bop = items[1]
                # for op in _generate_one(grammar, Bop, depth):
                #     if op[0] == "and":
                for BE in _generate_one(grammar, items[0], depth - 1):
                    for BE2 in _generate_one(grammar, items[2], depth - 1):
                        exp = z3.simplify(z3.And(BE[0], BE2[0]))
                        # print(exp)
                        yield [exp]
                        exp = z3.simplify(z3.Or(BE[0], BE2[0]))
                    # if op[0] == "or":
                    #     for BE in _generate_one(grammar, items[0], depth - 1):
                    #         for BE2 in _generate_one(grammar, items[2], depth - 1):
                    #             exp = z3.simplify(z3.Or(BE[0], BE2[0]))
                    #             # print(exp)
                        yield [exp]
            if len(items) > 1 and (items[1].__str__() == "cop"):

                # cop = items[1]
                # for op in _generate_one(grammar, cop, depth):
                #     if op[0] == "==":
                for BE in _generate_one(grammar, items[0], depth - 1):
                    for BE2 in _generate_one(grammar, items[2], depth - 1):
                        exp = z3.simplify(z3.And(BE[0] == BE2[0]))
                        # print(exp)
                        yield [exp]
                    # if op[0] == "<=":
                    #     for BE in _generate_one(grammar, items[0], depth - 1):
                    #         for BE2 in _generate_one(grammar, items[2], depth - 1):

                        exp = z3.simplify(z3.And(BE[0] <= BE2[0]))
                        # print(exp)
                        yield [exp]
            if len(items) > 1 and (items[1].__str__() == "mul"):
                mul = items[1]
                for op in _generate_one(grammar, mul, depth):
                    if op[0] == "*":
                        for BE in _generate_one(grammar, items[0], depth - 1):
                            for BE2 in _generate_one(grammar, items[2], depth - 1):
                                exp = z3.simplify((BE[0] * BE2[0]))
                                # print(exp)
                                yield [exp]
            if len(items) > 1 and (items[1].__str__() == "op"):
                for BE in _generate_one(grammar, items[0], depth - 1):
                    for BE2 in _generate_one(grammar, items[2], depth - 1):
                        exp = (BE[0] * BE2[0])
                        # print(exp)
                        yield [exp]
                        exp = (BE[0] + BE2[0])
                        # print(exp)
                        yield [exp]

            else:
                if (len(items) == 1):
                    yield from _generate_one(grammar, items[0], depth)
        except RecursionError as error:
            # Helpful error message while still showing the recursion stack.
            raise RuntimeError(
                "The grammar has rule(s) that yield infinite recursion!"
            ) from error
    else:
        yield []


def _generate_one(grammar, item, depth):
    vars = [z3.Var(i, z3.IntSort()) for i in range(2)]
    if depth > 0:
        if isinstance(item, Nonterminal):
            for prod in grammar.productions(lhs=item):
                yield from _generate_all(grammar, prod.rhs(), depth - 1)
        else:
            type = checkType(item, vars)
            # print(item,type)
            # print("------")

            yield [type]


def checkType(string, vars):
    boolOps = ["==", "<="]
    intOps = ["+", "*"]
    # print(string)
    substring = "v_"
    if str == '0':
        return 0
    else:
        if str.isdigit(string):
            return int(string)
        if string.lstrip('-').isdigit():
            return int(string)
    if substring in string:
        if string == "v_0":
            return vars[0]
        if string == "v_1":
            return vars[1]
    return string


if __name__ == "__main__":
    import nltk

    # z3_exp = z3.Var(0, z3.IntSort())-z3.Var(1, z3.IntSort())*z3.Var(1, z3.IntSort())==0
    # r, s1 = solve_substituted_chc_system(z3_exp, file="tests/code2inv-nl/nl-1-chc.smt2")
    # print(r, s1)
    grammar = nltk.parse.load_parser('learner/grammars/inv2.cfg').grammar()
    start_time = time.time()
    for n, sent in enumerate(generate(grammar, n=10000, depth=None)):
        if n % 10 == 0:
            print(sent[0])

        r, s1 = solve_substituted_chc_system(
            sent[0], file="tests/code2inv-nl/nl-1-chc.smt2")

        if r == z3.unsat:
            print(s1)
            print(f'Result: {r}')
            print("%3d. %s" % (n, sent))
            exit()
    
    print(f'Failed to find the answer, time elapsed: {time.time()-start_time}')
