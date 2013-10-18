import abc
from abc import ABCMeta
import java.util.ArrayList as ArrayList
import random
import math
from springpython.context import ApplicationContext
from springpython.config import XMLConfig
from springpython.aop import *
from vehicleRUM import *

class location():
    __slots__ = ('x', 'y')       

class abstractVehicle():
    __metaclass__ = ABCMeta
    energy_full = 30.00    
    startLocation = location().__slots__=(0,0) 
    margin = 1.0
    threshold = 20

    @abc.abstractmethod
    def on(self):
        return

    @abc.abstractmethod
    def off(self):
        return
    
    @abc.abstractmethod
    def recharge(self):
        return
    
    @abc.abstractmethod
    def visit(self, locations):
        return

    @classmethod
    def __subclasshook__(cls, C):
        if cls is abstractVehicle:
            if any("visit" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
    
class vehicle(abstractVehicle):
    
    def __init__(self):
        self.energy = self.energy_full
        self.charger = self.startLocation
        self.currentLocation = self.startLocation
        self.active = False
    
    def on(self):        
        self.energy-=0.1
        if self.energy>0:
            self.active = True           
            
    def off(self):
        self.active = False  
         
    def recharge(self):
        if self.sameLocation(self.charger, self.currentLocation):
            self.energy = self.energy_full
        'else throw not at location of a charger exception?'
     
    def visit(self):
        closest = self.getClosest(self.locsToBeVisited)
        disToClosest = self.getDistance(self.currentLocation, closest)
        disToCharger = self.getDistance(self.currentLocation, self.charger)
        disFromClosestToCharger = self.getDistance(closest, self.charger)
        if self.energy < self.threshold:
            'return to recharge, energy to low' 
            cost = random.randrange(100, 120, 1)*disToCharger/100
            if cost>self.energy:
                'vehicle stranded without energy, TODO update location'
                self.energy=0
            else:
                'arrived at charger, recharge energy and continue visiting locations'
                self.energy-=cost
                self.currentLocation = self.charger
                self.recharge()
                self.visit()
        else:
            if ((disToClosest+disFromClosestToCharger)*self.margin) < self.energy:
                cost = random.randrange(100, 120, 1)*disToClosest/100
                if cost>self.energy:
                    'vehicle stranded without energy, TODO update location'
                    self.energy=0
                else:
                    'enough energy to get to the location'
                    self.energy-=cost
                    self.currentLocation = closest            
                    'remove closest location from list of locations, since it has now been visited'
                    self.locsToBeVisited.remove(closest)
                    'if another location exists in the list, go to it, goto charger if not already there' 
                    if (self.locsToBeVisited.size()==0): 
                        if self.sameLocation(self.currentLocation, self.charger):
                            return
                        else:
                            self.locsToBeVisited.add(self.charger)
                            self.visit()
                    else:
                        self.visit()
            else:
                if disToCharger < self.energy:
                    'actual cost to get to the charger, might be slightly off from optimal due to obstacles'
                    cost = random.randrange(100, 120, 1)*disToCharger/100
                    if cost>self.energy:
                        'vehicle stranded without energy, TODO update location'
                        self.energy=0
                    else:
                        'arrived at charger, recharge energy and continue visiting locations'
                        self.energy-=cost
                        self.currentLocation = self.charger
                        self.recharge()
                        self.visit()     
    
    def getClosest(self, locations):
        first = True
        for location in locations:
            if first:
                closest = location
                first = False
            else:
                if self.getDistance(self.currentLocation, location) < self.getDistance(self.currentLocation, closest) :
                    closest = location;
        return closest    
                
    def sameLocation(self, loc1, loc2):
        return loc1[0] == loc2[0] & loc1[1] == loc2[1]
        
    def getDistance(self, origin, destination):   
        return math.sqrt(math.pow(math.fabs(origin[0]-destination[0]),2.0)+math.pow(math.fabs(origin[1]-destination[1]), 2.0))
    
    def toBeVisited(self, locations):
        self.locsToBeVisited = locations
        
def main():   
    
    pointcutAdvisor = RegexpMethodPointcutAdvisor(advice = [interceptor()], patterns = ["vehicle.on", "vehicle.off", "vehicle.visit"])
    v = ProxyFactoryObject(target = vehicle(), interceptors = [pointcutAdvisor])
    
    locations = ArrayList()
    'TODO, randomly generate some locations without adding duplicates'
    loc1 = location().__slots__=(1,3)
    locations.add(loc1)
    loc2 = location().__slots__=(2,5)
    locations.add(loc2)
    loc3 = location().__slots__=(3,7)
    locations.add(loc3)
    loc4 = location().__slots__=(3,8)
    locations.add(loc4)
    loc5 = location().__slots__=(9,1)
    locations.add(loc5)
    loc6 = location().__slots__=(9,9)
    locations.add(loc6)
    loc7 = location().__slots__=(5,5)
    locations.add(loc7)
    loc8 = location().__slots__=(1,1)
    locations.add(loc8)
    loc9 = location().__slots__=(0,9)
    locations.add(loc9)
    loc10 = location().__slots__=(4,2)
    locations.add(loc10)
    
    
    v.toBeVisited(locations)
    v.on()
    v.visit()
    v.off()
    print(v.energy)
    print(v.currentLocation)
    print(v.active)
    print(v.locsToBeVisited)
    
if __name__ == "__main__":
    main()          
