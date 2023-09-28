# Chronosymbolic Learning
Artifact for the paper "Chronosymbolic Learning: Efficient CHC Solving with Symbolic Reasoning and Inductive Learning"

- See `./experiment` for some significant results and configurations

- See `./examples` for examples of how our tool works

## Requirement (To set up our environment)
Python (3.7.0 or higher recommended, and [Anaconda](https://www.anaconda.com/) recommended to set up a new environment)

- Install packages in `requirements.txt`: `pip install -r requirements.txt`
    - Though not integrated in our artifact, you can also try to use [scikit-learn-intelex](https://intel.github.io/scikit-learn-intelex/latest/) to speed up CART DT if possible

- May have to manually set up `PYTHONPATH` and `PATH` properly,  `PYTHONPATH=$Z3_BIN/python`, `PATH=$PATH:$Z3_BIN`

- If the C5.0/LIBSVM binary cannot be executed properly, may have to recompile them in your OS and specify the binary executable files in `utils/dt/dt.py` in `class C5DT`, `C5_exec_path` and `utils/svm/svm.py` in `class LibSVMLearner`, `svm_exec_path`

## Chronosymbolic Learning
- Support SMT-LIB2 format (check-sat) and Datalog format (rule-query) 

- Have executable binaries of decision tree and SVM for Linux and MacOS, and can automatically adapt to the OS (Linux/Mac)

- Control flow implemented in `learner/run_agent.py` `run_Agent` function

- Hyperparameters in `config.yml`

- Temp files generated when calling decision tree and SVM are in `tmp/`

- Implemented some optimization for SMTLIB files generated by [SeaHorn](https://seahorn.github.io/)

- Run: `python test.py` with the parameters below:

    - Specify instance file name using `-f FILE_NAME` to run a single instance

    - Specify the log file (which records how the tool solves the CHC system) using `-l FILE_NAME`

    - Specify directory name using `-r -f DIR_NAME` to run a test suite (logs are automatically generated in log/DIR_NAME)
        - e.g. `python test.py -f tests/safe/ -a -r -v -t 360 -o result/result.log`
    
    - Or specify a file list using `-b -f FILELIST` (run files specified in the file list whose format is one file path in each line)
        - e.g. `python test.py -a -v -b -f tests/filtered.txt -a -t 360 -o result/result.log`

    - Increase log file verbosity using `-v` (not effective in output on screen)

    - Adjust timeout using `-t TIMEOUT`, only effective in directory mode

    - Specify the result summary log file using `-o FILE_NAME`; Export an additional result summary CSV `FILE_NAME_prefix.csv` (with success and timing statistics, and `is_correct` column shows the satisfiability of the CHC system if solved) using `-a`; The summary is only available when running multiple instances (directory mode or file list mode)

    - Start solving from the file index `K` in the folder `-s K` (`K` is the index starting from zero)

    - If you want to run multiple instances, make sure to use different `FILE_NAME`-s in the config file to avoid clash (`config.yml` in default)

    - More options see `--help`

- After finishing running, the `./tmp` directory can be deleted safely

# To reproduce the major result: Chronosymbolic-single

Please refer to the configuration in `./experiment/result_summary.log` and `./experiment/README.md` (where settings for other minor experiments are also provided). Using the default config in `config.yml` should also be decent. Even fixed random seeds can cause minor randomness that may slightly affect the performance.

- `python test.py -f tests/safe -a -r -v -t 360 -o result/result_safe.log`

- `python test.py -f tests/unsafe -a -r -v -t 360 -o result/result_unsafe.log`


# To run the baselines
## Spacer and GSpacer
- Configure [z3-gspacer-branch](https://github.com/hgvk94/z3/tree/ggbranch), `chmod +x z3`

- Specify the path of z3 (with GSpacer) binary in `utils/run_spacer.py` and `utils/run_spacer_filtered.py`

- Specify a folder name and run `utils/run_spacer.py` or specify a file list name and run `utils/run_spacer_filtered.py`

- Enable GSpacer: `enable_global_guidance = 1`

## LinearArbitrary and Freqhorn
Refer to [LinearArbitrary](https://github.com/GaloisInc/LinearArbitrary-SeaHorn/tree/master/test) and [Freqhorn](https://github.com/freqhorn/freqhorn).

A prebuilt docker image is available on [Docker Hub](https://hub.docker.com/r/sunsetray/lineararbitrary_seahorn).

For LinearArbitrary, you can also try our optimized data-driven learner implementation (set `ClassAgent = Chronosymbolic` to `ClassAgent = DataDrivenLearner` in `test.py` and run it in the same way as Chronosymbolic does)

## Manually "guess" an inductive invariant (hard to scale up)
In `test.py` `guess_manually` function:
- Modify `s = 'v_0 == v_1'` to indicate the inductive invariant

- Modify `db = load_horn_db_from_file(args.file_name, z3.main_ctx())` or pass the parameter in through command line to indicate SMTLIB2 file name

## Enumeration
- A simple implementation of an enumeration-based invariant synthesizer

- Run `learner/enumerate.py` that enumerates through a context-free grammar

# Benchmarks
[CHC-COMP](https://github.com/chc-comp)

[FreqHorn](https://github.com/freqhorn/freqhorn)

[LinearArbitrary](https://github.com/GaloisInc/LinearArbitrary-SeaHorn/tree/master/test)


# Reference
[chc-tools](https://github.com/chc-comp/chc-tools/tree/master/chctools)

[libsvm](http://www.csie.ntu.edu.tw/~cjlin/libsvm)

[ICE-C5](https://github.com/Chenguang-Zhu/ICE-C5)

[LinearArbitrary](https://github.com/GaloisInc/LinearArbitrary-SeaHorn)

[z3](https://github.com/Z3Prover/z3)

[SeaHorn](https://seahorn.github.io/)
