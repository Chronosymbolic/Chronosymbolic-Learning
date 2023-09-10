import time
import eventlet
import traceback
import z3

def run_Agent(Agent, main_logger):
    """
    main control flow, 
    return if it is successfully verified
    """

    if Agent.is_not_supported:  # skip array arg type and chc with too many relations
        Agent.logger.warning(f'************** Not supported! Skipped. **************')
        main_logger.info(f'************** Not supported! Skipped. **************')
        return False, False, False

    is_changed = True
    is_fail = False
    is_terminated = False
    bug_not_exists = True
    counter = 0
    start_time = time.time()
    try:
        while is_changed:
            counter += 1
            Agent.logger.warning(f'Episode No.{counter}')
            is_changed = False
            bug_not_exists, is_changed = Agent.solve_constraints()
            if not bug_not_exists:
                break
    except eventlet.timeout.Timeout:
        Agent.logger.warning(f'Solving instance timeout!')
        main_logger.info(f'Solving instance timeout!')
        is_fail = True
    except KeyboardInterrupt as e:
        Agent.logger.warning(f'Error {type(e)}: {e}')
        is_fail = True
        is_terminated = True
    except Exception as e:
        traceback.print_exc()
        Agent.logger.warning(f'Error {type(e)}: {e}')
        main_logger.info(f'Error {type(e)}: {e}')
        is_fail = True
        if str(e).find('Z3 returns unknown') != -1:
            Agent.aux_info['Unsolved Last Constraint'] = str(Agent.solver)


    # Print time stats
    elapsed_time = time.time() - start_time
    if Agent.init_phase_time > 166000000:  # init phase interrupted
        Agent.init_phase_time = time.time() - Agent.init_phase_time
    Agent.logger.warning(f'************** Finished in {elapsed_time} (secs) in {counter} epochs **************')
    main_logger.info(f'************** Finished in {elapsed_time} (secs) in {counter} epochs **************')
    other_time = elapsed_time - Agent.svm_time - Agent.dt_time - Agent.z3_time
    Agent.logger.warning(f'Total SVM Calls: {Agent.svm_calls}, DT Calls: {Agent.dt_calls}, Z3 Calls: {Agent.z3_calls}')
    Agent.logger.warning(f'Total SVM Time: {Agent.svm_time}, DT Time: {Agent.dt_time}, Z3 Time: {Agent.z3_time}')
    Agent.logger.warning(f'Others: {other_time}, Init Phase Time: {Agent.init_phase_time}, Simplifier Solver Time: {Agent.eq_solver_time}')
    main_logger.info(f'Total SVM Calls: {Agent.svm_calls}, DT Calls: {Agent.dt_calls}, Z3 Calls: {Agent.z3_calls}')
    main_logger.info(f'Total SVM Time: {Agent.svm_time}, DT Time: {Agent.dt_time}, Z3 Time: {Agent.z3_time}')
    main_logger.info(f'Others: {other_time}, Init Phase Time: {Agent.init_phase_time}, Simplifier Solver Time: {Agent.eq_solver_time}')
    
    # Print auxiliary information
    if len(Agent.aux_info) > 0:
        Agent.logger.warning('************** Auxiliary Info **************')
        main_logger.info('************** Auxiliary Info **************')
        for infomk, infomv in Agent.aux_info.items():
            Agent.logger.warning(f'{infomk}: {infomv}')
            main_logger.info(f'{infomk}: {infomv}')

    # Print result
    if bug_not_exists and not is_fail:
        Agent.logger.warning('************** Program is correct **************')
        main_logger.info('************** Program is correct **************')
        for rel, cand in Agent.cand_map.items():
            Agent.logger.warning(f'\nRelation: {rel}, \nCandidate: {cand}')
            main_logger.info(f'\nRelation: {rel}, \nCandidate: {cand}')
    elif is_fail:
        Agent.logger.warning(f'************** Program Verification Failed **************')
        main_logger.info(f'************** Program Verification Failed **************')
        return False, is_terminated, bug_not_exists
    elif not bug_not_exists:
        Agent.logger.warning(f'************** Program is BUGGY **************')
        main_logger.info(f'************** Program is BUGGY **************')
    
    return True, is_terminated, bug_not_exists

def test_solve_ctr(Agent):
    Agent.solve_constraints()

def test_SVM_C5(Agent):
    # test svm_learn
    db = Agent.db
    itp = db.get_rel('itp')
    Agent.pos_data_set.add_dp(itp, [0, 0])
    Agent.pos_data_set.add_dp(itp, [1, 1])

    Agent.neg_data_set.add_dp(itp, [251, 1001])
    Agent.neg_data_set.add_dp(itp, [310, 1036])
    Agent.neg_data_set.add_dp(itp, [557, 1013])
    Agent.neg_data_set.add_dp(itp, [11, 1])
    Agent.neg_data_set.add_dp(itp, [1, -1])
    Agent.neg_data_set.add_dp(itp, [-1, 1])
    Agent.neg_data_set.add_dp(itp, [0, 1])
    Agent.neg_data_set.add_dp(itp, [16, -14])
    # Agent.svm_learn([itp])
    Agent.C5_learn()

def test_data_structure(Agent):
    db = Agent.db
    q = db.get_queries()
    d = q[0].body()[0].decl()
    d = list(q[0].used_rels())[0]

    r = db.get_rules()[1]
    r_head = r.head()
    is_c = z3.is_const(r_head.arg(0))
    
    new_b, new_h = Agent.get_def(r)
    m = Agent.cand_map[d]