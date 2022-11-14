import simpy
import random
import matplotlib.pyplot as plt

import sys
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QApplication
from PyQt5.QtGui import QFont

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
            yield request
            #do the check in
            yield self.airport.env.timeout(random.randint(1,5)) # 1-5 minutes to check in
        print("time:", self.airport.env.now, "checking in done")
        self.airport.totalCheckin += self.airport.env.now - self.arrival_t


        #security
        with self.airport.security.request() as request:
            yield request
            #do the security
            yield self.airport.env.timeout(random.randint(2,6)) # 2-6 minutes
        print("time:", self.airport.env.now, "security check done")
        self.airport.totalSecurity += self.airport.env.now - self.arrival_t

        #boarding
        with self.airport.boarding.request() as request:
            yield request
            #do the boarding
            yield self.airport.env.timeout(random.randint(1,2)) #1-2 minutes to board
        print("time:", self.airport.env.now, "boarding done")
        
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
        self.setWindowTitle("Airport Simulation")
        self.setMinimumSize(QSize(960, 720))
        self.airport = Airport()
        self.checkin_labels = [
            QLabel(f"[C]", self) for i in range(self.airport.num_checkin)
        ]
        self.security_labels = [
            QLabel(f"[S]", self) for i in range(self.airport.num_security)
        ]
        self.boarding_labels = [
            QLabel(f"[B]", self) for i in range(self.airport.num_boarding)
        ]
        c_x = 100
        c_y = 50
        s_x = 400
        s_y = 50
        b_x = 700
        b_y = 50
        for i in range(self.airport.num_checkin):
            self.checkin_labels[i].move(c_x + i*50, c_y)
            self.checkin_labels[i].adjustSize()
        for i in range(self.airport.num_security):
            self.security_labels[i].move(s_x + i*50, s_y)
            self.security_labels[i].adjustSize()
        for i in range(self.airport.num_boarding):
            self.boarding_labels[i].move(b_x + i*50, b_y)
            self.boarding_labels[i].adjustSize()






app = QApplication(sys.argv)
myfont = QFont()
myfont.setWeight(60)
myfont.setPointSize(24)
app.setFont(myfont, 'QLabel')
gui = Gui()
gui.show()
sys.exit(app.exec_())


# airport.env.run()