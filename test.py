import sys
import z3
from horndb.horndb import load_horn_db_from_file
from horndb.original_horndb import OriginalHornClauseDb
from utils.la_utils import substitute, load_yaml, double_check
from learner.learner import DataDrivenLearner
from learner.learner_v2 import DataDrivenLearner_v2
from learner.chronosymbolic import Chronosymbolic
from learner.run_agent import run_Agent
from utils.dt.dt import SklearnDT, C5DT
import argparse
import logging
import os
import yaml
import pandas as pd

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)
import eventlet

import time
from datetime import datetime
import pysmt.environment
import logging


# --- Set agent and DT algorithm here ---
ClassAgent = Chronosymbolic
# ClassAgent = DataDrivenLearner  # LinearArbitrary like
# ClassAgent = DataDrivenLearner_v2  # LinearArbitrary like, optimized

ClassDT = C5DT  # C5.0
# ClassDT = SklearnDT  # CART
# --- Set agent and DT algorithm here ---


def guess_manually(args):
    """
    An example of manually setting invariants and checking
    """
    db = load_horn_db_from_file(args.file_name, original=True)
    print("db", db)

    print("db_rels", db.get_rels())
    print("db_rules", db.get_rules())
    # rel = db.get_rel("itp")
    rel = db.get_rel("main_1")
    rel_q = db.get_rel("simple!!query")

    v_0 = z3.Var(0, z3.IntSort())
    expr = v_0 <= 1
    expr_false = z3.BoolVal(False)

    db_sub = OriginalHornClauseDb()
    rules = db.get_rules()
    queries = db.get_queries()
    for rule in rules:
        new_rule = substitute(rule, rel, expr)
        new_rule = substitute(new_rule, rel_q, expr_false)
        db_sub.add_rule(new_rule)
    
    for rule in queries:
        new_rule = substitute(rule, rel, expr)
        new_rule = substitute(new_rule, rel_q, expr_false)
        db_sub.add_rule(new_rule)
    
    res, model = db_sub.find_cex()
    # res, model = db_sub.find_cex([db_sub.get_rules()[1]])
    # cex = model[0]
    print(res, model)
    return


def run_single_file(args, logger, agent_params):
    db = load_horn_db_from_file(fname=args.file_name)
    if db is None:
        logger.warning('Trivial case, skip (this program is correct)\n\n')
        sys.exit()
    
    Agent = ClassAgent(db, agent_params, ClassDT, log_path=args.log)

    if not args.verbose and not sys.gettrace():  # not in debug mode
        Agent.logger.setLevel(logging.INFO)
    Agent.logger.info(f'SMTLIB File Name: {os.path.abspath(args.file_name)}')
    Agent.logger.info(f'Log File Name: {os.path.abspath(args.log)}')

    is_successful, _, is_correct = run_Agent(Agent, logger)
    if is_correct and is_successful:
        learner_cand_map = None if Agent.__class__.__name__ != 'Chronosymbolic' else Agent.learner_cand_map
        _ = double_check(args.file_name, logger, Agent.cand_map, learner_cand_map, Agent.free_vars_prefix)


def run_dir_mode(args, logger, agent_params):
    dir_name = args.file_name.rstrip('/')
    log_path = 'log/' + dir_name.lstrip('/').split('/')[-1]
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    fail = 0
    fail_files = []
    file_names = []
    time_elapsed_all = []
    stat_flags = []
    total_time = 0
    total_files = 0
    file_name_suffix = datetime.now().strftime("%y%m%d_%H%M%S")

    g = os.walk(args.file_name)
    for _, _, file_list in g:
        file_list = sorted(file_list)  # fixed order of processing, easy to compare
        for i, file_name in enumerate(file_list):
            if not file_name.endswith('.smt') and not file_name.endswith('.smt2'):
                continue
            if i < args.start_from:  # run from breakpoint, start from args.start_from (idx starts from 0)
                continue
            total_files += 1
            file_names.append(file_name)
            path_file = dir_name + '/' + file_name
            log_path_file = log_path + '/' + file_name +'.log'
            logger.warning(f'======== File No.{i+1}/{len(file_list)} ({total_files-1-fail} succeeded): {os.path.abspath(path_file)} ========')

            start_time = time.time()
            pysmt.environment.reset_env()  # important!
            db = load_horn_db_from_file(fname=path_file)
            load_time = time.time() - start_time
            file_size = os.path.getsize(path_file) / float(1024)
            logger.warning(f'********* SMT2 Loading time: {load_time} secs, Size: {file_size:.2f}KB **********')
            if db is None:
                logger.warning('Trivial case, skip (this program is correct)\n\n')
                total_time += time.time() - start_time
                continue
            
            Agent = ClassAgent(db, agent_params, ClassDT, log_path=log_path_file,
                               file_name_suffix=file_name_suffix)

            if not args.verbose:
                Agent.logger.setLevel(logging.INFO)
            Agent.logger.info(f'SMTLIB File Name: {os.path.abspath(path_file)}')
            Agent.logger.info(f'Log File Name: {os.path.abspath(log_path_file)}')
            logger.info(f'Log File Name: {os.path.abspath(log_path_file)}')

            is_successful = True
            is_terminated = False
            is_correct = True
            eventlet.monkey_patch()
            with eventlet.Timeout(args.timeout):
                is_successful, is_terminated, is_correct = run_Agent(Agent, logger)
            stat_flags.append((is_successful, is_correct))

            if not is_successful:
                fail_files.append(os.path.abspath(path_file))
                fail += 1
            time_elapsed = time.time() - start_time
            total_time += time_elapsed
            time_elapsed_all.append(time_elapsed)
            
            if is_correct and is_successful:
                learner_cand_map = None if Agent.__class__.__name__ != 'Chronosymbolic' else Agent.learner_cand_map
                _ = double_check(path_file, logger, Agent.cand_map, learner_cand_map, Agent.free_vars_prefix)
            
            logger.warning('\n\n')

            if is_terminated:
                break
        
        logger.warning(f'********* Total time elapsed: {total_time // 60:0f} mins {total_time % 60:0f} secs **********')
        logger.warning(f'********* Successfully solved: {total_files-fail}/{total_files} **********')
        logger.warning('Fail to solve:')
        for ff in fail_files:
            logger.warning(ff)
        
        if args.csv:
            df = pd.DataFrame({
            'file_names': file_names,
            'time': time_elapsed_all,
            'is_successful': [int(flag[0]) for flag in stat_flags],
            'is_correct': [int(flag[1]) for flag in stat_flags],
            })
            csv_name = args.result.split('.')[0]+'.csv'
            df.to_csv(csv_name)
            logger.warning(f'Result stat saved to csv: {csv_name}')


def run_filelist_mode(args, logger, agent_params):
    dir_name = args.file_name.rstrip('/')
    log_path = 'log/' + dir_name 
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    fail = 0
    fail_files = []
    file_names = []
    time_elapsed_all = []
    stat_flags = []
    total_time = 0
    total_files = 0
    file_name_suffix = datetime.now().strftime("%y%m%d_%H%M%S")

    with open(args.file_name, 'r') as f:
        file_list = f.readlines()
    file_list = sorted(file_list)  # fixed order of processing, easy to compare
    for i, file_name in enumerate(file_list):
        file_name = file_name.strip()
        if file_name.startswith('#'):
            continue
        if not file_name.endswith('.smt') and not file_name.endswith('.smt2'):
            continue
        if i < args.start_from:  # run from breakpoint, start from args.start_from (idx starts from 0)
            continue

        total_files += 1
        file_name_last = file_name.split('/')[-1]
        file_names.append(file_name_last)
        log_path_file = log_path + '/' + file_name_last +'.log'
        logger.warning(f'======== File No.{i+1}/{len(file_list)} ({total_files-1-fail} succeeded): {os.path.abspath(file_name)} ========')

        start_time = time.time()
        pysmt.environment.reset_env()  # important!
        db = load_horn_db_from_file(fname=file_name)
        load_time = time.time() - start_time
        file_size = os.path.getsize(file_name) / float(1024)
        logger.warning(f'********* SMT2 Loading time: {load_time} secs, Size: {file_size:.2f}KB **********')
        if db is None:
            logger.warning('Trivial case, skip (this program is correct)\n\n')
            total_time += time.time() - start_time
            continue

        Agent = ClassAgent(db, agent_params, ClassDT, log_path=log_path_file,
                           file_name_suffix=file_name_suffix)

        if not args.verbose:
            Agent.logger.setLevel(logging.INFO)
        Agent.logger.info(f'SMTLIB File Name: {os.path.abspath(file_name)}')
        Agent.logger.info(f'Log File Name: {os.path.abspath(log_path_file)}')
        logger.info(f'Log File Name: {os.path.abspath(log_path_file)}')

        is_successful = True
        is_terminated = False
        is_correct = True
        eventlet.monkey_patch()
        with eventlet.Timeout(args.timeout):
            is_successful, is_terminated, is_correct = run_Agent(Agent, logger)
        stat_flags.append((is_successful, is_correct))

        if not is_successful:
            fail_files.append(os.path.abspath(file_name))
            fail += 1
        time_elapsed = time.time() - start_time
        total_time += time_elapsed
        time_elapsed_all.append(time_elapsed)

        
        if is_correct and is_successful:
            learner_cand_map = None if Agent.__class__.__name__ != 'Chronosymbolic' else Agent.learner_cand_map
            _ = double_check(file_name, logger, Agent.cand_map, learner_cand_map, Agent.free_vars_prefix)
        
        logger.warning('\n\n')

        if is_terminated:
            break
        
    logger.warning(f'********* Total time elapsed: {total_time // 60:0f} mins {total_time % 60:0f} secs **********')
    logger.warning(f'********* Successfully solved: {total_files-fail}/{total_files} **********')
    logger.warning('Fail to solve:')
    for ff in fail_files:
        logger.warning(ff)

    if args.csv:
        df = pd.DataFrame({
            'file_names': file_names,
            'time': time_elapsed_all,
            'is_successful': [int(flag[0]) for flag in stat_flags],
            'is_correct': [int(flag[1]) for flag in stat_flags],
            })
        csv_name = args.result.split('.')[0]+'.csv'
        df.to_csv(csv_name)
        logger.warning(f'Result stat saved to csv: {csv_name}')



if __name__ == "__main__":    
    # sys.exit(guess_manually())
    file_name = 'tests/simple_smt/10000.smt2'  # for testing functionality

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_name', help='SMTLIB File Name or dir name', default=file_name)
    parser.add_argument('-s', '--start_from', help='start from file index n (idx starts from 0)', type=int, default=0)
    parser.add_argument('-c', '--config', help='config file path', default='config.yml')
    parser.add_argument('-l', '--log', help='log file path', default='log.log')
    parser.add_argument('-o', '--result', help='result file path', default='result/result.log')
    parser.add_argument('-a', '--csv', help='whether export a csv of results', action='store_true')
    parser.add_argument('-v', '--verbose', help='increase output log file verbosity', action='store_true')
    parser.add_argument('-b', '--filelist', help='filelist (batch) mode, load files that in the filelist', action='store_true')
    parser.add_argument('-r', '--dir', help='directory mode, run all files in this directory', action='store_true')
    parser.add_argument('-t', '--timeout', help='timeout time (sec) on solving an instance, only effective in dir mode', type=int, default=100)
    args = parser.parse_args()

    logger = logging.getLogger(args.result)
    logger.setLevel(logging.DEBUG)
    
    sh = logging.StreamHandler()
    sh.setLevel(logging.WARNING)
    formatter = logging.Formatter(fmt='%(message)s')
    sh.setFormatter(formatter)
    if args.dir or args.filelist:
        fh = logging.FileHandler(args.result, mode='w')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    logger.addHandler(sh)

    logger.warning(f'{ClassAgent.__name__}\n')
    logger.warning(f'{ClassDT.__name__}\n')
    agent_params = load_yaml(args.config)
    logger.warning(f'--------- Hyperparameters ---------\n{yaml.dump(agent_params, default_flow_style=False)}')
    logger.warning('--------- CHC Solving ---------\n')

    if not agent_params['LOGGING']:
        sh.setLevel(logging.INFO)

    if not args.dir and not args.filelist:
        run_single_file(args, logger, agent_params)
    
    elif args.dir:  # dir mode
        run_dir_mode(args, logger, agent_params)
    
    else:
        run_filelist_mode(args, logger, agent_params)
