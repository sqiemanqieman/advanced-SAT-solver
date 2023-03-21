from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Combobox
import time

from CDCL import CDCL
from tools.utils import read_cnf

startTime = time.time()


class Window(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("SAT Solver")

        f1 = Frame(master, width=1200, height=150)
        f2 = Frame(master, width=1200, height=550)
        f1.pack()
        f2.pack()
        self.fileButton = Button(f1, text="Choose CNF file", command=self.browseFile)
        self.fileButton.place(x=0, y=0)
        self.file = Label(f1, text='./examples/and1.cnf')
        self.file.place(x=100, y=0)

        self.aaLabel = Label(f1, text='Assignment Algorithm:')
        self.aaLabel.place(x=0, y=30)
        self.aa = Combobox(f1)
        self.aa['values'] = ("VSIDS", "ERWA", "RSR", "LRB", "CHB")
        self.aa.current(0)
        self.aa.place(x=130, y=30)

        self.rpLabel = Label(f1, text='Restart Policy:')
        self.rpLabel.place(x=0, y=60)
        self.rp = Combobox(f1)
        self.rp['values'] = ("None", "MLR")
        self.rp.current(0)
        self.rp.place(x=130, y=60)

        self.rbLabel = Label(f1, text='Restart Bandit:')
        self.rbLabel.place(x=0, y=90)
        self.rb = Combobox(f1)
        self.rb['values'] = ("None", "UCB")
        self.rb.current(0)
        self.rb.place(x=130, y=90)

        self.ppLabel = Label(f1, text='Preprocess Policy:')
        self.ppLabel.place(x=0, y=120)
        self.pp = Combobox(f1)
        self.pp['values'] = ("None", "niver", "lighter-niver", "li-niver-withple")
        self.pp.current(0)
        self.pp.place(x=130, y=120)

        self.tpLabel = Label(f1, text='Time for Preprocessing:')
        self.tpLabel.place(x=300, y=30)
        self.tp = Label(f1, text='0.0000s')
        self.tp.place(x=430, y=30)
        self.tsLabel = Label(f1, text='Time for Solving:')
        self.tsLabel.place(x=300, y=55)
        self.ts = Label(f1, text='0.0000s')
        self.ts.place(x=430, y=55)

        self.startButton = Button(f1, text="start", command=self.start, background='green')
        self.startButton.place(x=350, y=110)
        self.clearButton = Button(f1, text="clear", command=lambda: self.result.delete(1.0, END), background='yellow')
        self.clearButton.place(x=380, y=110)
        self.quitButton = Button(f1, text="quit", command=exit, background='red')
        self.quitButton.place(x=410, y=110)

        self.alpha = Scale(f1, from_=0, to=1, resolution=0.01, orient=HORIZONTAL, label="alpha")
        self.alpha.set(0.4)
        self.alpha.place(x=500, y=25)
        self.discount = Scale(f1, from_=0, to=1, resolution=0.01, orient=HORIZONTAL, label="discount")
        self.discount.set(0.95)
        self.discount.place(x=600, y=25)
        self.batch = Scale(f1, from_=1, to=100, resolution=1, orient=HORIZONTAL, label="batch")
        self.batch.set(10)
        self.batch.place(x=500, y=80)

        self.result = Text(f2, width=600, height=400, bg='#DCDCDC', wrap=WORD)
        scroll = Scrollbar(f2, command=self.result.yview)
        self.result.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        self.result.pack(side=LEFT, fill=BOTH, expand=1)

    def browseFile(self):
        self.file['text'] = filedialog.askopenfilename(filetypes=[("CNF files", "*.cnf")], title="Choose a CNF file",
                                                       initialdir="./examples")

    def updateTime(self):
        global startTime
        self.time['text'] = f"{(time.time() - startTime):.4f}s"
        self.time.after(100, self.updateTime)

    def start(self):
        global startTime
        with open(self.file['text'], "r") as f:
            sentence, num_vars = read_cnf(f)
        cdcl = CDCL(sentence, num_vars, self.aa.get(), self.alpha.get(), self.discount.get(),
                    self.batch.get(), self.rp.get(), self.rb.get(), self.pp.get())
        # Process(target=self.updateTime).start()
        result, preprocess_time, solve_time = cdcl.solve()
        self.result.insert(END, f"""Config:{self.file['text'].split('/')[-1], self.aa.get(), self.alpha.get(),
                                            self.discount.get(), self.batch.get(), self.rp.get(), self.rb.get(),
                                            self.pp.get()}\nResult:{result}\n\n""")
        self.tp['text'] = f"{preprocess_time:.4f}s"
        self.ts['text'] = f"{solve_time:.4f}s"


if __name__ == "__main__":
    root = Tk()
    root.geometry("1200x700")
    app = Window(root)
    root.mainloop()
