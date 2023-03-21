import os
import csv
from func_timeout import func_set_timeout

from CDCL import CDCL
from tools.utils import read_cnf

# some other parameters:
Paras = {'discount': 0.95, 'alpha': 0.4, 'batch': 10}

# all choices for assignment algorithm
AssignmentAlgorithm = ["VSIDS", "ERWA", "RSR", "LRB", "CHB"]

# all choices for restart policy
RestartPolicy = ["MLR", "None"]
PreProcessor = ["lighter-NiVER", "None"]
Bandit = ["UCB", "None"]


def testTime():
    # get all test files
    # assume the test files are all in ./examples
    current_path = os.getcwd()
    file_path = current_path + "\\examples"
    TestFilenames = os.listdir(file_path)

    # save the result in a csv file
    r = open('results/timeTestResult.csv', 'w', newline="")
    csv_writer = csv.writer(r)
    csv_writer.writerow(["FileName",
                         "PreProcessor",
                         "RestartPolicy",
                         "Bandit",
                         "AssignmentAlgorithm",
                         "hasSolution",
                         "Time",
                         "PreprocessTime"])

    for testfile in TestFilenames:
        if not testfile.endswith("cnf"):
            continue
        for preprocess_policy in PreProcessor:
            for restart_policy in RestartPolicy:
                for bandit in Bandit:
                    if bandit != "None" and restart_policy == "None":
                        continue
                    if bandit != "None":
                        try:
                            Res = run_cdcl(testfile, preprocess_policy, restart_policy, bandit, "VSIDS")
                        except:
                            csv_writer.writerow(["TIMEOUT", testfile, preprocess_policy, restart_policy, bandit])
                            continue
                        Res[4] = '/'
                        csv_writer.writerow(Res)
                    else:
                        for assignment_algorithm in AssignmentAlgorithm:
                            try:
                                Res = run_cdcl(testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm)
                            except:
                                csv_writer.writerow(["TIMEOUT", testfile, preprocess_policy, restart_policy, bandit])
                                continue
                            csv_writer.writerow(Res)

    r.close()


# def handle_timeout(signum, frame):
#     raise TimeoutError("function timeout")

# timeout_sec = 2
# signal.signal(signal.SIGALRM, handle_timeout)

@func_set_timeout(200)
def run_cdcl(testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm):
    print(testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm)
    hasSolution = True
    with open("examples/" + testfile, "r") as f:
        sentence, num_vars = read_cnf(f)

    # Create CDCL solver and solve it!
    cdcl = CDCL(sentence, num_vars,
                assignment_algorithm,
                Paras['alpha'],
                Paras['discount'],
                Paras['batch'],
                restart_policy,
                bandit,
                preprocess_policy)
    # signal.alarm(timeout_sec)
    # try:
    res, preprocess_time, solve_time = cdcl.solve()
    # except TimeoutError:
        # -1 means find no solution within `timeout_sec` seconds
    # Res = [testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm, False, -1, preprocess_time]
    # return Res
    # finally:
        # signal.alarm(0)

    if res is None:
        print("NO SOLUTION")
        hasSolution = False

    Res = [testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm, hasSolution, solve_time, preprocess_time]
    return Res


if __name__ == "__main__":
    testTime()
