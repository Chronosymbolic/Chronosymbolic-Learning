## result_safe_summary.log and result_unsafe_summary.log
The logs are the running logs of our reported experiment on ``Chronosymbolic-single''. This experiment runs a suite of instances using a fixed set of hyperparameters.

The structure of the log is as follows:

1. The first 2 lines are the modules used.

2. The "Hyperparameters" section shows all the hyperparameters in `config.yml`.

3. The "CHC Solving" part shows the results of solving all instances in the test suite. For each instance, it shows the file names, the size of the `*.smt2` or `*.smt` instance, the overall running time and time of each component, auxiliary info generated when running our tool (not important), the satisfiability of the CHC (correctness of corresponding program) and the proof (solution interpretation of predicates), and the double check procedure ensuring the correctness of the proof. The figure below shows the detailed explanation of this part of log.

![log](https://github.com/Chronosymbolic/Chronosymbolic-Learning/blob/main/experiment/log_explanation.png)

4. At the end of the log, it shows the total time elapsed and the number of solved instances. It also provides a list of instances that our tool cannot solve.

The specifications of the device used to generate this log:

- Processor 12th Gen Intel(R) Core(TM) i7-12700H   2.30 GHz

- Installed RAM 32.0 GB (31.7 GB usable)
  
- System type: 64-bit operating system, x64-based processor


## comparison.xlsx
Detailed running time data on our major performance evaluation in the experiment section of our paper.

## result_rnd_seed.xlsx
Detailed running time data on our performance evaluation with different random seeds is described in the Appendix of the paper. We only show safe instances as an example. In `result_rnd_seed_gini.xlsx`, the only difference is to use Gini impurity instead of Shannon Entropy in DTs.

## To reproduce Chronosymbolic-cover
We provide essential experiments needed to run to reproduce the result:

1. Different strategies on scheduling the candidate hypothesis in Table 1 of our paper (e.g., tuning the hyperparameters in `SafeZoneUsage: '(self.total_iter // 200) % 2 == 0', UnsafeZoneUsage: '(self.total_iter // 100) % 2 == 0`);
2. Using different DT settings (may try random DT as well that may not work well overall but works on some specific instances) and Agents (set in `./test.py`);
3. Different dataset settings (enable the queue mode or not, how many samples should the datasets keep);
4. Different expansion strategy for the reasoner (`Expansion` in `./config.yml`).

## To reproduce results of CHC-COMP-22-LIA
The default settings in `./config.yml` should be decent (might be a little bit worse than the best result but within 5%). Note that, if the timeout malfunctions for some instances, interrupt the tool manually and use the `-s K` option starting from the file index `K` in the folder.
