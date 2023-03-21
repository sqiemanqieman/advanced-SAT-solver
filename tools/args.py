import argparse

# Path: tools\args.py


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discount", type=float, metavar="D", default=0.95,
                        help="discount coefficient for decaying, default 0.95")
    parser.add_argument("--alpha", type=float, metavar="A", default=0.4,
                        help="step-size coefficient for algorithms based on ERMA, default 0.4")
    parser.add_argument("-batch", type=int, metavar="A", default=10,
                        help="batch parameter used in LRB algorithm, default 10")
    parser.add_argument("-a", "--assignment-algorithm", type=str, choices=["VSIDS", "ERWA", "RSR", "LRB", "CHB"],
                        help="Case-sensitive, heuristic branching algorithm for assigning next literal, default VSIDS",
                        default=
                        "VSIDS"
                        # "ERWA"
                        # "RSR"
                        # "LRB"
                        # "CHB"
                        )
    parser.add_argument("-i", "--input", type=str, help="specify the CNF file needed to be solved, default and1.cnf",
                        default=
                        # "examples/and1.cnf"
                        # "examples/and2.cnf"
                        # "examples/bmc-2.cnf"
                        # "examples/bmc-7.cnf"
                        # "examples/test9_about34s.cnf"
                        # "my-examples/good-16-vars.cnf"
                        # "my-examples/bad-12-vars.cnf"
                        "examples/bmc-1.cnf"
                        # "my-examples/test.cnf"
                        # "my-examples/track-main-2018/2d5cc23d8d805a0cf65141e4b4401ba4-20180322_164245263_p_cnf_320_1120.cnf"
                        # "my-examples/track-main-2018/3c92dedae9bea8c2c22acd655e33d52d-e_rphp065_05.cnf"
                        # "my-examples/track-main-2018/0b8d274c5bf66683cbdd1238771b31f5-queen8-8-9.cnf"
                        )
    parser.add_argument("-r", "--restart-policy", type=str, choices=["MLR"],
                        help="specify the restart policy, default to be None, default None", default=
                        # None
                        "MLR"
                        )
    parser.add_argument("-p", "--preprocess-policy", type=str, choices=["NiVER", "lighter-NiVER", "li-NiVER-withPLE"],
                        help="specify the preprocess policy, default to be None, default None", default=
                        # None
                        # "NiVER"
                        "lighter-NiVER"
                        # "li-NiVER-withPLE"
                        )
    parser.add_argument("-b", "--bandit", type=str, choices=["UCB"],
                        help="specify the heuristic changing policy", default=
                        None
                        # "UCB"
                        )

    return parser.parse_args()
