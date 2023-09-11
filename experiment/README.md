## result_summary_safe.log
The log shows the running log of our reported experiment on ``Chronosymbolic-single''. This experiment runs a suite of instances using a fixed set of hyperparameters. The structure of the log is as follows:

1. The first 2 lines are the modules used.

2. The "Hyperparameters" section shows all the hyperparameters in `config.yaml`.

3. The "CHC Solving" part shows the results of solving all instances in the test suite. For each instance, it shows the file names, the size of the `*.smt2` or `*.smt` instance, the overall running time and time of each component, auxiliary info generated when running our tool (not important), the satisfiability of the CHC (correctness of corresponding program) and the proof (solution interpretation of predicates), and the double check procedure ensuring the correctness of the proof.

4. At the end of the log, it shows the total time elapsed and the number of solved instances. It also provides a list of instances that our tool cannot solve.

The specifications of the device used to generate this log:
  Processor	12th Gen Intel(R) Core(TM) i7-12700H   2.30 GHz
  Installed RAM	32.0 GB (31.7 GB usable)
  System type	64-bit operating system, x64-based processor


## comparison.xlsx
Detailed running time data on our major performance evaluation in the experiment section.

## result_rnd_seed.xlsx
Detailed running time data on our performance evaluation with different random seeds is described in our Appendix.
