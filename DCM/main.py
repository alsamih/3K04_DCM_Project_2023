import tkinter as tk
from tkinter import ttk #for styling
from tkinter import messagebox #popups
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tempfile import NamedTemporaryFile
import shutil
from tkinter import simpledialog
import serial
import threading
import time

FONT = ("Verdana",12)

ser = None

def open_serial_connection():
    global ser
    try:
        # Close the existing connection if it's open
        if ser is not None and ser.isOpen():
            ser.close()

        # Open a new connection
        ser = serial.Serial('COM6', 115200, timeout=0.5)
        return ser.isOpen()

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return False

def send_data_via_serial(parameters):
    global ser
    try:
        if ser is not None and ser.isOpen():
            # Convert parameters to a comma-separated string
            data_str = ','.join(map(str, parameters))
            ser.write(data_str.encode())  # Send the string as bytes
    except serial.SerialException as e:
        print(f"Error in sending data: {e}")
        messagebox.showerror("Serial Communication Error", f"Error in sending data: {e}")

def close_serial_connection():
    global ser
    try:
        if ser is not None and ser.isOpen():
            ser.close()
        ser = None  # Reset the serial connection variable
    except serial.SerialException as e:
        print(f"Error closing serial port: {e}")

def receive_data_via_serial():
    global ser
    try:
        if ser is not None and ser.isOpen():
            data = ser.read(16)  # Read from serial port
            return data.decode().strip()  # Decode and strip any whitespace
    except serial.SerialException as e:
        print(f"Error in receiving data: {e}")
        return None

class Window(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)

        #setting up container, where frames will be stacked
        container = tk.Frame(self)
        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0,weight=1) #weight is priority, 0 is like min size
        container.grid_columnconfigure(0,weight=1)

        #setting up frames
        self.frames={}

        #add all pages here
        for F in (Login,Register,Front, AOO, AAI, VOO, VVI, AOOR, VOOR, AAIR, VVIR):
            frame= F(container,self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew") #sticky to all 4 directions, so everything is stretched (stretching frame here)

        #We want to start at login page
        self.show_frame(Login)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        close_serial_connection()
        self.destroy()
    
    #helper funcs
    def show_frame(self,cont):
        '''
        this function switches the top frame

        cont is controller, controlling which frames are on top
        '''

        frame=self.frames[cont]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>") #raising event when frame should be shown
    
    def reset_entry(self,entry,txt):
        """
        resets entry widgets and resets it to whatever is in txt variable
        """
        entry.delete(0,'end')
        entry.insert(0,txt)

class Login(tk.Frame):
    """
    Login page implementation
    """
    def __init__(self,parent,controller):
        tk.Frame. __init__(self,parent)
        label=tk.Label(self,text="Login",font=FONT)
        label.pack(pady=10,padx=10)#padding

        #defining small functions for specific widget usernameLog
        def user_on_focusin(event):
            '''
            when user enters a widget, deletes preset text
            '''
            usernameLog.delete(0,'end')
        def user_on_focusout(event):
            '''user leaves widget, sets preset text'''
            if usernameLog.get()=='':
                usernameLog.insert(0,'Username')

        #user and pass inputs
        usernameLog=tk.Entry(self,bd=3)
        usernameLog.pack()
        usernameLog.insert(0,"Username")
        usernameLog.bind("<FocusIn>",user_on_focusin)
        usernameLog.bind("<FocusOut>",user_on_focusout)

        #defining small functions for specific widget passwordLog
        #for styling purposes, not really a functionality
        def pass_on_focusin(event):
            '''
            when user enters a widget, deletes preset text
            '''
            passwordLog.delete(0,'end')
            passwordLog.config(show="*") #hides user input
        def pass_on_focusout(event):
            '''user leaves widget, sets preset text'''
            if passwordLog.get()=='':
                passwordLog.insert(0,'Password')
                passwordLog.config(show="")
        
        passwordLog=tk.Entry(self,bd=3)
        passwordLog.pack()
        passwordLog.insert(0,"Password") #default text
        passwordLog.bind("<FocusIn>",pass_on_focusin) #deletes text when keyboard focused
        passwordLog.bind("<FocusOut>",pass_on_focusout) #adds text back when keyboard loses focus

        #errormsg
        errormsg=tk.Label(self,text="")
        errormsg.pack()

        def store_user(user):
            with open("currentuser.csv","w") as file:
                csv_writer=csv.writer(file)
                csv_writer.writerow(user)
        
        #readUser function which allows login 
        def readUser():
            username = usernameLog.get()
            password = passwordLog.get()

            #open text file and read to see whether or not the correct user and pass was inputed

            with open("users.csv", "r") as file:
                csv_reader=csv.reader(file)
                for row in csv_reader:
                    if (row[0]==username and row[1]==password):
                        print("Login successful!")

                        store_user(row)

                        #clearing login page
                        errormsg.config(text="")
                        controller.reset_entry(usernameLog,"Username")
                        controller.reset_entry(passwordLog,"Password")
                        passwordLog.config(show="")

                        controller.show_frame(Front)
                        # You can implement logic to switch to the next frame here
                        break
                else:
                    errormsg.config(text="Incorrect username or password! Please try again!")
                    
        
        #login button
        loginB = tk.Button(self, text = "Login", command = lambda: [readUser()])
        loginB.pack()

        #reg button
        RegisterB = tk.Button(self,text="Register an Account",command=lambda: [controller.show_frame(Register),controller.reset_entry(usernameLog,"Username"),controller.reset_entry(passwordLog,"Password"),passwordLog.config(show=""),app.focus_set(),errormsg.config(text="")])
        #^ removes previous text and keyboard focus
        RegisterB.pack()

class Register(tk.Frame):
    """
    Register page implementation
    """
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="Register",font=FONT)
        label.pack(pady=10,padx=10)#padding

        #defining small functions for specific widget usernameLog
        def on_focusin(event):
            '''
            when user enters a widget, deletes preset text
            '''
            usernameLog.delete(0,'end')
        def on_focusout(event):
            '''user leaves widget, sets preset text'''
            if usernameLog.get()=='':
                usernameLog.insert(0,'Username')

        def interacted(event):
            '''
            checks if widget has been interacted with (by raising a flag)
            '''
        
        #user and pass inputs
        usernameLog=tk.Entry(self,bd=3)
        usernameLog.pack()
        usernameLog.insert(0,"Username")
        usernameLog.bind("<FocusIn>",on_focusin)
        usernameLog.bind("<FocusOut>",on_focusout)

        #defining small functions for specific widget passwordLog
        def on_focusin(event):
            '''
            when user enters a widget, deletes preset text
            '''
            passwordLog.delete(0,'end')
            passwordLog.config(show="*") #hides user input
        def on_focusout(event):
            '''user leaves widget, sets preset text'''
            if passwordLog.get()=='':
                passwordLog.insert(0,'Password')
                passwordLog.config(show="")
        
        passwordLog=tk.Entry(self,bd=3)
        passwordLog.pack()
        passwordLog.insert(0,"Password") #default text
        passwordLog.bind("<FocusIn>",on_focusin) #deletes text when keyboard focused
        passwordLog.bind("<FocusOut>",on_focusout) #adds text back when keyboard loses focus

        #defining small functions for specific widget passwordLog
        def on_focusin(event):
            '''
            when user enters a widget, deletes preset text
            '''
            confirmLog.delete(0,'end')
            confirmLog.config(show="*") #hides user input
        def on_focusout(event):
            '''user leaves widget, sets preset text'''
            if confirmLog.get()=='':
                confirmLog.insert(0,'Confirm Password')
                confirmLog.config(show="")
        
        confirmLog=tk.Entry(self,bd=3)
        confirmLog.pack()
        confirmLog.insert(0,"Confirm Password") #default text
        confirmLog.bind("<FocusIn>",on_focusin) #deletes text when keyboard focused
        confirmLog.bind("<FocusOut>",on_focusout) #adds text back when keyboard loses focus

        #errormsg
        errormsg=tk.Label(self,text="")
        errormsg.pack()

        #buttons
        #Reg button
        RegisterB = tk.Button(self,text="Register",command=lambda: [registerCheck(), app.focus_set()]) #show_frame is placeholder rn for register func which is yet to be created
        #^ removes previous text and keyboard focus
        RegisterB.pack()
     
        #checks for existing usernames saved
        def usernameExists(username):
            with open("users.csv", 'r', newline='') as csv_file:
                csv_reader=csv.reader(csv_file)
                for row in csv_reader:
                    if (row[0] == username):
                        return True
            return False
        
        #function for checking number of users registered
        def numRegistered():
            with open("users.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                user_count = sum(1 for row in csv_reader if row)  # Count non-empty rows
            return user_count

        #function to write a user into the text file
        def writeUser():
            username = usernameLog.get()
            password = passwordLog.get()
                     
            #username,password,"LRL","URL","AA","VA","APW","VPW","AS","VS","VRP","ARP","PVARP","Hysteresis","RS"
            write_data=[username,password,0,0,0,0,0,0,0,0,0,0,0,0,0]         
            #opens text file to append user info
            with open("users.csv", 'a', newline='') as csv_file:
                csv_writer=csv.writer(csv_file)
                csv_writer.writerow(write_data)
         
        def registerCheck():
            
            username = usernameLog.get()
            password = passwordLog.get()
            confirmP = confirmLog.get()


            if ' ' in username:
                errormsg.config(text="Username cannot contain spaces.")
            elif username =='Username':
                errormsg.config(text="Please input a valid username.")
            elif password == "Password" or password =="Confirm Password" or password=='':
                errormsg.config(text="Please input a valid password")
                
            elif numRegistered() >= 10:
                errormsg.config(text="Registration is closed. Maximum users reached.")
            elif (confirmP !=password):
                errormsg.config(text="Passwords do not match.")
            elif usernameExists(username):
                errormsg.config(text="Username already exists. Please use a different Username.")
            else:
                writeUser()
                messagebox.showinfo("","Successfully registered. Please login to continue.")
                #resetting everything in case user wants to register again
                controller.reset_entry(usernameLog,"Username")
                controller.reset_entry(passwordLog,"Password")
                passwordLog.config(show="")
                controller.reset_entry(confirmLog,"Confirm password")
                confirmLog.config(show="")
                errormsg.config(text="")
                controller.show_frame(Login)

        #login button
        LoginB = tk.Button(self,text="Back to login",command=lambda: [controller.show_frame(Login),controller.reset_entry(usernameLog,"Username"),controller.reset_entry(passwordLog,"Password"),passwordLog.config(show=""),controller.reset_entry(confirmLog,"Confirm password"),confirmLog.config(show=""),errormsg.config(text=""),app.focus_set()])
        LoginB.pack()

def get_curr_user():
    with open("currentuser.csv","r") as file:
        reader=csv.reader(file)
        for row in reader:
            return row

def delete_user(username):
    tempfile = NamedTemporaryFile(mode='w', delete=False, newline='')
    with open('users.csv', 'r', newline='') as csvfile, tempfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(tempfile)
        for row in reader:
            if row[0] != username:
                writer.writerow(row)

    shutil.move(tempfile.name, 'users.csv')

class Front(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.bind("<<ShowFrame>>",self.on_show_frame)
        self.controller = controller  

        self.grid_rowconfigure(0, weight=1)  # Give weight to rows
        self.grid_columnconfigure(0, weight=1)  # Give weight to columns

        label=tk.Label(self,text="Select Pacemaker Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding
        
        global welcome
        welcome = tk.Label(self,text=("Welcome, "),font=FONT)
        welcome.pack()

        #creating drop down list
        sel=tk.StringVar()
        selectMode = ttk.Combobox(self, textvariable = sel, state="readonly")
        selectMode['values'] = ("AOO","AAI","VOO","VVI","AOOR", "VOOR", "AAIR", "VVIR")
        selectMode.pack()
        

        def updateMode(*args):

            if (sel.get()=="AOO"):
                controller.show_frame(AOO)
            elif sel.get()=="AAI":
                controller.show_frame(AAI)
            elif sel.get()=="VOO":
                controller.show_frame(VOO)
            elif sel.get()=="VVI":
                controller.show_frame(VVI)
            elif sel.get()=="AOOR":
                controller.show_frame(AOOR)
            elif sel.get()=="VOOR":
                controller.show_frame(VOOR)
            elif sel.get()=="AAIR":
                controller.show_frame(AAIR)
            elif sel.get()=="VVIR":
                controller.show_frame(VVIR)


        sel.trace('w',updateMode)

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack(pady = 5)

        def test_con():
            # Close existing connection if open
            close_serial_connection()

            # Attempt to open a new connection
            if not open_serial_connection():
                messagebox.showerror("Serial Connection", "Failed to open serial port.")
            else:
                messagebox.showinfo("Device Connected", "Connection successful.")
                
        connectionButton = tk.Button(self,text="Check for connection",command = lambda: [test_con()])
        connectionButton.pack(pady=5)

        def sameDevice():
            if not open_serial_connection():
                messagebox.showerror("Serial Connection", "There is no device connected")
            else:
                messagebox.showinfo("" ,"Device is the same")

        sameDeviceButton = tk.Button(self,text="Check if different device is connected",command = sameDevice)
        sameDeviceButton.pack(pady=5)
        

        homeButton = tk.Button(self,text="Log out",command=lambda: [controller.show_frame(Login),app.focus_set(),close_serial_connection()])
        homeButton.pack(pady=50)
        
         # Button to delete a user
        delete_user_button = tk.Button(self, text="Delete User", command=self.delete_user_prompt)
        delete_user_button.pack(pady=5) 

    def delete_user_prompt(self):
            # Prompt for username to delete
        current_user = get_curr_user()
        if current_user:
            username = current_user[0]  # Assuming the username is the first element
            delete_user(username)
            messagebox.showinfo("Info", f"User {username} deleted.")
            
            self.controller.show_frame(Login)

    def on_show_frame(self,event):
        welcome.config(text=("Welcome, " + get_curr_user()[0]))

class AOO(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="AOO Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding
        self.ecg_time = 0  # Initialize time counter for ECG
        self.ecg_signal = np.array([])  # Initialize ECG signal array

        self.paused = False  # New attribute to control pause state
        self.running = False 

        self.stored_lower_lim = 0
        self.stored_upper_lim = 0
        self.stored_atrial_amp = 0
        self.stored_atrial_pulse_width = 0

        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"

            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 4:
                                lowerLim, upperLim, atrialAmpl, atrialPulse = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return
                        
                        
                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)
                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)
                        atrialAmp_var = tk.StringVar()
                        atrialAmp_var.set(atrialAmpl)
                        atrialPulse_var = tk.StringVar()
                        atrialPulse_var.set(atrialPulse)

                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 100, y = 100)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 160, y = 100)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 100, y = 120)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 160, y = 120)

                        atrialAmplab = tk.Label(self, text = "upper lim: ")
                        atrialAmplab = tk.Label(self, text = "atrial amp: ")
                        atrialAmplab.place(x = 100, y = 140)
                        atrialAmplab1 = tk.Label(self, textvariable=atrialAmp_var)
                        atrialAmplab1.place(x = 180, y = 140)

                        atrialPulselab = tk.Label(self, text = "upper lim: ")
                        atrialPulselab = tk.Label(self, text = "atrial pulse: ")
                        atrialPulselab.place(x = 100, y = 160)
                        atrialPulselab1 = tk.Label(self, textvariable=atrialPulse_var)
                        atrialPulselab1.place(x = 180, y = 160)

        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
            
        def save_text():
            """
            checking if inputs are correct, if true, update crv files
            """
            if (inputs_correct()):
                #inputting txt into the DB
                #in other words, we are importing the csv into the DB right now
                self.stored_lower_lim = float(self.lowerLimit.get())
                self.stored_upper_lim = float(self.upperLimit.get())
                self.stored_atrial_amp = float(self.atrialAmp.get())
                self.stored_atrial_pulse_width = float(self.atrialPulseWidth.get())

                data = [self.stored_lower_lim, self.stored_upper_lim, self.stored_atrial_amp, self.stored_atrial_pulse_width]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename, 'r', newline='') as csvFile, tempfile:
                    reader = csv.reader(csvFile, delimiter=',')
                    writer = csv.writer(tempfile, delimiter=',')

                    for row in reader:
                        if row[0] == currUser:  # If it's the current user
                            row[2:] = data  # Replace the existing data with new data
                        writer.writerow(row)

                shutil.move(tempfile.name, filename)

                #updating currentuser
                curr_data=[get_curr_user()[0],get_curr_user()[1],self.stored_lower_lim,self.stored_upper_lim,self.stored_atrial_amp,self.stored_atrial_pulse_width]
                with open('currentuser.csv','w', newline='') as file:
                    writer=csv.writer(file,delimiter=',')
                    writer.writerow(curr_data)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")

        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False
            
            #atrialamp (regulated)
            atrialamp=float(self.atrialAmp.get())
            #or atrialamp!=0.0
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(atrialamp not in allowed_in):
                return False

            #atrialpulsewidth
            awp=float(self.atrialPulseWidth.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(awp not in allowed_in):
                return False
            return True

        # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()

        #lower
        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))
        
        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()

        #upper
        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        # atrial amplif
        atrial_amplification = tk.Label(self, text="Atrial Amplification", font=FONT)
        atrial_amplification.pack()

        #atrial amp
        self.atrialAmp = tk.Entry(self)
        self.atrialAmp.pack(pady=10)
        self.atrialAmp.config(validate="key", validatecommand=(self.atrialAmp.register(is_digit_check), "%P"))

         # atrial pulse
        atrial_pulse = tk.Label(self, text="Atrial Pulse Width", font=FONT)
        atrial_pulse.pack()

        #atrial pulse width
        self.atrialPulseWidth = tk.Entry(self)
        self.atrialPulseWidth.pack(pady=10)
        self.atrialPulseWidth.config(validate="key", validatecommand=(self.atrialPulseWidth.register(is_digit_check), "%P"))

        button_frame = tk.Frame(self)
        button_frame.pack()

        save_button = tk.Button(button_frame, text="Submit Data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()

        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack()

        # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

class AAI(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="AAI Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding

        self.ecg_time = 0  # Initialize time counter for ECG
        self.ecg_signal = np.array([])  # Initialize ECG signal array

        self.paused = False  # New attribute to control pause state
        self.running = False 

        self.stored_lower_lim = 0
        self.stored_upper_lim = 0
        self.stored_atrial_amp = 0
        self.stored_atrial_pulse_width = 0
            
        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"

            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 9:
                                lowerLim, upperLim, atrialAmpl, atrialPulse, atrialSens, arp1, pvarp1, hyst, ratesmooth = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return
                        
                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)
                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)
                        atrialAmp_var = tk.StringVar()
                        atrialAmp_var.set(atrialAmpl)
                        atrialPulse_var = tk.StringVar()
                        atrialPulse_var.set(atrialPulse)

                        atrialSens_var = tk.StringVar()
                        atrialSens_var.set(atrialSens)
                        arp1_var = tk.StringVar()
                        arp1_var.set(arp1)
                        pvarp1_var = tk.StringVar()
                        pvarp1_var.set(pvarp1)

                        hyst_var = tk.StringVar()
                        hyst_var.set(hyst)
                        ratesmooth_var = tk.StringVar()
                        ratesmooth_var.set(ratesmooth)


                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 100, y = 100)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 160, y = 100)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 100, y = 120)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 160, y = 120)

                        atrialAmplab = tk.Label(self, text = "atrial amp: ")
                        atrialAmplab.place(x = 100, y = 140)
                        atrialAmplab1 = tk.Label(self, textvariable=atrialAmp_var)
                        atrialAmplab1.place(x = 180, y = 140)

                        atrialPulselab = tk.Label(self, text = "atrial pulse: ")
                        atrialPulselab.place(x = 100, y = 160)
                        atrialPulselab1 = tk.Label(self, textvariable=atrialPulse_var)
                        atrialPulselab1.place(x = 180, y = 160)

                        atrialSenslab = tk.Label(self, text = "atrial sens: ")
                        atrialSenslab.place(x = 100, y = 180)
                        atrialSenslab1 = tk.Label(self, textvariable=atrialSens_var)
                        atrialSenslab1.place(x = 180, y = 180)

                        arplab = tk.Label(self, text = "arp: ")
                        arplab.place(x = 100, y = 200)
                        arplab1 = tk.Label(self, textvariable=arp1_var)
                        arplab1.place(x = 140, y = 200)

                        pvarplab = tk.Label(self, text = "pvarp: ")
                        pvarplab.place(x = 100, y = 220)
                        pvarplab1 = tk.Label(self, textvariable=pvarp1_var)
                        pvarplab1.place(x = 160, y = 220)

                        hystlab = tk.Label(self, text = "hysteresis: ")
                        hystlab.place(x = 100, y = 240)
                        hystlab1 = tk.Label(self, textvariable=hyst_var)
                        hystlab1.place(x = 180, y = 240)

                        ratesmoothlab = tk.Label(self, text = "rate smooth: ")
                        ratesmoothlab.place(x = 100, y = 260)
                        ratesmoothlab1 = tk.Label(self, textvariable=ratesmooth_var)
                        ratesmoothlab1.place(x = 180, y = 260)

        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
        
        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False

            #atrialamp (regulated)
            atrialamp=float(self.atrialAmp.get())
            #or atrialamp!=0.0
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(atrialamp not in allowed_in):
                return False

            #atrialpulsewidth
            awp=float(self.atrialPulseWidth.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(awp not in allowed_in):
                return False
            
            #atrialsensitiby
            atrials=float(self.atrialsensitivity.get())
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if (atrials not in allowed_in):
                return False
            
            #ARP (same as VRP FOR NOW and PVARP)
            try:
                arp=int(self.arp.get())
            except:
                return False
            if (arp <150 or arp>500):
                return False
            if (arp%10!=0):
                return False
            #ARP (same as VRP FOR NOW and PVARP)
            try:
                pvarp=int(self.pvarp.get())
            except:
                return False
            if (pvarp <150 or pvarp>500):
                return False
            if (pvarp%10!=0):
                return False

            return True

        def save_text():
            if (inputs_correct()):
                lowerLim = self.lowerLimit.get()
                upperLim = self.upperLimit.get()
                atrialAmpl = self.atrialAmp.get()
                atrialPulse = self.atrialPulseWidth.get()
                atrialSens = self.atrialsensitivity.get()
                arp1 = self.arp.get()
                pvarp1 = self.pvarp.get()
                hyst = self.Hysteresis.get()
                ratesmooth = self.rate_smooth.get()

                data = [lowerLim, upperLim, atrialAmpl, atrialPulse, atrialSens, arp1, pvarp1, hyst, ratesmooth]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename,'r',newline='') as csvFile, tempfile:
                    reader=csv.reader(csvFile,delimiter=',')
                    writer=csv.writer(tempfile,delimiter=',')

                    for row in reader:
                        if (row[0]==currUser): #current user is this line
                            row[2:]=data
                        writer.writerow(row)
                shutil.move(tempfile.name,filename)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")

            #updating currentuser
            curr_data=[get_curr_user()[0],get_curr_user()[1],lowerLim,upperLim,atrialAmpl,atrialPulse]
            with open('currentuser.csv','w', newline='') as file:
                writer=csv.writer(file,delimiter=',')
                writer.writerow(curr_data)
        
        # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()
        
        #lower
        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))

        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()

        #upper
        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        # atrial amplif
        atrial_amp = tk.Label(self, text="Atrial Amplification", font=FONT)
        atrial_amp.pack()

        #atrial amp
        self.atrialAmp = tk.Entry(self)
        self.atrialAmp.pack(pady=10)
        self.atrialAmp.config(validate="key", validatecommand=(self.atrialAmp.register(is_digit_check), "%P"))

        # atrial amplif
        atrial_pulse = tk.Label(self, text="Atrial Pulse Width", font=FONT)
        atrial_pulse.pack()

        #atrial pulse
        self.atrialPulseWidth = tk.Entry(self)
        self.atrialPulseWidth.pack(pady=10)
        self.atrialPulseWidth.config(validate="key", validatecommand=(self.atrialPulseWidth.register(is_digit_check), "%P"))
        
        # atrial amplif
        atrial_sens = tk.Label(self, text="Atrial Sensitivity", font=FONT)
        atrial_sens.pack()
        
        #atrial sens
        self.atrialsensitivity = tk.Entry(self)
        self.atrialsensitivity.pack(pady=10)
        self.atrialsensitivity.config(validate="key", validatecommand=(self.atrialsensitivity.register(is_digit_check), "%P"))

        # atrial amplif
        arp2 = tk.Label(self, text="ARP", font=FONT)
        arp2.pack()

        #arp
        self.arp = tk.Entry(self)
        self.arp.pack(pady=10)
        self.arp.config(validate="key", validatecommand=(self.arp.register(is_digit_check), "%P"))

        # atrial amplif
        pvarp2 = tk.Label(self, text="PVARP", font=FONT)
        pvarp2.pack()

        #pvarp
        self.pvarp = tk.Entry(self)
        self.pvarp.pack(pady=10)
        self.pvarp.config(validate="key", validatecommand=(self.pvarp.register(is_digit_check), "%P"))

        # Hysteresis
        Hysteresis_label = tk.Label(self, text="Hysteresis", font=FONT)
        Hysteresis_label.pack()

        self.Hysteresis = tk.Entry(self)
        self.Hysteresis.pack(pady=10)
        self.Hysteresis.config(validate="key", validatecommand=(self.Hysteresis.register(is_digit_check), "%P"))

        # Rate Smoothing
        rate_smooth_label = tk.Label(self, text="Rate Smoothing", font=FONT)
        rate_smooth_label.pack()

        self.rate_smooth = tk.Entry(self)
        self.rate_smooth.pack(pady=10)
        self.rate_smooth.config(validate="key", validatecommand=(self.rate_smooth.register(is_digit_check), "%P"))

        button_frame = tk.Frame(self)
        button_frame.pack()

        save_button = tk.Button(button_frame, text="submit data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()

        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack(pady=15)

     # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

class VOO(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="VOO Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding

        #LRL, URL, VA, VPW,
            
        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"

            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 6:
                                lowerLim, upperLim, placeholder1, placeholder2, ventricularAmpl, ventricularPulse = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return


                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)
                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)

                        placeholder1_var = tk.StringVar()
                        placeholder1_var.set(placeholder1)

                        placeholder2_var = tk.StringVar()
                        placeholder2_var.set(placeholder2)
                        
                        ventricularAmp_var = tk.StringVar()
                        ventricularAmp_var.set(ventricularAmpl)
                        venttricularPulse_var = tk.StringVar()
                        venttricularPulse_var.set(ventricularPulse)

                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 100, y = 100)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 160, y = 100)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 100, y = 120)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 160, y = 120)

                        ventricularamplab = tk.Label(self, text = "ventricular amp: ")
                        ventricularamplab.place(x = 100, y = 140)
                        ventricularamplab1 = tk.Label(self, textvariable=ventricularAmp_var)
                        ventricularamplab1.place(x = 220, y = 140)

                        ventricularPulselab = tk.Label(self, text = "ventricular pulse: ")
                        ventricularPulselab.place(x = 100, y = 160)
                        ventricularPulselab1 = tk.Label(self, textvariable=venttricularPulse_var)
                        ventricularPulselab1.place(x = 220, y = 160)

        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
        
        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False

            #ventricalamp (regulated)
            vamp=float(self.ventricularAmp.get())
            #or atrialamp!=0.0
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(vamp not in allowed_in):
                return False
                    
            #ventricalpulsewidth
            vwp=float(self.ventricularPulseWidth.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(vwp not in allowed_in):
                return False

            return True

        def save_text():
            if (inputs_correct()):
                lowerLim = self.lowerLimit.get()
                upperLim = self.upperLimit.get()
                ventricularAmpl = self.ventricularAmp.get()
                ventricularPulse = self.ventricularPulseWidth.get()
                
                data=[lowerLim,upperLim,"na", "na",ventricularAmpl,ventricularPulse]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename,'r',newline='') as csvFile, tempfile:
                    reader=csv.reader(csvFile,delimiter=',')
                    writer=csv.writer(tempfile,delimiter=',')

                    for row in reader:
                        if (row[0]==currUser): #current user is this line
                            row[2:]=data
                        writer.writerow(row)
                shutil.move(tempfile.name,filename)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")

        # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()

        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))

        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()

        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        # Ventricular Amplitude
        ventricular_amp = tk.Label(self, text="Ventricular Amplitude", font=FONT)
        ventricular_amp.pack()

        self.ventricularAmp = tk.Entry(self)
        self.ventricularAmp.pack(pady=10)
        self.ventricularAmp.config(validate="key", validatecommand=(self.ventricularAmp.register(is_digit_check), "%P"))

        # Ventricular Pulse Width
        ventricular_pulse_width = tk.Label(self, text="Ventricular Pulse Width", font=FONT)
        ventricular_pulse_width.pack()

        self.ventricularPulseWidth = tk.Entry(self)
        self.ventricularPulseWidth.pack(pady=10)
        self.ventricularPulseWidth.config(validate="key", validatecommand=(self.ventricularPulseWidth.register(is_digit_check), "%P"))


        button_frame = tk.Frame(self)
        button_frame.pack()

        save_button = tk.Button(button_frame, text="submit data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()
    
        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack(pady=15)

     # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

class VVI(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="VVI Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding
            
        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"

            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 8:
                                lowerLim, upperLim, ventricularAmpl, ventricularPulse, ventricularSens, vrp1, hyst, ratesmooth = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return
                        
                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)
                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)
                        ventricularAmp_var = tk.StringVar()
                        ventricularAmp_var.set(ventricularAmpl)
                        venttricularPulse_var = tk.StringVar()
                        venttricularPulse_var.set(ventricularPulse)

                        ventricularSens_var = tk.StringVar()
                        ventricularSens_var.set(ventricularSens)
                        vrp1_var = tk.StringVar()
                        vrp1_var.set(vrp1)
                        
                        hyst_var = tk.StringVar()
                        hyst_var.set(hyst)
                        ratesmooth_var = tk.StringVar()
                        ratesmooth_var.set(ratesmooth)


                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 100, y = 100)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 160, y = 100)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 100, y = 120)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 160, y = 120)

                        ventricularamplab = tk.Label(self, text = "ventricular amp: ")
                        ventricularamplab.place(x = 100, y = 140)
                        ventricularamplab1 = tk.Label(self, textvariable=ventricularAmp_var)
                        ventricularamplab1.place(x = 200, y = 140)

                        ventricularPulselab = tk.Label(self, text = "ventricular pulse: ")
                        ventricularPulselab.place(x = 100, y = 160)
                        ventricularPulselab1 = tk.Label(self, textvariable=venttricularPulse_var)
                        ventricularPulselab1.place(x = 200, y = 160)

                        ventricularSenslab = tk.Label(self, text = "ventricular sens: ")
                        ventricularSenslab.place(x = 100, y = 180)
                        ventricularSenslab1 = tk.Label(self, textvariable=ventricularSens_var)
                        ventricularSenslab1.place(x = 200, y = 180)

                        vrplab = tk.Label(self, text = "vrp: ")
                        vrplab.place(x = 100, y = 200)
                        vrplab1 = tk.Label(self, textvariable=vrp1_var)
                        vrplab1.place(x = 160, y = 200)

                        hystlab = tk.Label(self, text = "hysteresis: ")
                        hystlab.place(x = 100, y = 220)
                        hystlab1 = tk.Label(self, textvariable=hyst_var)
                        hystlab1.place(x = 160, y = 220)

                        ratesmoothlab = tk.Label(self, text = "rate smooth: ")
                        ratesmoothlab.place(x = 100, y = 240)
                        ratesmoothlab1 = tk.Label(self, textvariable=ratesmooth_var)
                        ratesmoothlab1.place(x = 220, y = 240)

        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
        
        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False

             #ventricalamp (regulated)
            vamp=float(self.ventricularAmp.get())
            #or atrialamp!=0.0
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(vamp not in allowed_in):
                return False
                    
            #ventricalpulsewidth
            vwp=float(self.ventricularPulseWidth.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(vwp not in allowed_in):
                return False
            
            #atrialsensitiby
            ventricals=float(self.ventricularsensitivity.get())
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if (ventricals not in allowed_in):
                return False
            
            #ARP (same as VRP FOR NOW and PVARP)
            try:
                vrp=int(self.vrp.get())
            except:
                return False
            if (vrp <150 or vrp>500):
                return False
            if (vrp%10!=0):
                return False
           
            return True

        def save_text():
            if (inputs_correct()):
                lowerLim = self.lowerLimit.get()
                upperLim = self.upperLimit.get()
                ventricularAmpl = self.ventricularAmp.get()
                ventricularPulse = self.ventricularPulseWidth.get()
                ventricularSens = self.ventricularsensitivity.get()
                vrp1 = self.vrp.get()
                hyst = self.Hysteresis.get()
                ratesmooth = self.rate_smooth.get()

                data = [lowerLim, upperLim, ventricularAmpl, ventricularPulse, ventricularSens, vrp1, hyst, ratesmooth]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename,'r',newline='') as csvFile, tempfile:
                    reader=csv.reader(csvFile,delimiter=',')
                    writer=csv.writer(tempfile,delimiter=',')

                    for row in reader:
                        if (row[0]==currUser): #current user is this line
                            row[2:]=data
                        writer.writerow(row)
                shutil.move(tempfile.name,filename)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")
            


        # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()

        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))

        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()

        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        # Ventricular Amplitude
        ventricular_amp = tk.Label(self, text="Ventricular Amplitude", font=FONT)
        ventricular_amp.pack()

        self.ventricularAmp = tk.Entry(self)
        self.ventricularAmp.pack(pady=10)
        self.ventricularAmp.config(validate="key", validatecommand=(self.ventricularAmp.register(is_digit_check), "%P"))

        # Ventricular Pulse Width
        ventricular_pulse_width = tk.Label(self, text="Ventricular Pulse Width", font=FONT)
        ventricular_pulse_width.pack()

        self.ventricularPulseWidth = tk.Entry(self)
        self.ventricularPulseWidth.pack(pady=10)
        self.ventricularPulseWidth.config(validate="key", validatecommand=(self.ventricularPulseWidth.register(is_digit_check), "%P"))

        # Ventricular Sensitivity
        ventricular_sensitivity = tk.Label(self, text="Ventricular Sensitivity", font=FONT)
        ventricular_sensitivity.pack()

        self.ventricularsensitivity = tk.Entry(self)
        self.ventricularsensitivity.pack(pady=10)
        self.ventricularsensitivity.config(validate="key", validatecommand=(self.ventricularsensitivity.register(is_digit_check), "%P"))

        # VRP
        VRP_label = tk.Label(self, text="VRP", font=FONT)
        VRP_label.pack()

        self.vrp = tk.Entry(self)
        self.vrp.pack(pady=10)
        self.vrp.config(validate="key", validatecommand=(self.vrp.register(is_digit_check), "%P"))

        # Hysteresis
        Hysteresis_label = tk.Label(self, text="Hysteresis", font=FONT)
        Hysteresis_label.pack()

        self.Hysteresis = tk.Entry(self)
        self.Hysteresis.pack(pady=10)
        self.Hysteresis.config(validate="key", validatecommand=(self.Hysteresis.register(is_digit_check), "%P"))

        # Rate Smoothing
        rate_smooth_label = tk.Label(self, text="Rate Smoothing", font=FONT)
        rate_smooth_label.pack()

        self.rate_smooth = tk.Entry(self)
        self.rate_smooth.pack(pady=10)
        self.rate_smooth.config(validate="key", validatecommand=(self.rate_smooth.register(is_digit_check), "%P"))

        button_frame = tk.Frame(self)
        button_frame.pack()

        save_button = tk.Button(button_frame, text="submit data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()
    
        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack(pady=15)

     # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

class AOOR(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="AOOR Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding

        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"


            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 9:
                                lowerLim, upperLim, maxSens, atrialAmpl, atrialPulse, activityThresh, reactionTime, responseFac, recoveryTime = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return
                        
                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)

                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)

                        maxSens_var = tk.StringVar()
                        maxSens_var.set(maxSens)

                        atrialAmpl_var = tk.StringVar()
                        atrialAmpl_var.set(atrialAmpl)

                        atrialPulse_var = tk.StringVar()
                        atrialPulse_var.set(atrialPulse)

                        activityThresh_var = tk.StringVar()
                        activityThresh_var.set(activityThresh)

                        reactionTime_var = tk.StringVar()
                        reactionTime_var.set(reactionTime)

                        responseFac_var = tk.StringVar()
                        responseFac_var.set(responseFac)

                        recoveryTime_var = tk.StringVar()
                        recoveryTime_var.set(recoveryTime)

                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 100, y = 100)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 160, y = 100)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 100, y = 120)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 160, y = 120)

                        maxSenslab = tk.Label(self, text = "maximum sensor rate: ")
                        maxSenslab.place(x = 100, y = 140)
                        maxSenslab1 = tk.Label(self, textvariable=maxSens_var)
                        maxSenslab1.place(x = 230, y = 140)

                        atrialAmpllab = tk.Label(self, text = "atrial amplitude: ")
                        atrialAmpllab.place(x = 100, y = 160)
                        atrialAmpllab1 = tk.Label(self, textvariable=atrialAmpl_var)
                        atrialAmpllab1.place(x = 200, y = 160)

                        atrialPulselab = tk.Label(self, text = "atrial pulse: ")
                        atrialPulselab.place(x = 100, y = 180)
                        atrialPulselab1 = tk.Label(self, textvariable=atrialPulse_var)
                        atrialPulselab1.place(x = 160, y = 180)

                        activityThreshlab = tk.Label(self, text = "activity threshold: ")
                        activityThreshlab.place(x = 100, y = 200)
                        activityThreshlab1 = tk.Label(self, textvariable=activityThresh_var)
                        activityThreshlab1.place(x = 210, y = 200)

                        reactionTimelab = tk.Label(self, text = "reaction time: ")
                        reactionTimelab.place(x = 100, y = 220)
                        reactionTimelab1 = tk.Label(self, textvariable=reactionTime_var)
                        reactionTimelab1.place(x = 180, y = 220)

                        responseFaclab = tk.Label(self, text = "response factor: ")
                        responseFaclab.place(x = 100, y = 240)
                        responseFaclab1 = tk.Label(self, textvariable=responseFac_var)
                        responseFaclab1.place(x = 190, y = 240)

                        recoveryTimelab = tk.Label(self, text = "recovery time: ")
                        recoveryTimelab.place(x = 100, y = 260)
                        recoveryTimelab1 = tk.Label(self, textvariable=recoveryTime_var)
                        recoveryTimelab1.place(x = 180, y = 260)

        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
            
        def save_text():
            """
            checking if inputs are correct, if true, update crv files
            """
            if (inputs_correct()):
                #inputting txt into the DB
                #in other words, we are importing the csv into the DB right now
                lowerLim = self.lowerLimit.get()
                upperLim = self.upperLimit.get()
                maxSens = self.maxSens.get()
                atrialAmpl = self.atrialAmp.get()
                atrialPulse = self.atrialPulseWidth.get()
                activityThresh = self.activityThresh.get()
                reactionTime = self.reactionTime.get()
                responseFac = self.responseFac.get()
                recoveryTime = self.recoveryTime.get()
                
                data=[lowerLim,upperLim,maxSens,atrialAmpl,atrialPulse, activityThresh, reactionTime, responseFac, recoveryTime]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename,'r',newline='') as csvFile, tempfile:
                    reader=csv.reader(csvFile,delimiter=',')
                    writer=csv.writer(tempfile,delimiter=',')

                    for row in reader:
                        if (row[0]==currUser): #current user is this line
                            row[2:]=data
                        writer.writerow(row)
                shutil.move(tempfile.name,filename)

                #updating currentuser
                curr_data=[get_curr_user()[0],get_curr_user()[1],lowerLim,upperLim,maxSens,atrialAmpl,atrialPulse, activityThresh, reactionTime, responseFac, recoveryTime]
                with open('currentuser.csv','w', newline='') as file:
                    writer=csv.writer(file,delimiter=',')
                    writer.writerow(curr_data)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")

            
        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False
            
            #maximum sensor rate
            try:
                maxSens=int(self.maxSens.get())
            except:
                return False
            if(50> maxSens or maxSens > 175):
                return False
            if(maxSens %5!=0):
                return False

            #atrialamp (regulated)
            atrialamp=float(self.atrialAmp.get())
            #or atrialamp!=0.0
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(atrialamp not in allowed_in):
                return False
                    
            #atrialpulsewidth
            awp=float(self.atrialPulseWidth.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(awp not in allowed_in):
                return False
            
            #activity threshold will have dropdown menu so no need for limits
            
            #reaction time
            try:
                reactionTime=int(self.reactionTime.get())
            except:
                return False
            if(10 > reactionTime or reactionTime > 50):
                return False
            if(reactionTime %10!= 0):
                return False
            
            #response factor
            try:
                responseFac=int(self.responseFac.get())
            except:
                return False
            if(1 > responseFac or responseFac > 16):
                return False
            if(reactionTime %1!= 0):
                return False
            

            #recovery time
            try:
                recoveryTime=int(self.recoveryTime.get())
            except:
                return False
            if(2> recoveryTime or recoveryTime > 16):
                return False
            if(recoveryTime %1!=0):
                return False
            
            return True

     # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()
         #lower
        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))


        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()
        #upper
        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        #maximum sensor rate
        max_sensor_rate = tk.Label(self, text="Maximum Sensor Rate", font=FONT)
        max_sensor_rate.pack()
         #max sens rate
        self.maxSens = tk.Entry(self)
        self.maxSens.pack(pady=10)
        self.maxSens.config(validate="key", validatecommand=(self.maxSens.register(is_digit_check), "%P"))

        #atrial amplitude
        atrial_amplitude = tk.Label(self, text="Atrial Amplitude", font=FONT)
        atrial_amplitude.pack()
        #atrial amp
        self.atrialAmp = tk.Entry(self)
        self.atrialAmp.pack(pady=10)
        self.atrialAmp.config(validate="key", validatecommand=(self.atrialAmp.register(is_digit_check), "%P"))


        # atrial pulse
        atrial_pulse = tk.Label(self, text="Atrial Pulse Width", font=FONT)
        atrial_pulse.pack()
        #atrial pulse width
        self.atrialPulseWidth = tk.Entry(self)
        self.atrialPulseWidth.pack(pady=10)
        self.atrialPulseWidth.config(validate="key", validatecommand=(self.atrialPulseWidth.register(is_digit_check), "%P"))


        
        activity_thresh= tk.Label(self, text="Activity Threshold", font=FONT)
        activity_thresh.pack()
        val = tk.StringVar()
        selectmode = ttk.Combobox(self, textvariable = val, state = "readonly")
        selectmode['values'] = ("V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High")
        selectmode.pack()
        def chosen_activity_thresh(self, *args):
            if val.get() == "V-Low":
                self.activityThresh.set(-3)
            elif val.get() == "Low":
                self.activityThresh.set(-2)
            elif val.get() == "Med-Low":
                self.activityThresh.set(-1)
            elif val.get() == "Med":
                self.activityThresh.set(0)
            elif val.get() == "Med-High":
                self.activityThresh.set(1)
            elif val.get() == "High":
                self.activityThresh.set(2)
            elif val.get() == "V-High":
                self.activityThresh.set(3)

        # Set up a trace on the StringVar to call the update function when the selection changes
        self.activityThresh = tk.StringVar()
        val.trace('w', lambda *args: chosen_activity_thresh(self, *args))



        #Reaction Time
        reaction_time = tk.Label(self, text="Reaction Time", font=FONT)
        reaction_time.pack()
        #atrial pulse width
        self.reactionTime = tk.Entry(self)
        self.reactionTime.pack(pady=10)
        self.reactionTime.config(validate="key", validatecommand=(self.reactionTime.register(is_digit_check), "%P"))


        #Response Factor
        response_factor = tk.Label(self, text="Response Factor", font=FONT)
        response_factor.pack()
        #response factor
        self.responseFac = tk.Entry(self)
        self.responseFac.pack(pady=10)
        self.responseFac.config(validate="key", validatecommand=(self.responseFac.register(is_digit_check), "%P"))


        #Recovery Time
        response_factor = tk.Label(self, text="Recovery Time", font=FONT)
        response_factor.pack()
        #recovery time
        self.recoveryTime = tk.Entry(self)
        self.recoveryTime.pack(pady=10)
        self.recoveryTime.config(validate="key", validatecommand=(self.recoveryTime.register(is_digit_check), "%P"))


        button_frame = tk.Frame(self)
        button_frame.pack()

        save_button = tk.Button(button_frame, text="Submit Data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()
    

        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

     # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

class VOOR(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="VOOR Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding

        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"

            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 9:
                                lowerLim, upperLim, maxSens, ventAmpl, ventPulse, activityThresh, reactionTime, responseFac, recoveryTime = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return
                        

                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)
                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)
                        maxSens_var = tk.StringVar()
                        maxSens_var.set(maxSens)
                        ventAmpl_var = tk.StringVar()
                        ventAmpl_var.set(ventAmpl)
                        ventPulse_var = tk.StringVar()
                        ventPulse_var.set(ventPulse)
                        activityThresh_var = tk.StringVar()
                        activityThresh_var.set(activityThresh)
                        reactionTime_var = tk.StringVar()
                        reactionTime_var.set(reactionTime)
                        responseFac_var = tk.StringVar()
                        responseFac_var.set(responseFac)
                        recoveryTime_var = tk.StringVar()
                        recoveryTime_var.set(recoveryTime)

                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 100, y = 100)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 160, y = 100)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 100, y = 120)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 160, y = 120)

                        maxSenslab = tk.Label(self, text = "maximum sensor rate: ")
                        maxSenslab.place(x = 100, y = 140)
                        maxSenslab1 = tk.Label(self, textvariable=maxSens_var)
                        maxSenslab1.place(x = 230, y = 140)

                        atrialAmpllab = tk.Label(self, text = "Ventricular amplitude: ")
                        atrialAmpllab.place(x = 100, y = 160)
                        atrialAmpllab1 = tk.Label(self, textvariable=ventAmpl_var)
                        atrialAmpllab1.place(x = 230, y = 160)

                        atrialPulselab = tk.Label(self, text = "Ventricular pulse: ")
                        atrialPulselab.place(x = 100, y = 180)
                        atrialPulselab1 = tk.Label(self, textvariable=ventPulse_var)
                        atrialPulselab1.place(x = 190, y = 180)

                        activityThreshlab = tk.Label(self, text = "activity threshold: ")
                        activityThreshlab.place(x = 100, y = 200)
                        activityThreshlab1 = tk.Label(self, textvariable=activityThresh_var)
                        activityThreshlab1.place(x = 210, y = 200)

                        reactionTimelab = tk.Label(self, text = "reaction time: ")
                        reactionTimelab.place(x = 100, y = 220)
                        reactionTimelab1 = tk.Label(self, textvariable=reactionTime_var)
                        reactionTimelab1.place(x = 180, y = 220)

                        responseFaclab = tk.Label(self, text = "response factor: ")
                        responseFaclab.place(x = 100, y = 240)
                        responseFaclab1 = tk.Label(self, textvariable=responseFac_var)
                        responseFaclab1.place(x = 190, y = 240)

                        recoveryTimelab = tk.Label(self, text = "recovery time: ")
                        recoveryTimelab.place(x = 100, y = 260)
                        recoveryTimelab1 = tk.Label(self, textvariable=recoveryTime_var)
                        recoveryTimelab1.place(x = 180, y = 260)
        
        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
            
        def save_text():
            """
            checking if inputs are correct, if true, update crv files
            """
            if (inputs_correct()):
                #inputting txt into the DB
                #in other words, we are importing the csv into the DB right now
                lowerLim = self.lowerLimit.get()
                upperLim = self.upperLimit.get()
                maxSens = self.maxSens.get()
                ventricularAmp = self.ventricularAmp.get()
                ventricularPulseWidth = self.ventricularPulseWidth.get()
                activityThresh = self.activityThresh.get()
                reactionTime = self.reactionTime.get()
                responseFac = self.responseFac.get()
                recoveryTime = self.recoveryTime.get()
                
                data=[lowerLim,upperLim,maxSens,ventricularAmp,ventricularPulseWidth, activityThresh, reactionTime, responseFac, recoveryTime]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename,'r',newline='') as csvFile, tempfile:
                    reader=csv.reader(csvFile,delimiter=',')
                    writer=csv.writer(tempfile,delimiter=',')

                    for row in reader:
                        if (row[0]==currUser): #current user is this line
                            row[2:]=data
                        writer.writerow(row)
                shutil.move(tempfile.name,filename)

                #updating currentuser
                curr_data=[get_curr_user()[0],get_curr_user()[1],lowerLim,upperLim,maxSens,ventricularAmp,ventricularPulseWidth, activityThresh, reactionTime, responseFac, recoveryTime]
                with open('currentuser.csv','w', newline='') as file:
                    writer=csv.writer(file,delimiter=',')
                    writer.writerow(curr_data)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")            
    
            
        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False
            
            #maximum sensor rate
            try:
                maxSens=int(self.maxSens.get())
            except:
                return False
            if(50> maxSens or maxSens > 175):
                return False
            if(maxSens %5!=0):
                return False

            #ventricular amplitude
            vamp=float(self.ventricularAmp.get())
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(vamp not in allowed_in):
                return False

            #ventricular pulse width
            vwp=float(self.ventricularPulseWidth.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(vwp not in allowed_in):
                return False

            #activity threshold

            #reaction time
            try:
                reactionTime=int(self.reactionTime.get())
            except:
                return False
            if(10 > reactionTime or reactionTime > 50):
                return False
            if(reactionTime %10!= 0):
                return False
            
            #response factor
            try:
                responseFac=int(self.responseFac.get())
            except:
                return False
            if(1 > responseFac or responseFac > 16):
                return False
            if(reactionTime %1!= 0):
                return False
            

            #recovery time
            try:
                recoveryTime=int(self.recoveryTime.get())
            except:
                return False
            if(2> recoveryTime or recoveryTime > 16):
                return False
            if(recoveryTime %1!=0):
                return False
            
            return True
        

        # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()
        #lower
        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))
        
        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()
        #upper
        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        #maximum sensor rate
        max_sensor_rate = tk.Label(self, text="Maximum Sensor Rate", font=FONT)
        max_sensor_rate.pack()
         #max sens rate
        self.maxSens = tk.Entry(self)
        self.maxSens.pack(pady=10)
        self.maxSens.config(validate="key", validatecommand=(self.maxSens.register(is_digit_check), "%P"))

        # Ventricular Amplitude
        ventricular_amp = tk.Label(self, text="Ventricular Amplitude", font=FONT)
        ventricular_amp.pack()

        self.ventricularAmp = tk.Entry(self)
        self.ventricularAmp.pack(pady=10)
        self.ventricularAmp.config(validate="key", validatecommand=(self.ventricularAmp.register(is_digit_check), "%P"))

        # Ventricular Pulse Width
        ventricular_pulse_width = tk.Label(self, text="Ventricular Pulse Width", font=FONT)
        ventricular_pulse_width.pack()

        self.ventricularPulseWidth = tk.Entry(self)
        self.ventricularPulseWidth.pack(pady=10)
        self.ventricularPulseWidth.config(validate="key", validatecommand=(self.ventricularPulseWidth.register(is_digit_check), "%P"))

        activity_thresh= tk.Label(self, text="Activity Threshold", font=FONT)
        activity_thresh.pack()
        val = tk.StringVar()
        selectmode = ttk.Combobox(self, textvariable = val, state = "readonly")
        selectmode['values'] = ("V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High")
        selectmode.pack()
        def chosen_activity_thresh(self, *args):
            if val.get() == "V-Low":
                self.activityThresh.set(-3)
            elif val.get() == "Low":
                self.activityThresh.set(-2)
            elif val.get() == "Med-Low":
                self.activityThresh.set(-1)
            elif val.get() == "Med":
                self.activityThresh.set(0)
            elif val.get() == "Med-High":
                self.activityThresh.set(1)
            elif val.get() == "High":
                self.activityThresh.set(2)
            elif val.get() == "V-High":
                self.activityThresh.set(3)

        # Set up a trace on the StringVar to call the update function when the selection changes
        self.activityThresh = tk.StringVar()
        val.trace('w', lambda *args: chosen_activity_thresh(self, *args))


        #Reaction Time
        reaction_time = tk.Label(self, text="Reaction Time", font=FONT)
        reaction_time.pack()
        #atrial pulse width
        self.reactionTime = tk.Entry(self)
        self.reactionTime.pack(pady=10)
        self.reactionTime.config(validate="key", validatecommand=(self.reactionTime.register(is_digit_check), "%P"))


        #Response Factor
        response_factor = tk.Label(self, text="Response Factor", font=FONT)
        response_factor.pack()
        #response factor
        self.responseFac = tk.Entry(self)
        self.responseFac.pack(pady=10)
        self.responseFac.config(validate="key", validatecommand=(self.responseFac.register(is_digit_check), "%P"))


        #Recovery Time
        response_factor = tk.Label(self, text="Recovery Time", font=FONT)
        response_factor.pack()
        #recovery time
        self.recoveryTime = tk.Entry(self)
        self.recoveryTime.pack(pady=10)
        self.recoveryTime.config(validate="key", validatecommand=(self.recoveryTime.register(is_digit_check), "%P"))


        button_frame = tk.Frame(self)
        button_frame.pack()

        save_button = tk.Button(button_frame, text="Submit Data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()
    

        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

     # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

class AAIR(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="AAIR Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding

        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"


            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 14:
                                lowerLim, upperLim, maxSens, atrialAmpl, atrialPulse, atrialSens, ARPP, PVARP, Hys, rateSmooth, activityThresh, reactionTime, responseFac, recoveryTime = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return
                        
                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)

                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)

                        maxSens_var = tk.StringVar()
                        maxSens_var.set(maxSens)

                        atrialAmpl_var = tk.StringVar()
                        atrialAmpl_var.set(atrialAmpl)

                        atrialPulse_var = tk.StringVar()
                        atrialPulse_var.set(atrialPulse)

                        atrialSens_var = tk.StringVar()
                        atrialSens_var.set(atrialSens)

                        ARPP_var = tk.StringVar()
                        ARPP_var.set(ARPP)

                        PVARP_var = tk.StringVar()
                        PVARP_var.set(PVARP)

                        Hys_var = tk.StringVar()
                        Hys_var.set(Hys)

                        rateSmooth_var = tk.StringVar()
                        rateSmooth_var.set(rateSmooth)

                        activityThresh_var = tk.StringVar()
                        activityThresh_var.set(activityThresh)

                        reactionTime_var = tk.StringVar()
                        reactionTime_var.set(reactionTime)

                        responseFac_var = tk.StringVar()
                        responseFac_var.set(responseFac)

                        recoveryTime_var = tk.StringVar()
                        recoveryTime_var.set(recoveryTime)
                        

                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 100, y = 100)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 160, y = 100)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 100, y = 120)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 160, y = 120)

                        maxSenslab = tk.Label(self, text = "maximum sensor rate: ")
                        maxSenslab.place(x = 100, y = 140)
                        maxSenslab1 = tk.Label(self, textvariable=maxSens_var)
                        maxSenslab1.place(x = 180, y = 140)

                        atrialAmpllab = tk.Label(self, text = "atrial amplitude: ")
                        atrialAmpllab.place(x = 100, y = 160)
                        atrialAmpllab1 = tk.Label(self, textvariable=atrialAmpl_var)
                        atrialAmpllab1.place(x = 180, y = 160)

                        atrialPulselab = tk.Label(self, text = "atrial pulse: ")
                        atrialPulselab.place(x = 100, y = 180)
                        atrialPulselab1 = tk.Label(self, textvariable=atrialPulse_var)
                        atrialPulselab1.place(x = 180, y = 180)

                        atrialSenslab = tk.Label(self, text = "artrial sensitivity: ")
                        atrialSenslab.place(x = 100, y = 200)
                        atrialSenslab1 = tk.Label(self, textvariable=atrialSens_var)
                        atrialSenslab1.place(x = 140, y = 200)


                        ARPPlab = tk.Label(self, text = "ARP: ")
                        ARPPlab.place(x = 100, y = 220)
                        ARPPlab1 = tk.Label(self, textvariable= ARPP_var)
                        ARPPlab1.place(x = 160, y = 220)


                        PVARPlab = tk.Label(self, text = "PVARP: ")
                        PVARPlab.place(x = 100, y = 240)
                        PVARPlab1 = tk.Label(self, textvariable=PVARP_var)
                        PVARPlab1.place(x = 180, y = 240)

                        Hyslab = tk.Label(self, text = "Hysteresis: ")
                        Hyslab.place(x = 100, y = 260)
                        Hyslab1 = tk.Label(self, textvariable=Hys_var)
                        Hyslab1.place(x = 180, y = 260)

                        rateSmoothlab = tk.Label(self, text = "rate smoothing: ")
                        rateSmoothlab.place(x = 100, y = 280)
                        rateSmoothlab1 = tk.Label(self, textvariable=rateSmooth_var)
                        rateSmoothlab1.place(x = 180, y = 280)

                        activityThreshlab = tk.Label(self, text = "activity threshold: ")
                        activityThreshlab.place(x = 100, y = 300)
                        activityThreshlab1 = tk.Label(self, textvariable=activityThresh_var)
                        activityThreshlab1.place(x = 180, y = 300)

                        reactionTimelab = tk.Label(self, text = "reaction time: ")
                        reactionTimelab.place(x = 100, y = 320)
                        reactionTimelab1 = tk.Label(self, textvariable=reactionTime_var)
                        reactionTimelab1.place(x = 180, y = 320)

                        responseFaclab = tk.Label(self, text = "response factor: ")
                        responseFaclab.place(x = 100, y = 340)
                        responseFaclab1 = tk.Label(self, textvariable=responseFac_var)
                        responseFaclab1.place(x = 180, y = 340)


                        recoveryTimelab = tk.Label(self, text = "recovery time: ")
                        recoveryTimelab.place(x = 100, y = 360)
                        recoveryTimelab1 = tk.Label(self, textvariable=recoveryTime_var)
                        recoveryTimelab1.place(x = 180, y = 360)

        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
            
        def save_text():
            """
            checking if inputs are correct, if true, update crv files
            """
            if (inputs_correct()):
                #inputting txt into the DB
                #in other words, we are importing the csv into the DB right now
                lowerLim = self.lowerLimit.get()
                upperLim = self.upperLimit.get()
                maxSens = self.maxSens.get()
                atrialAmpl = self.atrialAmp.get()
                atrialPulse = self.atrialPulseWidth.get()
                atrialSens = self.atrialSens.get()
                ARPP = self.ARPP.get()
                PVARP = self.PVARP.get()
                Hys = self.Hys.get()
                rateSmooth = self.rateSmooth.get()
                activityThresh = self.activityThresh.get()
                reactionTime = self.reactionTime.get()
                responseFac = self.responseFac.get()
                recoveryTime = self.recoveryTime.get()
                
                data=[lowerLim,upperLim,maxSens,atrialAmpl,atrialPulse, atrialSens, ARPP, PVARP, Hys, rateSmooth,activityThresh, reactionTime, responseFac, recoveryTime]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename,'r',newline='') as csvFile, tempfile:
                    reader=csv.reader(csvFile,delimiter=',')
                    writer=csv.writer(tempfile,delimiter=',')

                    for row in reader:
                        if (row[0]==currUser): #current user is this line
                            row[2:]=data
                        writer.writerow(row)
                shutil.move(tempfile.name,filename)

                #updating currentuser
                curr_data=[get_curr_user()[0],get_curr_user()[1],lowerLim,upperLim,maxSens,atrialAmpl,atrialPulse, activityThresh, reactionTime, responseFac, recoveryTime]
                with open('currentuser.csv','w', newline='') as file:
                    writer=csv.writer(file,delimiter=',')
                    writer.writerow(curr_data)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")


        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False
            
            #maximum sensor rate
            try:
                maxSens=int(self.maxSens.get())
            except:
                return False
            if(50> maxSens or maxSens > 175):
                return False
            if(maxSens %5!=0):
                return False

            #atrialamp (regulated)
            atrialamp=float(self.atrialAmp.get())
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(atrialamp not in allowed_in):
                return False
                    
            #atrialpulsewidth
            awp=float(self.atrialPulseWidth.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(awp not in allowed_in):
                return False
            
            #atrialsens (regulated)
            atrialSens=float(self.atrialSens.get())
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(atrialSens not in allowed_in):
                return False
                    
            #ARP
            try:
                ARPP=int(self.ARPP.get())
            except:
                return False
            if(150> ARPP or ARPP > 500):
                return False
            if(ARPP %10!=0):
                return False
            
            #PVARP
            try:
                PVARP=int(self.PVARP.get())
            except:
                return False
            if(150> PVARP or PVARP > 500):
                return False
            if(PVARP %10!=0):
                return False


            
            #Hysteresis
            try: #incase a float is inputted instead
                Hys=int(self.Hys.get())
                lowerlim=int(self.lowerLimit.get())

            except:
                return False
            if(Hys != lowerlim and Hys != 0):
                return False
            

            #rate smoothing
            rsmooth=float(self.rateSmooth.get())
            allowed_in=[0, 3, 6, 9, 12, 15, 18, 21, 25]
            if(rsmooth not in allowed_in):
                return False

            #reaction time
            try:
                reactionTime=int(self.reactionTime.get())
            except:
                return False
            if(10 > reactionTime or reactionTime > 50):
                return False
            if(reactionTime %10!= 0):
                return False
            
            #response factor
            try:
                responseFac=int(self.responseFac.get())
            except:
                return False
            if(1 > responseFac or responseFac > 16):
                return False
            if(reactionTime %1!= 0):
                return False
            

            #recovery time
            try:
                recoveryTime=int(self.recoveryTime.get())
            except:
                return False
            if(2> recoveryTime or recoveryTime > 16):
                return False
            if(recoveryTime %1!=0):
                return False
            
            return True


        # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()
        lower_rate_limit.place(x=110, y=50)
         #lower
        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.place(x=120, y=80)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))
        
        
        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()
        upper_rate_limit.place(x=110, y=110)
        #upper
        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.place(x=120, y=140)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        #maximum sensor rate
        max_sensor_rate = tk.Label(self, text="Maximum Sensor Rate", font=FONT)
        max_sensor_rate.pack()
        max_sensor_rate.place(x=90, y=170)
         #max sens rate
        self.maxSens = tk.Entry(self)
        self.maxSens.pack(pady=10)
        self.maxSens.place(x=120, y=200)
        self.maxSens.config(validate="key", validatecommand=(self.maxSens.register(is_digit_check), "%P"))

        #atrial amplitude
        atrial_amplitude = tk.Label(self, text="Atrial Amplitude", font=FONT)
        atrial_amplitude.pack()
        atrial_amplitude.place(x=105, y=230)
        #atrial amp
        self.atrialAmp = tk.Entry(self)
        self.atrialAmp.pack(pady=10)
        self.atrialAmp.place(x=120, y=260)
        self.atrialAmp.config(validate="key", validatecommand=(self.atrialAmp.register(is_digit_check), "%P"))


        # atrial pulse
        atrial_pulse = tk.Label(self, text="Atrial Pulse Width", font=FONT)
        atrial_pulse.pack()
        atrial_pulse.place(x=110, y=290)
        #atrial pulse width
        self.atrialPulseWidth = tk.Entry(self)
        self.atrialPulseWidth.pack(pady=10)
        self.atrialPulseWidth.place(x=120, y=320)
        self.atrialPulseWidth.config(validate="key", validatecommand=(self.atrialPulseWidth.register(is_digit_check), "%P"))

        #atrial sensitivity 
        atrial_Sens = tk.Label(self, text="Atrial Sensitivity", font=FONT)
        atrial_Sens.pack()
        atrial_Sens.place(x=110, y=350)
        #atrial sensitivity
        self.atrialSens = tk.Entry(self)
        self.atrialSens.pack(pady=10)
        self.atrialSens.place(x=120, y=380)
        self.atrialSens.config(validate="key", validatecommand=(self.atrialSens.register(is_digit_check), "%P"))

        #ARP 
        A_R_P = tk.Label(self, text="ARP", font=FONT)
        A_R_P.pack()
        A_R_P.place(x=160, y=410)
        #ARP
        self.ARPP = tk.Entry(self)
        self.ARPP.pack(pady=10)
        self.ARPP.place(x=120, y=440)
        self.ARPP.config(validate="key", validatecommand=(self.ARPP.register(is_digit_check), "%P"))

        #PVARP 
        P_V_A_R_P = tk.Label(self, text="PVARP", font=FONT)
        P_V_A_R_P.pack()
        P_V_A_R_P.place(x=510, y=50)
        #PVARP
        self.PVARP = tk.Entry(self)
        self.PVARP.pack(pady=10)
        self.PVARP.place(x=490, y=80)
        self.PVARP.config(validate="key", validatecommand=(self.PVARP.register(is_digit_check), "%P"))

        #Hysteresis 
        hysteresis = tk.Label(self, text="Hysteresis", font=FONT)
        hysteresis.pack()
        hysteresis.place(x=505, y=110)
        #Hysteresis
        self.Hys = tk.Entry(self)
        self.Hys.pack(pady=10)
        self.Hys.place(x=490, y=140)
        self.Hys.config(validate="key", validatecommand=(self.Hys.register(is_digit_check), "%P"))

        #Rate Smoothing 
        rate_smoothing = tk.Label(self, text="Rate Smoothing", font=FONT)
        rate_smoothing.pack()
        rate_smoothing.place(x=490, y=170)
        #Rate Smoothing
        self.rateSmooth = tk.Entry(self)
        self.rateSmooth.pack(pady=10)
        self.rateSmooth.place(x=490, y=200)
        self.rateSmooth.config(validate="key", validatecommand=(self.rateSmooth.register(is_digit_check), "%P"))
     

        #activity Threshold
        activity_thresh = tk.Label(self, text="Activity Threshold", font=FONT)
        activity_thresh.pack()
        activity_thresh.place(x=490, y=230)
        val = tk.StringVar()
        selectmode = ttk.Combobox(self, textvariable = val, state = "readonly")
        selectmode['values'] = ("V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High")
        selectmode.place(x=485, y=260)
        def chosen_activity_thresh(self, *args):
            if val.get() == "V-Low":
                self.activityThresh.set(-3)
            elif val.get() == "Low":
                self.activityThresh.set(-2)
            elif val.get() == "Med-Low":
                self.activityThresh.set(-1)
            elif val.get() == "Med":
                self.activityThresh.set(0)
            elif val.get() == "Med-High":
                self.activityThresh.set(1)
            elif val.get() == "High":
                self.activityThresh.set(2)
            elif val.get() == "V-High":
                self.activityThresh.set(3)

        # Set up a trace on the StringVar to call the update function when the selection changes
        self.activityThresh = tk.StringVar()
        val.trace('w', lambda *args: chosen_activity_thresh(self, *args))
       


        #Reaction Time
        reaction_time = tk.Label(self, text="Reaction Time", font=FONT)
        reaction_time.pack()
        reaction_time.place(x=490, y=290)
        #atrial pulse width
        self.reactionTime = tk.Entry(self)
        self.reactionTime.pack(pady=10)
        self.reactionTime.place(x=490, y=320)
        self.reactionTime.config(validate="key", validatecommand=(self.reactionTime.register(is_digit_check), "%P"))


        #Response Factor
        response_factor = tk.Label(self, text="Response Factor", font=FONT)
        response_factor.pack()
        response_factor.place(x=490, y=350)
        #response factor
        self.responseFac = tk.Entry(self)
        self.responseFac.pack(pady=10)
        self.responseFac.place(x=490, y=380)
        self.responseFac.config(validate="key", validatecommand=(self.responseFac.register(is_digit_check), "%P"))


        #Recovery Time
        response_factor = tk.Label(self, text="Recovery Time", font=FONT)
        response_factor.pack()
        response_factor.place(x=490, y=410)
        #recovery time
        self.recoveryTime = tk.Entry(self)
        self.recoveryTime.pack(pady=10)
        self.recoveryTime.place(x=490, y=440)
        self.recoveryTime.config(validate="key", validatecommand=(self.recoveryTime.register(is_digit_check), "%P"))


        button_frame = tk.Frame(self)
        button_frame.pack()
       

        save_button = tk.Button(button_frame, text="Submit Data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()
    

        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

     # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

class VVIR(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="VVIR Mode",font=FONT)
        label.pack(pady=10,padx=10)#padding

        def load_saved_data(self):
            currUser = get_curr_user()[0]
            filename = "users.csv"


            with open(filename, 'r', newline='') as csvFile:
                reader = csv.reader(csvFile, delimiter=',')
                for row in reader:
                    if row[0] == currUser:
                        try:
                            if len(row) >= 13:
                                lowerLim, upperLim, maxSens, ventAmpl, ventPulse, ventSens, VRP, Hys, rateSmooth, activityThresh, reactionTime, responseFac, recoveryTime = row[2:]
                        except ValueError:
                            messagebox.showinfo("Error! Data is not for this op mode")
                            return
                        lowerLim_var = tk.StringVar()
                        lowerLim_var.set(lowerLim)

                        upperLim_var = tk.StringVar()
                        upperLim_var.set(upperLim)

                        maxSens_var = tk.StringVar()
                        maxSens_var.set(maxSens)

                        ventAmpl_var = tk.StringVar()
                        ventAmpl_var.set(ventAmpl)

                        ventPulse_var = tk.StringVar()
                        ventPulse_var.set(ventPulse)

                        ventSens_var = tk.StringVar()
                        ventSens_var.set(ventSens)

                        VRP_var = tk.StringVar()
                        VRP_var.set(VRP)

                        Hys_var = tk.StringVar()
                        Hys_var.set(Hys)

                        rateSmooth_var = tk.StringVar()
                        rateSmooth_var.set(rateSmooth)

                        activityThresh_var = tk.StringVar()
                        activityThresh_var.set(activityThresh)

                        reactionTime_var = tk.StringVar()
                        reactionTime_var.set(reactionTime)

                        responseFac_var = tk.StringVar()
                        responseFac_var.set(responseFac)

                        recoveryTime_var = tk.StringVar()
                        recoveryTime_var.set(recoveryTime)

                        lowerlimlab = tk.Label(self, text = "lower lim: ")
                        lowerlimlab.place(x = 300, y = 450)
                        lowerlimlab1 = tk.Label(self, textvariable=lowerLim_var)
                        lowerlimlab1.place(x = 360, y = 450)
                        
                        upperLimlab = tk.Label(self, text = "upper lim: ")
                        upperLimlab.place(x = 300, y = 470)
                        upperLimlab1 = tk.Label(self, textvariable=upperLim_var)
                        upperLimlab1.place(x = 360, y = 470)

                        maxSenslab = tk.Label(self, text = "maximum sensor rate: ")
                        maxSenslab.place(x = 300, y = 490)
                        maxSenslab1 = tk.Label(self, textvariable=maxSens_var)
                        maxSenslab1.place(x = 420, y = 490)

                        ventAmpllab = tk.Label(self, text = "vetricular amplitude: " )
                        ventAmpllab.place(x = 300, y = 510)
                        ventAmpllab1 = tk.Label(self, textvariable=ventAmpl_var)
                        ventAmpllab1.place(x = 410, y = 510)

                        ventPulselab = tk.Label(self, text = "ventricular pulse: ")
                        ventPulselab.place(x = 300, y = 530)
                        ventPulselab1 = tk.Label(self, textvariable=ventPulse_var)
                        ventPulselab1.place(x = 395, y = 530)

                        ventSenslab = tk.Label(self, text = "ventricular sensitivity: ")
                        ventSenslab.place(x = 300, y = 550)
                        ventSenslab1 = tk.Label(self, textvariable=ventSens_var)
                        ventSenslab1.place(x = 390, y = 550)


                        VRPlab = tk.Label(self, text = "VRP: ")
                        VRPlab.place(x = 300, y = 570)
                        VRPlab1 = tk.Label(self, textvariable= VRP_var)
                        VRPlab1.place(x = 330, y = 570)


                        Hyslab = tk.Label(self, text = "Hysteresis: ")
                        Hyslab.place(x = 300, y = 590)
                        Hyslab1 = tk.Label(self, textvariable=Hys_var)
                        Hyslab1.place(x = 350, y = 590)

                        rateSmoothlab = tk.Label(self, text = "rate smoothing: ")
                        rateSmoothlab.place(x = 300, y = 610)
                        rateSmoothlab1 = tk.Label(self, textvariable=rateSmooth_var)
                        rateSmoothlab1.place(x = 400, y = 610)

                        activityThreshlab = tk.Label(self, text = "activity threshold: ")
                        activityThreshlab.place(x = 300, y = 630)
                        activityThreshlab1 = tk.Label(self, textvariable=activityThresh_var)
                        activityThreshlab1.place(x = 380, y = 630)

                        reactionTimelab = tk.Label(self, text = "reaction time: ")
                        reactionTimelab.place(x = 300, y = 650)
                        reactionTimelab1 = tk.Label(self, textvariable=reactionTime_var)
                        reactionTimelab1.place(x = 390, y = 650)

                        responseFaclab = tk.Label(self, text = "response factor: ")
                        responseFaclab.place(x = 300, y = 670)
                        responseFaclab1 = tk.Label(self, textvariable=responseFac_var)
                        responseFaclab1.place(x = 380, y = 670)


                        recoveryTimelab = tk.Label(self, text = "recovery time: ")
                        recoveryTimelab.place(x = 300, y = 690)
                        recoveryTimelab1 = tk.Label(self, textvariable=recoveryTime_var)
                        recoveryTimelab1.place(x = 380, y = 690)

        def is_digit_check(P):
            """
            limits input on entrys
            """
            if P.replace(".", "").isnumeric():
                return True
            elif P=="":
                return True
            else:
                return False
            
        def save_text():
            """
            checking if inputs are correct, if true, update crv files
            """
            if (inputs_correct()):
                #inputting txt into the DB
                #in other words, we are importing the csv into the DB right now
                lowerLim = self.lowerLimit.get()
                upperLim = self.upperLimit.get()
                maxSens = self.maxSens.get()
                ventAmpl = self.ventAmpl.get()
                ventPulse = self.ventPulse.get()
                ventSens = self.ventSens.get()
                VRP = self.VRP.get()
                Hys = self.Hys.get()
                rateSmooth = self.rateSmooth.get()
                activityThresh = self.activityThresh.get()
                reactionTime = self.reactionTime.get()
                responseFac = self.responseFac.get()
                recoveryTime = self.recoveryTime.get()
                
                data=[lowerLim,upperLim,maxSens,ventAmpl,ventPulse, ventSens, VRP, Hys, rateSmooth,activityThresh, reactionTime, responseFac, recoveryTime]
                send_data_via_serial(data) 

                #line we want to write into csv
                currUser=get_curr_user()[0]
                filename="users.csv"
                tempfile =NamedTemporaryFile('w+t',newline='',delete=False)

                with open(filename,'r',newline='') as csvFile, tempfile:
                    reader=csv.reader(csvFile,delimiter=',')
                    writer=csv.writer(tempfile,delimiter=',')

                    for row in reader:
                        if (row[0]==currUser): #current user is this line
                            row[2:]=data
                        writer.writerow(row)
                shutil.move(tempfile.name,filename)

                #updating currentuser
                curr_data=[get_curr_user()[0],get_curr_user()[1],lowerLim,upperLim,maxSens,ventAmpl,ventPulse, ventSens, VRP, Hys, rateSmooth,activityThresh, reactionTime, responseFac, recoveryTime]
                with open('currentuser.csv','w', newline='') as file:
                    writer=csv.writer(file,delimiter=',')
                    writer.writerow(curr_data)
                self.generate_ecg()
            else:
                messagebox.showinfo("","Please correct your inputs.")


        def inputs_correct():
            """
            checking if inputs are correct
            """
            #lower rate limit
            try: #incase a float is inputted instead
                lowerlim=int(self.lowerLimit.get())
            except:
                return False
            if(lowerlim < 30 or lowerlim >175):
                return False
            if(30<=lowerlim<=50 or 90<=lowerlim<=175):
                if lowerlim%5!=0:
                    return False
            #upper rate limit
            try:
                upperlim=int(self.upperLimit.get())
            except:
                return False
            if(50> upperlim or upperlim > 175):
                return False
            if(upperlim %5!=0):
                return False
            
            #maximum sensor rate
            try:
                maxSens=int(self.maxSens.get())
            except:
                return False
            if(50> maxSens or maxSens > 175):
                return False
            if(maxSens %5!=0):
                return False

            #ventAmpl (regulated)
            ventAmpl=float(self.ventAmpl.get())
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(ventAmpl not in allowed_in):
                return False
                    
            #atrialpulsewidth
            vpw=float(self.ventPulse.get())
            allowed_in=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
            if(vpw not in allowed_in):
                return False
            
            #atrialsens (regulated)
            ventSens=float(self.ventSens.get())
            allowed_in=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0]
            if(ventSens not in allowed_in):
                return False
                    
            #VRP
            try:
                VRP=int(self.VRP.get())
            except:
                return False
            if(150> VRP or VRP > 500):
                return False
            if(VRP %10!=0):
                return False

            
            #Hysteresis
            try: #incase a float is inputted instead
                Hys=int(self.Hys.get())
                lowerlim=int(self.lowerLimit.get())

            except:
                return False
            if(Hys != lowerlim and Hys != 0):
                return False
            

            #rate smoothing
            rsmooth=float(self.rateSmooth.get())
            allowed_in=[0, 3, 6, 9, 12, 15, 18, 21, 25]
            if(rsmooth not in allowed_in):
                return False

            #reaction time
            try:
                reactionTime=int(self.reactionTime.get())
            except:
                return False
            if(10 > reactionTime or reactionTime > 50):
                return False
            if(reactionTime %10!= 0):
                return False
            
            #response factor
            try:
                responseFac=int(self.responseFac.get())
            except:
                return False
            if(1 > responseFac or responseFac > 16):
                return False
            if(reactionTime %1!= 0):
                return False
            

            #recovery time
            try:
                recoveryTime=int(self.recoveryTime.get())
            except:
                return False
            if(2> recoveryTime or recoveryTime > 16):
                return False
            if(recoveryTime %1!=0):
                return False
            
            return True


        # Lower Rate Limit
        lower_rate_limit = tk.Label(self, text="Lower Rate Limit", font=FONT)
        lower_rate_limit.pack()
        lower_rate_limit.place(x=110, y=50)
         #lower
        self.lowerLimit = tk.Entry(self)
        self.lowerLimit.pack(pady=10)
        self.lowerLimit.place(x=120, y=80)
        self.lowerLimit.config(validate="key", validatecommand=(self.lowerLimit.register(is_digit_check), "%P"))
        
        
        # Upper Rate Limit
        upper_rate_limit = tk.Label(self, text="Upper Rate Limit", font=FONT)
        upper_rate_limit.pack()
        upper_rate_limit.place(x=110, y=110)
        #upper
        self.upperLimit = tk.Entry(self)
        self.upperLimit.pack(pady=10)
        self.upperLimit.place(x=120, y=140)
        self.upperLimit.config(validate="key", validatecommand=(self.upperLimit.register(is_digit_check), "%P"))

        #maximum sensor rate
        max_sensor_rate = tk.Label(self, text="Maximum Sensor Rate", font=FONT)
        max_sensor_rate.pack()
        max_sensor_rate.place(x=90, y=170)
         #max sens rate
        self.maxSens = tk.Entry(self)
        self.maxSens.pack(pady=10)
        self.maxSens.place(x=120, y=200)
        self.maxSens.config(validate="key", validatecommand=(self.maxSens.register(is_digit_check), "%P"))

        #Ventricular Amplitude
        vent_amplitude = tk.Label(self, text="Ventricular Amplitude", font=FONT)
        vent_amplitude.pack()
        vent_amplitude.place(x=105, y=230)
        #Ventricular Amplitude
        self.ventAmpl = tk.Entry(self)
        self.ventAmpl.pack(pady=10)
        self.ventAmpl.place(x=120, y=260)
        self.ventAmpl.config(validate="key", validatecommand=(self.ventAmpl.register(is_digit_check), "%P"))


        # Ventricular pulse
        vent_pulse = tk.Label(self, text="Ventricular Pulse Width", font=FONT)
        vent_pulse.pack()
        vent_pulse.place(x=110, y=290)
        #Ventricular pulse width
        self.ventPulse = tk.Entry(self)
        self.ventPulse.pack(pady=10)
        self.ventPulse.place(x=120, y=320)
        self.ventPulse.config(validate="key", validatecommand=(self.ventPulse.register(is_digit_check), "%P"))

        #Ventricular sensitivity 
        ventricular_Sens = tk.Label(self, text="Ventricular Sensitivity", font=FONT)
        ventricular_Sens.pack()
        ventricular_Sens.place(x=110, y=350)
        #Ventricular sensitivity
        self.ventSens = tk.Entry(self)
        self.ventSens.pack(pady=10)
        self.ventSens.place(x=120, y=380)
        self.ventSens.config(validate="key", validatecommand=(self.ventSens.register(is_digit_check), "%P"))

        #VRP 
        V_R_P = tk.Label(self, text="VRP", font=FONT)
        V_R_P.pack()
        V_R_P.place(x=160, y=410)
        #VRP
        self.VRP = tk.Entry(self)
        self.VRP.pack(pady=10)
        self.VRP.place(x=120, y=440)
        self.VRP.config(validate="key", validatecommand=(self.VRP.register(is_digit_check), "%P"))

        #Hysteresis 
        hysteresis = tk.Label(self, text="Hysteresis", font=FONT)
        hysteresis.pack()
        hysteresis.place(x=505, y=50)
        #Hysteresis
        self.Hys = tk.Entry(self)
        self.Hys.pack(pady=10)
        self.Hys.place(x=490, y=80)
        self.Hys.config(validate="key", validatecommand=(self.Hys.register(is_digit_check), "%P"))

        #Rate Smoothing 
        rate_smoothing = tk.Label(self, text="Rate Smoothing", font=FONT)
        rate_smoothing.pack()
        rate_smoothing.place(x=490, y=110)
        #Rate Smoothing
        self.rateSmooth = tk.Entry(self)
        self.rateSmooth.pack(pady=10)
        self.rateSmooth.place(x=490, y=140)
        self.rateSmooth.config(validate="key", validatecommand=(self.rateSmooth.register(is_digit_check), "%P"))
     


        activity_thresh= tk.Label(self, text="Activity Threshold", font=FONT)
        activity_thresh.pack()
        activity_thresh.place(x=470, y=170)
        val = tk.StringVar()
        selectmode = ttk.Combobox(self, textvariable = val, state = "readonly")
        selectmode['values'] = ("V-Low", "Low", "Med-Low", "Med", "Med-High", "High", "V-High")
        selectmode.place(x=485, y=200)
        def chosen_activity_thresh(self, *args):
            if val.get() == "V-Low":
                self.activityThresh.set(-3)
            elif val.get() == "Low":
                self.activityThresh.set(-2)
            elif val.get() == "Med-Low":
                self.activityThresh.set(-1)
            elif val.get() == "Med":
                self.activityThresh.set(0)
            elif val.get() == "Med-High":
                self.activityThresh.set(1)
            elif val.get() == "High":
                self.activityThresh.set(2)
            elif val.get() == "V-High":
                self.activityThresh.set(3)

        # Set up a trace on the StringVar to call the update function when the selection changes
        self.activityThresh = tk.StringVar()
        val.trace('w', lambda *args: chosen_activity_thresh(self, *args))
       


        #Reaction Time
        reaction_time = tk.Label(self, text="Reaction Time", font=FONT)
        reaction_time.pack()
        reaction_time.place(x=490, y=230)
        #atrial pulse width
        self.reactionTime = tk.Entry(self)
        self.reactionTime.pack(pady=10)
        self.reactionTime.place(x=490, y=260)
        self.reactionTime.config(validate="key", validatecommand=(self.reactionTime.register(is_digit_check), "%P"))


        #Response Factor
        response_factor = tk.Label(self, text="Response Factor", font=FONT)
        response_factor.pack()
        response_factor.place(x=490, y=290)
        #response factor
        self.responseFac = tk.Entry(self)
        self.responseFac.pack(pady=10)
        self.responseFac.place(x=490, y=320)
        self.responseFac.config(validate="key", validatecommand=(self.responseFac.register(is_digit_check), "%P"))


        #Recovery Time
        response_factor = tk.Label(self, text="Recovery Time", font=FONT)
        response_factor.pack()
        response_factor.place(x=490, y=350)
        #recovery time
        self.recoveryTime = tk.Entry(self)
        self.recoveryTime.pack(pady=10)
        self.recoveryTime.place(x=490, y=380)
        self.recoveryTime.config(validate="key", validatecommand=(self.recoveryTime.register(is_digit_check), "%P"))


        button_frame = tk.Frame(self)
        button_frame.pack()
       

        save_button = tk.Button(button_frame, text="Submit Data", command = lambda: [save_text()])
        save_button.pack()

        retrieveDataBtn = tk.Button(button_frame, text = "Retrieve Prev Data", command = lambda: [load_saved_data(self)])
        retrieveDataBtn.pack()
    

        my_label = tk.Label(self, text= '')
        my_label.pack()

        button1 = tk.Button(self,text="Back to Mode Selection",command=lambda: controller.show_frame(Front))
        button1.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

     # Save the stop button as an attribute
        self.stop_button = tk.Button(button_frame, text="Stop ECG", command=self.stop_ecg_update)
        self.stop_button.pack()

        # Save the resume button as an attribute
        self.resume_button = tk.Button(button_frame, text="Resume ECG", command=self.resume_ecg_update)
        self.resume_button.pack()

        # Initially, you might want to disable the resume button since there's nothing to resume yet
        self.resume_button.config(state=tk.DISABLED)

        reset_button = tk.Button(button_frame, text="Reset ECG", command=self.reset_ecg)
        reset_button.pack()

        #errormsg
        msg=tk.Label(self,text="")
        msg.pack()

    def reset_ecg(self):
        # Check if the ECG update loop is running and stop it
        if self.running:
            self.stop_ecg_update()

        # Clear the ECG signal data and reset the time counter
        self.ecg_signal = np.array([])
        self.ecg_time = 0

        # Clear the graph if the window is still open
        if self.ecg_window and self.canvas:
            self.ax.clear()
            self.ax.set_title("Simulated ECG Signal")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Voltage (mV)")
            self.canvas.draw()

    def create_ecg_waveform(self, duration, lrl, url, atrial_amp, atrial_pulse_width):
   
        # Time vector
        dt = 1.0 / 1000  # 1 millisecond time step
        t = np.arange(0, duration, dt)

        # Initialize ECG signal
        ecg_signal = np.zeros_like(t)

        # Calculate beat durations at LRL and URL
        beat_duration_lrl = 60.0 / lrl  # in seconds
        beat_duration_url = 60.0 / url  # in seconds

        # Create the ECG waveform
        time_elapsed = 0
        while time_elapsed < duration:
            # Linear interpolation for beat duration within LRL and URL range
            beat_duration = np.interp(time_elapsed, [0, duration], [beat_duration_lrl, beat_duration_url])

            # P-wave parameters
            p_start = time_elapsed
            p_duration = atrial_pulse_width
            p_peak = p_start + p_duration / 2

            # QRS complex parameters
            qrs_start = p_start + p_duration
            qrs_duration = 0.08  # fixed duration of QRS complex
            qrs_peak = qrs_start + qrs_duration / 2

            # T-wave parameters
            t_start = qrs_start + qrs_duration
            t_duration = beat_duration - p_duration - qrs_duration
            t_peak = t_start + t_duration / 2

            # Adding P, QRS, T components to the ECG signal
            ecg_signal += atrial_amp * np.exp(-((t - p_peak)**2 / (2 * (p_duration / 2)**2)))  # P-wave
            ecg_signal += 1.5 * atrial_amp * np.exp(-((t - qrs_peak)**2 / (2 * (qrs_duration / 2)**2)))  # QRS complex
            ecg_signal += 0.75 * atrial_amp * np.exp(-((t - t_peak)**2 / (2 * (t_duration / 2)**2)))  # T-wave

            time_elapsed += beat_duration

        return t, ecg_signal

    def update_ecg_continuously(self):
        segment_duration = 1  # Duration of each segment (in seconds)
        self.running = True  # Start the update loop
        self.paused = False  # Ensure not paused when starting
        while self.running:
            if self.paused:
                   time.sleep(1)  # Pause updating, check every second
                   continue
            try:
                # Fetch values from the input fields
                lower_lim = self.stored_lower_lim
                upper_lim = self.stored_upper_lim
                atrial_amp = self.stored_atrial_amp
                atrial_pulse_width = self.stored_atrial_pulse_width

                # Generate the ECG waveform for a segment
                t, ecg_segment = self.create_ecg_waveform(segment_duration, lower_lim, upper_lim, atrial_amp, atrial_pulse_width)

                if not self.ecg_window:
                    return

                # Append the new segment to the existing data
                self.ecg_signal = np.concatenate((self.ecg_signal, ecg_segment))
                self.ecg_time += segment_duration

                # Update atrial graph
                self.ax1.clear()
                self.ax1.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal, color = 'red')
                self.ax1.set_title("Atrial Signal")
                # ...

                # Update ventricular graph
                self.ax2.clear()
                self.ax2.plot(np.arange(0, self.ecg_time, 1.0 / 1000), self.ecg_signal)
                self.ax2.set_title("Ventricular Signal")
                # ...

                self.canvas.draw()

                time.sleep(segment_duration)  # Sleep for the duration of the segment

            except ValueError:
                # Handle any errors here
                time.sleep(1)
                continue

    def generate_ecg(self):
        # Create the ECG window if it doesn't exist
        if not hasattr(self, 'ecg_window') or not self.ecg_window.winfo_exists():
            self.ecg_window = tk.Toplevel(self)
            self.ecg_window.title("ECG Graphs")
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))  # Two subplots
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.ecg_window)
            self.canvas.get_tk_widget().pack()

        # Start the thread for continuous ECG update if it's not already running
        if not hasattr(self, 'ecg_update_thread') or not self.ecg_update_thread.is_alive():
            self.running = True
            self.paused = False
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
    
    def stop_ecg_update(self):
        # Set the paused flag to True to pause the ECG update loop
        self.paused = True

        self.stop_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
    
    def resume_ecg_update(self):
        if not self.running:
            # Restart the update thread if it's not running
            self.running = True
            self.ecg_update_thread = threading.Thread(target=self.update_ecg_continuously)
            self.ecg_update_thread.daemon = True
            self.ecg_update_thread.start()
        self.paused = False  # Resume updating

        # Enable the stop button and disable the resume button
        self.stop_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

# Driver Code
app=Window()
app.title("PaceMaker")
#adjusting starting size of window
app.minsize(700,700)
app.mainloop()

# conn.commit()
# conn.close()