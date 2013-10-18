import abc
from abc import ABCMeta
import java.util.ArrayList as ArrayList
import random
import math
from springpython.context import ApplicationContext
from springpython.config import XMLConfig
from springpython.aop import *
from vehicleRUM2 import *

class location():
    __slots__ = ('x', 'y')       

class battery():
    
    energy_full = 10
    energy = energy_full   
    
    def __init__(self):
        self.energy = self.energy_full   
        
    def consume(self, amount):
        self.energy -= amount   
    
        
class engine():
    
    'maximum gears this engine supports'
    maxGears = 6
    'current gear, 0 means no gear selected'
    gear = 0
    'consumption per hour driven'
    consumption = 0
    'speed in km/h'
    speed = 0
    
    def __init__(self, battery):
        self.gear = 0
        self.speed = 0
        self.status = "off"   
        self.battery = battery   
        self.consumption = 0
        
    def turnOn(self):
        self.status = "idle"
        if self.battery.energy<=0.01:
            self.turnOff()
        else:            
            self.setGear(1) 
            self.battery.consume(self.consumption)
        
    def turnOff(self):
        self.status = "off"
        self.consumption = 0
        
    def drive(self, distance):
        if(self.status == "off"):
            return False
        self.status = "driving"
        self.battery.consume(distance/self.speed*self.consumption)  
        print(self.battery.energy)
        if self.battery.energy<=0:
            print("no more power")
            self.turnOff()
            return False
        return True
        
    def setGear(self, gear):
        if(gear<=self.maxGears):
            self.gear = gear
        if self.status == "idle":
            self.consumption = 0.01
        else:
            if self.status == "off":
                self.consumption = 0
            else:
                self.setConsumption()
                
    def setSpeed(self, throttle):
        if throttle > 100:
            throttle = 100
        else:
            if throttle < 0:
                'engine switches off'
                self.turnOff()
                return
        
        'at 40% throttle would reach these optimal speeds'
        'gear 1 -> 10 km/h'
        'gear 2 -> 20 km/h'
        'gear 3 -> 35 km/h'
        'gear 4 -> 45 km/h'
        'gear 5 -> 60 km/h'
        'gear 6 -> 80 km/h'
        "assume speed changes by 1% per 1% more/less throttle, can't drop more than 20% below optimal"
        if self.gear==1:
            self.speed = max((100+throttle-40),0.8)*10/100
        elif self.gear==2:
            self.speed = max((100+throttle-40),0.8)*20/100            
        elif self.gear==3:
            self.speed = max((100+throttle-40),0.8)*35/100
        elif self.gear==4:
            self.speed = max((100+throttle-40),0.8)*45/100
        elif self.gear==5:
            self.speed = max((100+throttle-40),0.8)*60/100
        else:
            self.speed = max((100+throttle-40),0.8)*80/100             
        self.setConsumption()                                 
         
                
    def setConsumption(self):
        
        'consumption of fuel at optimal speed is 10 fuel per hour'  
        'optimal speeds:'      
        'gear 1 -> 10 km/h'
        'gear 2 -> 20 km/h'
        'gear 3 -> 35 km/h'
        'gear 4 -> 45 km/h'
        'gear 5 -> 60 km/h'
        'gear 6 -> 80 km/h'
        'for every 10% that the speed is over this optimal, consumption is up by 15%' 
        'for every 10% that it is below this optimal, consumption drops by 5%'
        
        if self.gear==1:            
            if self.speed<10:   
                self.consumption = ((self.speed-10)/10.0/0.1*5+100)*10/100
            else:
                self.consumption = ((self.speed-10)/10.0/0.1*15+100)*10/100
        elif self.gear==2:
            if self.speed<20:   
                self.consumption = ((self.speed-20)/20.0/0.1*5+100)*10/100
            else:
                self.consumption = ((self.speed-20)/20.0/0.1*15+100)*10/100
        elif self.gear==3:
            if self.speed<35:   
                self.consumption = ((self.speed-35)/35.0/0.1*5+100)*10/100
            else:
                self.consumption = ((self.speed-35)/35.0/0.1*15+100)*10/100
        elif self.gear==4:
            if self.speed<45:   
                self.consumption = ((self.speed-45)/45.0/0.1*5+100)*10/100
            else:
                self.consumption = ((self.speed-45)/45.0/0.1*15+100)*10/100
        elif self.gear==5:
            if self.speed<60:   
                self.consumption = ((self.speed-60)/60.0/0.1*5+100)*10/100
            else:
                self.consumption = ((self.speed-60)/60.0/0.1*15+100)*10/100
        else:
            if self.speed<80:   
                self.consumption = ((self.speed-80)/80.0/0.1*5+100)*10/100
            else:
                self.consumption = ((self.speed-80)/80.0/0.1*15+100)*10/100
        
class route():
    
    def __init__(self, locations, current):
        self.locations = locations      
        self.currentLocation = current
        self.coveredDistance = 0
    
    def getRoute(self):        
        'sort locations to create the shortest route?' 
        return self.locations
    
    def visited(self):
        'remove the first location from the route'        
        self.coveredDistance+=self.getDistance(self.currentLocation, self.locations.get(0))        
        self.currentLocation = self.locations.get(0)
        self.locations.remove(0)
        
    def getRemainingDistance(self):
        distance = 0
        oldLocation = self.currentLocation
        for location in self.locations:
            distance += self.getDistance(oldLocation, location)
            oldLocation = location
        return distance
        
    def getDistanceToNext(self):    
        return self.getDistance(self.currentLocation, self.locations.get(0))
    
    def getDistance(self, currentLoc, nextLoc):    
        return math.sqrt(math.pow(math.fabs(currentLoc[0]-nextLoc[0]),2.0)+math.pow(math.fabs(currentLoc[1]-nextLoc[1]), 2.0))
    

class abstractVehicle():
    __metaclass__ = ABCMeta

    def __init__(self, route, engine, battery):    
        self.route = route
        self.battery = battery
        self.engine = engine

    @abc.abstractmethod
    def on(self, locations):
        return

    @abc.abstractmethod
    def off(self):
        return
        
    @abc.abstractmethod
    def drive(self):
        return

    @classmethod
    def __subclasshook__(cls, C):
        if cls is abstractVehicle:
            if any("drive" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
    
    
class vehicle(abstractVehicle):
    
    def on(self):      
        self.engine.turnOn()     
            
    def off(self):
        self.engine.turnOff()          
   
    def drive(self):
        self.engine.setGear(6)        
        self.engine.setSpeed(100)
        driving = True
        while((self.route.getRoute().size()>0) & driving):   
            print("driving ", self.engine.status)
            'get distance, then drive it'     
            driving = self.engine.drive(self.route.getDistanceToNext())
            if driving:
                self.route.visited()
        self.off();                 
        
def main():   
    
    'pointcutAdvisor = RegexpMethodPointcutAdvisor(advice = [interceptor()], patterns = ["vehicle.on", "vehicle.off", "vehicle.visit"])'
    'v = ProxyFactoryObject(target = vehicle(), interceptors = [pointcutAdvisor])'
    
    startLocation = location().__slots__=(0,0)    
    locations = ArrayList()
    loc1 = location().__slots__=(-10,5)
    locations.add(loc1)
    loc2 = location().__slots__=(1,7)
    locations.add(loc2)
    loc3 = location().__slots__=(3,11)
    locations.add(loc3)
    loc4 = location().__slots__=(7,18)
    locations.add(loc4)
    loc5 = location().__slots__=(15,13)
    locations.add(loc5)
    loc6 = location().__slots__=(6,21)
    locations.add(loc6)
    loc7 = location().__slots__=(0,23)
    locations.add(loc7)
    loc8 = location().__slots__=(-4,29)
    locations.add(loc8)
    loc9 = location().__slots__=(-10,25)
    locations.add(loc9)
    loc11 = location().__slots__=(3,33)
    locations.add(loc11)
    loc12 = location().__slots__=(3,40)
    locations.add(loc12)
    loc13 = location().__slots__=(0,40)
    locations.add(loc13)
    
    b = battery()
    e = engine(b)
    r = route(locations, startLocation)  
    br = batteryRUM(b)
    rr = routeRUM(r)   
    rr.setBatteryRUM(br)
    br.setRouteRUM(rr)
    er = engineRUM(e)
    rr.setEngineRUM(er)
    v = vehicle(r, e, b)
    
    v.on()
    v.drive()
    v.off()
    print(b.energy)
    print(r.currentLocation)
    print(r.getRoute())
    
if __name__ == "__main__":
    main()          
