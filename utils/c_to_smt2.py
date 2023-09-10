# seahorn required
import os
src = '/seahorn/seahorn/G-CLN/benchmarks/code2inv/c_processed/'
target = '/seahorn/seahorn/G-CLN/benchmarks/code2inv/smt2_seahorn/'

if not os.path.exists(target):
    os.makedirs(target)

g = os.walk(src)
for _, _, file_list in g:
    for file_name in file_list:
        cmd = "/seahorn/seahorn/build/run/bin/sea smt " + src + file_name + " -o " + target + file_name + ".smt2"
        print("command executed: "+cmd)
        os.system(cmd)
