import simpy
import random
import matplotlib.pyplot as plt

import sys
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QApplication
from PyQt5.QtGui import QFont
import time

class Airport(object):
    totalCheckin = 0
    totalSecurity = 0
    totalBoarding = 0
    cur_passenger = 0
    avgCheckin = []
    avgBoarding = []
    avgSecurity = []
    def __init__(self, num_checkin = 5, num_security = 5, num_boarding = 1, num_passengers = 100, arrival_limit = 100):
        self.env = simpy.Environment()
        self.num_checkin = num_checkin
        self.num_security = num_security
        self.num_boarding = num_boarding
        self.curr_checkin = 0
        self.curr_security = 0
        self.curr_boarding = 0
        self.curr_done = 0
        self.checkin = simpy.Resource(self.env, num_checkin)
        self.security = simpy.Resource(self.env, num_security)
        self.boarding = simpy.Resource(self.env, num_boarding)
        self.num_passengers = num_passengers
        self.passengers = [
            Passenger(self, random.randint(0, arrival_limit)) for i in range(num_passengers)
        ]

class Passenger(object):
    def __init__(self, airport, arrival_time):
        self.arrival_t = arrival_time
        self.airport = airport
        self.action = self.airport.env.process(self.run())
    def run(self):

        #wait for arrival
        delta = self.arrival_t - self.airport.env.now
        yield self.airport.env.timeout(delta)
        print("time:", self.airport.env.now, "passenger arrived")

        #check in 
        with self.airport.checkin.request() as request:
            self.airport.curr_checkin += 1
            yield request
            #do the check in
            yield self.airport.env.timeout(random.randint(1,5)) # 1-5 minutes to check in
            self.airport.curr_checkin -= 1
        print("time:", self.airport.env.now, "checking in done")
        self.airport.totalCheckin += self.airport.env.now - self.arrival_t


        #security
        with self.airport.security.request() as request:
            self.airport.curr_security+=1
            yield request
            #do the security
            yield self.airport.env.timeout(random.randint(2,6)) # 2-6 minutes
            self.airport.curr_security -= 1
        print("time:", self.airport.env.now, "security check done")
        self.airport.totalSecurity += self.airport.env.now - self.arrival_t

        #boarding
        with self.airport.boarding.request() as request:
            self.airport.curr_boarding += 1
            yield request
            #do the boarding
            yield self.airport.env.timeout(random.randint(1,2)) #1-2 minutes to board
            self.airport.curr_boarding -= 1
        print("time:", self.airport.env.now, "boarding done")
        self.airport.curr_done += 1
        print("time:", self.airport.env.now, f"passenger arrived at {self.arrival_t} and done at {self.airport.env.now}")
        self.airport.totalBoarding += self.airport.env.now - self.arrival_t
        self.airport.cur_passenger = self.airport.cur_passenger + 1
        # Statistics
        
        self.airport.avgCheckin.append(self.airport.totalCheckin/self.airport.cur_passenger)
        self.airport.avgSecurity.append(self.airport.totalSecurity/self.airport.cur_passenger)
        self.airport.avgBoarding.append(self.airport.totalBoarding/self.airport.cur_passenger)
        
        if self.airport.cur_passenger == self.airport.num_passengers:
            print("Average Checkin Time: ", self.airport.totalCheckin/self.airport.num_passengers)
            print("Average Security Time: ", self.airport.totalSecurity/self.airport.num_passengers)
            print("Average Boarding Time: ", self.airport.totalBoarding/self.airport.num_passengers)
            custList = list(range(1,101))
            
            # Plotting average Checking
            plt.figure()
            plt.title("Average Checking Time vs No of Customers")
            plt.scatter(custList, self.airport.avgCheckin)
            plt.plot(custList, self.airport.avgCheckin)
            plt.savefig('checking_time_vs_customers.png')
            
            #Average Security
            plt.figure()
            plt.title("Average Security Time vs No of Customers")
            plt.scatter(custList, self.airport.avgSecurity)
            plt.plot(custList, self.airport.avgSecurity)
            plt.savefig('security_time_vs_customers.png')
            
            # Average Boarding
            plt.figure()
            plt.title("Average Boarding Time vs No of Customers")
            plt.scatter(custList, self.airport.avgBoarding)
            plt.plot(custList, self.airport.avgBoarding)
            plt.savefig('boarding_time_vs_customers.png')

            plt.show()
            
class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.myfont = QFont()
        self.myfont.setPointSize(15)
        self.setWindowTitle("Airport Simulation")
        self.setMinimumSize(QSize(960, 720))
        self.airport = Airport()
        self.checkin_labels = [
            QLabel(f"[C{i+1}]", self) for i in range(self.airport.num_checkin)
        ]
        self.security_labels = [
            QLabel(f"[S{i+1}]", self) for i in range(self.airport.num_security)
        ]
        self.boarding_labels = [
            QLabel(f"[B{i+1}]", self) for i in range(self.airport.num_boarding)
        ]
        c_x = 100
        c_y = 150
        s_x = 400
        s_y = 150
        b_x = 700
        b_y = 150
        for i in range(self.airport.num_checkin):
            self.checkin_labels[i].move(c_x + i*50, c_y)
            self.checkin_labels[i].adjustSize()
        for i in range(self.airport.num_security):
            self.security_labels[i].move(s_x + i*50, s_y)
            self.security_labels[i].adjustSize()
        for i in range(self.airport.num_boarding):
            self.boarding_labels[i].move(b_x + i*50, b_y)
            self.boarding_labels[i].adjustSize()

        self.time_label = QLabel(f"time: {self.airport.env.now}", self)
        self.time_label.move(400, 25)
        self.checkin_num_label = QLabel(f"waiting: {self.airport.curr_checkin}", self)
        self.checkin_num_label.move(100, 200)
        self.checkin_num_label.adjustSize()
        self.security_num_label = QLabel(f"waiting: {self.airport.curr_security}", self)
        self.security_num_label.move(400, 200)
        self.security_num_label.adjustSize()
        self.boarding_num_label = QLabel(f"waiting: {self.airport.curr_boarding}", self)
        self.boarding_num_label.move(700, 200)
        self.boarding_num_label.adjustSize()
        self.done_num_label = QLabel(f"done: {self.airport.curr_done}", self)
        self.done_num_label.move(400, 300)

        self.next_button = QPushButton("Next Time Step", self)
        self.next_button.move(400, 400)
        self.next_button.resize(100, 50)
        self.next_button.setFont(self.myfont)
        self.next_button.adjustSize()
        self.next_button.clicked.connect(self.nextStep)
        self.ff_button = QPushButton("Fast Forward to the end", self)
        self.ff_button.move(400, 500)
        self.ff_button.resize(100, 50)
        self.ff_button.setFont(self.myfont)
        self.ff_button.adjustSize()
        self.ff_button.clicked.connect(self.fastForward)

    def updateUI(self):
        self.time_label.setText(f"time:{self.airport.env.now}")
        self.time_label.adjustSize()
        self.checkin_num_label.setText(f"waiting: {self.airport.curr_checkin}")
        self.checkin_num_label.adjustSize()
        self.security_num_label.setText(f"waiting: {self.airport.curr_security}")
        self.security_num_label.adjustSize()
        self.boarding_num_label.setText(f"waiting: {self.airport.curr_boarding}")
        self.boarding_num_label.adjustSize()
        self.done_num_label.setText(f"done: {self.airport.curr_done}")
        self.done_num_label.adjustSize()

    def nextStep(self):
        try:
            self.airport.env.step()
        except simpy.core.EmptySchedule:
            print("finished")
            return False
        curr_time = self.airport.env.now
        while self.airport.env.peek() == curr_time:
            try:
                self.airport.env.step()
            except simpy.core.EmptySchedule:
                print("finished")
                return False

        self.updateUI()
        
        return True

    def fastForward(self):
        self.airport.env.run()
        self.updateUI()
        
                

app = QApplication(sys.argv)
myfont = QFont()
myfont.setWeight(60)
myfont.setPointSize(20)
app.setFont(myfont, 'QLabel')
gui = Gui()
gui.show()
sys.exit(app.exec_())


# airport.env.run()