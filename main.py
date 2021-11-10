import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import date
from datetime import datetime
import mysql.connector
import matplotlib.pyplot as plt
from hospital import *


win = tk.Tk() #MAIN WINDOW
global expiredblood
#CONNECTION WITH DATABASE
db = mysql.connector.connect(
    host='localhost',
    user='ido',
    passwd='password',
    database='blooddonation'
    )
mycursor = db.cursor()

def dashboard():
    global checkinventory_img
    global attend_img
    global record_img
    global chart_img
    global mainframe #main frame has been golabalized

    mainframe = tk.Frame(win, borderwidth = 1)
    mainframe.pack(expand=True, padx=20) #fill="both" has beeen removed

    #checkinventory button
    checkinventory_img= tk.PhotoImage(file='img/checkinventory.png')
    check_btn= tk.Button(mainframe, image=checkinventory_img, borderwidth=0, command = check_stock)
    check_btn.pack(pady=20)

    #attenddemand image
    attend_img = tk.PhotoImage(file='img/attenddemand.png')
    attend_btn= tk.Button(mainframe, image=attend_img, borderwidth=0, command=attendreq)
    attend_btn.pack(pady=25)

    #newrecord image
    record_img = tk.PhotoImage(file='img/newrecord.png')
    record_btn= tk.Button(mainframe, image=record_img, borderwidth=0, command=newrecord)
    record_btn.pack(pady=25)

    #newrecord image
    chart_img = tk.PhotoImage(file='img/visualchart.png')
    chart_btn= tk.Button(mainframe, image=chart_img, borderwidth=0, command=chartgraph)
    chart_btn.pack(pady=25)

#creating POPUP Window and respective methods
def finisher():
    global expiredblood
    for i in expiredblood:
        query = "delete from bags where bagid = (%s)"
        mycursor.execute(query,(i,))

    messagebox.showinfo("Sucess", "Bad bags are removed from stock!")
    db.commit()


def popup_permission(data):
    popwindow =  tk.Toplevel(win)
    popwindow.title('Confirmation')

    #moving popup window to center
    win_height = 150
    win_width = 300
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (win_width/2))
    y_cordinate = int((screen_height/2) - (win_height/2))
    popwindow.geometry("{}x{}+{}+{}".format(win_width, win_height, x_cordinate, y_cordinate))

    alert = ttk.Label(popwindow, text= str(data) +" numbers of bags are expired."+"\n Do you want to delete expired bags?")
    button1 = ttk.Button(popwindow, text="YES", command=lambda:[finisher(),popwindow.destroy()])
    button2 = ttk.Button(popwindow, text="NO", command=popwindow.destroy)
    alert.pack()
    button1.pack()
    button2.pack()
    popwindow.mainloop()

def check_stock():
    mainframe.destroy() #removing dashboard
    #to insert in treeview
    def stock_insert(rows):
        for i in rows:
            tv.insert('','end',values=i)

    #starts
    stock_frame = tk.LabelFrame(win)
    tv = ttk.Treeview(stock_frame, columns=(1,2,3), show="headings",height='10')

    style = ttk.Style()
    style.configure('Treeview', rowheight = 40)
    style.configure('W.TButton', font =
               ('calibri', 10),
                foreground = 'black')

    tv.pack(pady=20)
    tv.heading(1, text="Bag ID")
    tv.heading(2, text='Group')
    tv.heading(3, text='Date')

    query = "select * from bags"
    mycursor.execute(query)
    rows = mycursor.fetchall()
    stock_insert(rows)

    #back funtion again creates dashboard
    def back():
        back_button.destroy()
        stock_frame.destroy()
        dashboard()

    def restock():
        global expiredblood
        today = date.today()
        expiredblood = []
        query = "SELECT * FROM bags"
        mycursor.execute(query,)
        rows = mycursor.fetchall()
        for i in rows:
            datetime_obj = datetime.strptime(i[2], '%Y-%m-%d')
            onlydate = datetime_obj.date()
            differ = (today - onlydate).days
            if differ > 30:
                expiredblood.append(i[0])

        gate = len(expiredblood)
        if gate > 0:
            popup_permission(gate)
        else:
            messagebox.showinfo("Fresh", "All blood bags are healthy!!")

    check_button = ttk.Button(stock_frame, text=" CHECK EXPIRED ",style = 'W.TButton', command = restock)
    check_button.pack()

    back_button = ttk.Button(stock_frame, text = 'BACK', command = back)
    back_button.pack(side=tk.LEFT, padx=50)

    #stock frame positiong
    stock_frame.pack(fill="both", expand="yes", padx=20)

#FOR 2nd OPTION
def attendreq():
    mainframe.destroy()

    attend_frame=tk.LabelFrame(win)
    attend_frame.pack()

    def processor(bagid):
        query = "DELETE FROM bags WHERE bagid=(%s)"
        mycursor.execute(query,(bagid,))
        db.commit()
        messagebox.showinfo('Success', 'Blood bag has been trasferred!!')

    def popup_per(data):
        popwindow =  tk.Toplevel(win)
        popwindow.title('Confirmation')

        #moving popup window to center
        win_height = 150
        win_width = 300
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (win_width/2))
        y_cordinate = int((screen_height/2) - (win_height/2))
        popwindow.geometry("{}x{}+{}+{}".format(win_width, win_height, x_cordinate, y_cordinate))

        alert = ttk.Label(popwindow, text= str(data) +" bag id is about to be trasferred!"+"\n Are you sure?")
        button1 = ttk.Button(popwindow, text="YES", command = lambda:[processor(data),popwindow.destroy()])
        button2 = ttk.Button(popwindow, text="NO", command=popwindow.destroy)
        alert.pack()
        button1.pack()
        button2.pack()
        popwindow.mainloop()


    def response():
        if len(data.get())<1:
            messagebox.showwarning('Error','ID cannot be empty!')

        else:
            validlist = [i[0] for i in row]
            if int(data.get()) not in validlist:
                messagebox.showwarning('Error', 'Please pick one id from the list!')
            else:
                popup_per(data.get())

    #calling function from hospital module
    request = check_demand()

    if request == 'X':
        messagebox.showwarning('Error','Connection TIME OUT!!')
    else:
        fetched = ttk.Label(attend_frame, text= request + ' blood group is requested! ')
        fetched.pack(side=tk.TOP,anchor=tk.W,fill=tk.X,padx=550)

        query = 'SELECT * FROM bags WHERE bloodgroup = (%s)'
        mycursor.execute(query,(request,))
        row = mycursor.fetchall()

        if len(row) >=1:
            def stock_insert(rows):
                for i in rows:
                    tv.insert('','end',values=i)
            #starts
            tv = ttk.Treeview(attend_frame, columns=(1,2,3), show="headings",height='6')
            style = ttk.Style()
            style.configure('Treeview', rowheight = 40)
            style.configure('W.TButton', font =
                       ('calibri', 10),
                        foreground = 'black')
            tv.pack(pady=20)
            tv.heading(1, text="Bag ID")
            tv.heading(2, text='Group')
            tv.heading(3, text='Date')

            stock_insert(row)

            data=tk.StringVar()
            send = ttk.Label(attend_frame, text='BAG ID: ')
            send.pack()
            send_Entry = ttk.Entry(attend_frame, width=25, textvariable=data)
            send_Entry.pack()
            responsebtn = ttk.Button(attend_frame, text = 'SEND', command=response)
            responsebtn.pack(pady=30)

        else:
            query = 'SELECT * FROM donor WHERE bloodgroup = (%s)'
            mycursor.execute(query,(request,))
            newrow = mycursor.fetchall()

            if len(newrow) >=1:
                masterlist=[]
                childlist=[]
                for i in newrow:
                    childlist.append(i[1])
                    childlist.append(i[3])
                    childlist.append(i[4])
                    masterlist.append(childlist)
                    childlist=[]

                print(masterlist)

                def stock_insert(rows):
                    for i in rows:
                        tv.insert('','end',values=i)
                #starts
                tv = ttk.Treeview(attend_frame, columns=(1,2,3), show="headings",height='6')
                style = ttk.Style()
                style.configure('Treeview', rowheight = 40)
                style.configure('W.TButton', font =
                           ('calibri', 10),
                            foreground = 'black')
                tv.pack(pady=20)
                tv.heading(1, text="Name")
                tv.heading(2, text='Cell No')
                tv.heading(3, text='Email')

                stock_insert(masterlist)
            else:
                    messagebox.showinfo('Sorry!', 'No bags and No donors available!!')


    #BACK BUTTON
    def back():
        back_button.destroy()
        attend_frame.destroy()
        dashboard()

    back_button = ttk.Button(attend_frame, text = 'BACK', command = back)
    back_button.pack(side=tk.LEFT, padx=50)
    attend_frame.pack(fill="both", expand="yes")

#FOR 3rd OPTION
def newrecord():
    mainframe.destroy() #removing dashboard
    #starts
    newrecord_frame = tk.LabelFrame(win)
    newrecord_frame.pack()

    donorframe = tk.LabelFrame(newrecord_frame)
    #donorframe.pack(side=tk.LEFT,padx=50)
    donorframe.grid(row=0, column=0, padx=(30,0), pady=(40,0))

    bagframe = tk.LabelFrame(newrecord_frame)
    #bagframe.pack(side=tk.RIGHT)
    bagframe.grid(row=0, column=3, padx=(30,0), pady=(40,0))

    searchframe = tk.LabelFrame(newrecord_frame, text="Finding donor's ID")
    searchframe.grid(row=0, column=2, padx=(30,0), pady=(40,0))

    #adding label to donorframe
    f_name =tk.StringVar()
    first_name = ttk.Label(donorframe, text='First Name: ')
    first_name.grid(row=0, column=0, padx= (20,0),pady=(40,10))

    firstEntry = ttk.Entry(donorframe, width=25, textvariable=f_name)
    firstEntry.grid(row=0, column=1, padx= (0,20),pady=(40,10))

    l_name=tk.StringVar()
    last_name = ttk.Label(donorframe, text='Last Name: ')
    last_name.grid(row=1, column=0,padx= (20,0),pady=(10,10))

    lastEntry = ttk.Entry(donorframe, width=25, textvariable=l_name)
    lastEntry.grid(row=1, column=1, padx= (0,20))

    ph_num=tk.StringVar()
    phone = ttk.Label(donorframe, text='Phone: ')
    phone.grid(row=2, column=0,padx= (20,0),pady=(10,10))

    phoneEntry = ttk.Entry(donorframe, width=25, textvariable=ph_num)
    phoneEntry.grid(row=2, column=1, padx= (0,20))

    email=tk.StringVar()
    mail = ttk.Label(donorframe, text='Mail: ')
    mail.grid(row=3, column=0,padx= (20,0),pady=(10,10))

    mailEntry = ttk.Entry(donorframe, width=25, textvariable=email)
    mailEntry.grid(row=3, column=1, padx= (0,20))

    bloodGroup = ttk.Label(donorframe, text='Blood Group: ')
    bloodGroup.grid(row=4, column=0,padx= (20,0),pady=(10,10))

    bloodtype = tk.StringVar()
    bloodchoosen = ttk.Combobox(donorframe, width = 25, textvariable = bloodtype)

    # Adding combobox drop down list
    bloodchoosen['values'] = ('A+','A-','B+','B-','AB+','AB-','O+','O-',)
    bloodchoosen.grid(column = 1, row = 4,padx= (0,20))
    bloodchoosen.current(0)
    #---------------------------WORK HERE-------------------------------------------
    def work():
        if len(f_name.get()) < 3 or len(l_name.get()) < 2 :
            messagebox.showwarning("Error", "Name cannot be empty!")
        else:
            try:
                check = int(ph_num.get())
            except:
                messagebox.showwarning("Error", "Cell no cannot be alphabet")

            query = "SELECT * FROM donor WHERE phone = (%s) or gmail = (%s)"
            mycursor.execute(query,(ph_num.get(), email.get()))
            rows = mycursor.fetchall()
            if len(rows) == 1:
                messagebox.showwarning("Error", "Mail or cell no already registered!")
            else:
                query2 = "INSERT INTO donor(firstname, lastname, phone, gmail, bloodgroup) VALUES (%s,%s,%s,%s,%s)"
                mycursor.execute(query2,(f_name.get(),l_name.get(),ph_num.get(),email.get(),bloodtype.get()))
                db.commit()
                messagebox.showinfo("Added", "Successfully Inserted!")
                #clearing Entry Form
                firstEntry.delete(0, tk.END)
                lastEntry.delete(0,tk.END)
                phoneEntry.delete(0, tk.END)
                mailEntry.delete(0,tk.END)

    adddonor = ttk.Button(donorframe, text='Add Donor', command=work)
    adddonor.grid(row=5, column=1, pady=(10,20))

    #DONATE FRAME STARTS FROM HERE
    id = ttk.Label(bagframe, text='Donor ID: ')
    id.grid(row=0, column=0, padx= (20,0),pady=(40,10))

    did = tk.StringVar()
    idEntry = ttk.Entry(bagframe, width=25, textvariable=did)
    idEntry.grid(row=0, column=1, padx= (0,20),pady=(40,10))

    #function for execution of donation
    def donateexe():
        if len(did.get()) < 1:
            messagebox.showwarning("Error","Id cannot be empty!")
        else:
            data = int(did.get())
            query = "SELECT * FROM donor WHERE donorid = (%s)"
            mycursor.execute(query,(data,))
            rows = mycursor.fetchall()
            if len(rows) == 1:
                query2 = "SELECT lastdonation FROM donor WHERE donorid = (%s)"
                mycursor.execute(query2,(data,))
                values = list(mycursor.fetchall())
                if values[0][0] == None:
                    query3 = "SELECT bloodgroup FROM donor WHERE donorid = (%s)"
                    mycursor.execute(query3,(data,))
                    values2 = mycursor.fetchall()
                    query4 = "INSERT INTO bags(bloodgroup, lastdonation) VALUES (%s,%s)"
                    bldgrp = values2[0][0]
                    today = date.today()
                    mycursor.execute(query4,(bldgrp, today, ))
                    messagebox.showinfo("Added", "Successfully Inserted!")
                    query5 = "UPDATE donor SET lastdonation = (%s) WHERE donorid = (%s)"
                    mycursor.execute(query5,(today,data,))
                    db.commit()

                else:
                    delta = date.today() - values[0][0]
                    ddiff = delta.days
                    if ddiff < 120:
                        messagebox.showwarning("Need Gap", "Minimum 120 days gap required !")
                    else:
                        query6 = "SELECT bloodgroup FROM donor WHERE donorid = (%s)"
                        mycursor.execute(query6,(data,))
                        values3 = mycursor.fetchall()
                        query7 = "INSERT INTO bags(bloodgroup, lastdonation) VALUES (%s,%s)"
                        bldgrpa = values3[0][0]
                        today = date.today()
                        mycursor.execute(query7,(bldgrpa, today, ))
                        messagebox.showinfo("Added", "Successfully Inserted!")
                        query8 = "UPDATE donor SET lastdonation = (%s) WHERE donorid = (%s)"
                        mycursor.execute(query8,(today,data,))
                        db.commit()
                        print(bldgrpa)

            else:
                messagebox.showwarning("Error","User Not Found!")

    addblood_button = ttk.Button(bagframe, text = 'Donate', command=donateexe)
    addblood_button.grid(row=1, column=1, pady=(0,40))

    #searchframe starts
    def search():
        method = str(via.get())
        data = enteredtext.get()

        if method == 'Gmail':
            query = "SELECT donorid from donor WHERE gmail = (%s)"
            mycursor.execute(query,(data,))
            rows = mycursor.fetchall()
            if len(rows) == 1:
                messagebox.showinfo("Donor ID", "Donor Id for "+ data + " is " + str(rows[0][0]))
                searchEntry.delete(0, tk.END)
            else:
                messagebox.showinfo("Donor ID", "Sorry! User not Registered")

        else:
            if data.isdigit():
                data2 = int(enteredtext.get())

                query = "SELECT donorid from donor WHERE phone = (%s)"
                mycursor.execute(query,(data2,))
                rows = mycursor.fetchall()
                if len(rows) == 1:
                    messagebox.showinfo("Donor ID", "Donor Id for "+ data + " is " + str(rows[0][0]))
                    searchEntry.delete(0, tk.END)
                else:
                    messagebox.showinfo("Donor ID", "Sorry! User not Registered")
            else:
                messagebox.showwarning("Error", "Expected integer!")


    searchBy = ttk.Label(searchframe, text='Search By: ')
    searchBy.grid(row=0, column=0,padx= (20,0),pady=(40,10))

    via = tk.StringVar()
    searchchosen = ttk.Combobox(searchframe, width = 25, textvariable = via)

    # Adding combobox drop down list
    searchchosen['values'] = ('Phone', 'Gmail')
    searchchosen.grid(column = 1, row = 0,padx= (0,20),pady=(40,10))
    searchchosen.current(0)

    enteredtext = tk.StringVar()
    entersome = ttk.Label(searchframe, text='Enter: ')
    entersome.grid(row=1, column=0, padx= (20,0),pady=(10,10))

    searchEntry = ttk.Entry(searchframe, width=25, textvariable=enteredtext)
    searchEntry.grid(row=1, column=1, padx= (0,20),pady=(10,10))

    search_button = ttk.Button(searchframe, text = 'Search', command=search)
    search_button.grid(row=2, column=1, pady=(0,40))

    def back():
        back_button.destroy()
        newrecord_frame.destroy()
        dashboard()

    back_button = ttk.Button(newrecord_frame, text = 'BACK', command = back)
    back_button.grid(row=1, column=2, padx=(10,0), pady=25)
    newrecord_frame.pack(fill="both", expand="yes")

def chartgraph():
    query = "SELECT bloodgroup FROM bags"
    mycursor.execute(query)
    rows = mycursor.fetchall()
    allgrp=[]
    for i in rows:
        allgrp.append(i[0])

    result = dict((i, allgrp.count(i)) for i in allgrp)
    labels, sizes=zip(*result.items())
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

#calling dashboard
dashboard()

def screen_setup():
    win_height = 650
    win_width = 1350
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (win_width/2))
    y_cordinate = int((screen_height/2) - (win_height/2))
    win.geometry("{}x{}+{}+{}".format(win_width, win_height, x_cordinate, y_cordinate))

screen_setup() #calling screen setup to center GUI
win.title('Blood Bank')
win.mainloop()
