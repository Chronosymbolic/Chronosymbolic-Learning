import os
import time

src = 'tests/filtered_22'
z3_path = '/home/ssr/z3/build/z3'
# z3_path = 'utils/z3'
target = 'result/z3_gspacer_chc22_fil.log'

enable_global_guidance = 1  # GSpacer version of Z3 required
timeout = 360

enable_log = 1
if enable_log:
    file = open(target, "w")
    file.write(f'enable_global_guidance: {enable_global_guidance}\n\n')
    file.close()

higher_verbose = 0
print_stat = False
enable_skip = 1
print_proof = 1  # print invariant


if __name__ == "__main__":
    since = time.time()
    if enable_log:
        os.system("touch " + target)

    fail = 0
    fail_names = []
    counter = 0
    with open(src, 'r') as f:
        file_list = f.readlines()
    file_list = sorted(file_list)
    for i, file_name in enumerate(file_list):
        file_name = file_name.strip()
        if enable_skip:
            if file_name.find('#')!= -1:
                print("{}/{}, skipped file: {}".format(i+1, len(file_list), file_name))
                continue

        cmd = f"timeout -s SIGKILL {timeout} {z3_path} {os.path.abspath(file_name)} fp.engine=spacer 2>&1 "
        counter += 1

        if enable_global_guidance:
            cmd += " fp.spacer.global=true fp.spacer.concretize=true fp.spacer.conjecture=true fp.spacer.expand_bnd=true "
        if print_stat:
            cmd += " fp.print_statistics=true "
        if print_proof:
                cmd += " dump_models=true "
        if higher_verbose:
            # cmd += " -v:1 -tr:spacer "
            cmd += " -v:1  "
        if enable_log:
            with open(target, "a") as file:
                file.write(f"======== File No.{i+1}/{len(file_list)} ({counter-1-fail} succeeded), command executed: {cmd}\n")
            print(f"======== File No.{i+1}/{len(file_list)} ({counter-1-fail} succeeded), command executed: {cmd}")
        current_time = time.time()
        p = os.popen(cmd, 'r')
        buf = p.read()
        print(buf)
        with open(target, "a") as file:
            file.write(f'{buf}\n')

        if not (buf.find('sat') != -1 or buf.find('unsat') != -1):
            fail += 1
            fail_names.append(os.path.abspath(file_name))
        
        if enable_log:
            with open(target, "a") as file:
                file.write(f'************** Finished in {time.time()-current_time} (secs) **************\n\n')
        print(f'************** Finished in {time.time()-current_time} (secs) **************\n')

    time_elapsed = time.time() - since
    print_str = '\n'
    print_str += f'********* Total time elapsed: {time_elapsed // 60:0f} mins {time_elapsed % 60:0f} secs **********'
    print_str += f'\n********* Successfully solved: {counter-fail}/{counter} **********'
    print_str += f'\nFail to solve:'
    for f in fail_names:
        print_str += '\n' + f
    with open(target, "a") as file:
        file.write(print_str)
    print(print_str)