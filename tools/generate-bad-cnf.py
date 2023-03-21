def generate(num_var):
    i = 1
    res = [[]]
    while i <= num_var:
        j = 0
        while j < len(res):
            tmp = []
            tmp += res[j]
            tmp.append(-i)
            res.insert(j + 1, tmp)
            res[j].append(i)
            j += 2
        i += 1
    with open("../my-examples/bad-" + str(num_var) + "-vars.cnf", "w+") as f:
        print("p", "cnf", num_var, 2 ** num_var, file=f)
        for clause in res:
            print(str(clause)[1:-1].replace(",", ""), 0, file=f)


if __name__ == "__main__":
    for i in range(2, 20):
        generate(i)