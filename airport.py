import simpy
import random

class Airport(object):
    def __init__(self, num_checkin = 5, num_security = 5, num_boarding = 1, num_passengers = 100, arrival_limit = 100):
        self.env = simpy.Environment()
        self.checkin = simpy.Resource(self.env, num_checkin)
        self.security = simpy.Resource(self.env, num_security)
        self.boarding = simpy.Resource(self.env, num_boarding)
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

        #security
        with self.airport.security.request() as request:
            yield request
            #do the security
            yield self.airport.env.timeout(random.randint(2,6)) # 2-6 minutes
        print("time:", self.airport.env.now, "security check done")

        #boarding
        with self.airport.boarding.request() as request:
            yield request
            #do the boarding
            yield self.airport.env.timeout(random.randint(1,2)) #1-2 minutes to board
        print("time:", self.airport.env.now, "boarding done")
        
        print("time:", self.airport.env.now, f"passenger arrived at {self.arrival_t} and done at {self.airport.env.now}")

airport = Airport()
airport.env.run()