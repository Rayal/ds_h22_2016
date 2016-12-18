import Tkinter as tk
from Tkinter import *
import tkMessageBox

def screen_function(server_list, button_function):
    root = tk.Tk()

    lblName = Label(root, text="User Name")
    lblName.pack()
    lblName.place(x=60, y=50)

    entryName = Entry(root, width=39)
    entryName.pack()
    entryName.place(x=60, y=80)

    Lb1 = Listbox(root,width=39, height=10)
    ind=1
    for i in server_list:
        Lb1.insert(ind,i)
        ind=ind+1


    Lb1.pack()
    Lb1.place(x=60, y=120)

    btnJoin = Button(root, width=33, text="Join", command= lambda :button_function(entryName.get(), Lb1.get(ACTIVE)))
    btnJoin.pack()
    btnJoin.place(x=60, y=300)

    root.title('Battleship Game')
    root.minsize(width=700, height=500)
    root.mainloop()

