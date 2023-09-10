import os
import sys
p = os.path.abspath('.')
sys.path.insert(1, p)

import pandas as pd
import pysmt
import z3
from utils.la_utils import find_fact_rel, find_query_rel
from horndb.horndb import load_horn_db_from_file


dir_name = 'tests/freqhorn/bench_horn_cex'
csv_file = 'bench_horn_cex.csv'


def is_nl(rules):
    # return True: have nl chcs
    has_nl = False
    for r in rules:
        if not r.is_linear():
            has_nl = True
            print(r)
    return has_nl


def get_num_args(rels):
    arg_num = 0
    for rel in rels:
        args = rel.num_args()
        arg_num += args
    return arg_num


def get_max_rule_len(rules):
    max_rule_len = 0
    for rule in rules:
        rule_len = len(str(rule))
        max_rule_len = rule_len if rule_len > max_rule_len else max_rule_len
    return max_rule_len


file_names = []
is_nls = []
rule_nums = []
rel_nums = []
arg_nums = []  # total arg num in predicates
db_lens = []
max_rule_lens = []


dir_name = dir_name.rstrip('/')
total_files = 0
g = os.walk(dir_name)
for _, _, file_list in g:
    file_list = sorted(file_list)
    for i, file_name in enumerate(file_list):
        if not file_name.endswith('.smt') and not file_name.endswith('.smt2'):
            continue

        total_files += 1
        path_file = dir_name + '/' + file_name
        file_names.append(file_name)

        print(f'======== File No.{i+1}/{len(file_list)}: {path_file} ========')

        pysmt.environment.reset_env()  # important!
        db = load_horn_db_from_file(path_file, z3.main_ctx())

        rules = db.get_rules()
        rels = db.get_rels_list()
        nl = is_nl(rules)
        rule_num = len(list(rules))
        rel_num = len(rels)
        arg_num = get_num_args(rels)
        db_len = len(str(db))
        max_rule_len = get_max_rule_len(rules)

        is_nls.append(nl)
        rule_nums.append(rule_num)
        rel_nums.append(rel_num)
        arg_nums.append(arg_num)
        db_lens.append(db_len)
        max_rule_lens.append(max_rule_len)


df = pd.DataFrame({
    'file_names': file_names,
    'is_NL': is_nls,
    'rule_nums': rule_nums,
    'rel_nums': rel_nums,
    'arg_nums': arg_nums,
    'db_lens': db_lens,
    'max_rule_lens': max_rule_lens
})
print(df.describe())
df.to_csv(csv_file)
