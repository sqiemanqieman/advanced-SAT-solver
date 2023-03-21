from CDCL import CDCL
from tools.utils import read_cnf, verify
from tools.args import parse_args


def main(args):
    # Create problem.
    with open(args.input, "r") as f:
        sentence, num_vars = read_cnf(f)
    origin_sentence = list(sentence)

    # Create CDCL solver and solve it!
    cdcl = CDCL(sentence, num_vars, args.assignment_algorithm, args.alpha, args.discount, args.batch,
                args.restart_policy, args.bandit, args.preprocess_policy)
    res, t1, t2 = cdcl.solve()

    if res is None: print("✘ No solution found")
    else:
        print(f"✔ Successfully found a solution: {res}")
        print(f"The solution is verified to be {verify(origin_sentence, res)}")
    print(f"{t1} seconds for preprocessing")
    print(f"{t2} seconds elapsed for solving")


if __name__ == "__main__":
    args = parse_args()
    main(args)
