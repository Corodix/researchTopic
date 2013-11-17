import random
import vehicle
from vehicleRUM import EngineRUM 
from vehicleRUM import GearBoxRUM 
from vehicleRUM import VehicleRUM 

'world has a route network and weather'


class World():    
    
    def __init__(self, network):
        self.roadNetwork = network
        self.initWeather()
        
    def initWeather(self):
        self.weather = Weather()
        
    def addVehicle(self, vehicle, location):
        location.addVehicle(vehicle)
        
    def driveVehicleTo(self, vehicle, destination):     
        self.roadNetwork.driveTo(vehicle, destination)
        
    
class Weather():
    
    direction_front = 1
    direction_side = 2
    direction_back = 3
    max_strength = 5
            
    def __init__(self):
        'strength is wind strength'        
        self.strength = random.randrange(0, self.max_strength, 1)
        'direction is where the wind is coming from compared to the car, so front, back or side'
        self.direction = random.randrange(0,3,1)
        
        
    def getWeather(self):
        'determines the weather randomly.'
        '60% chance it has not changed in strength'
        '15% chance it has increased by one step, unless it is at the max strength, then it instead decreases in strength'
        '15% chance it has decreased by one step, unless it is at the minimum strength, then it instead increases in strength'
        '5% chance it has changed by 2 steps.'
        change = random.random()*100
        if ((change > 60) & (change <=75) & (self.strength<self.max_strength)) | ((change >75) & (change <=90) & (self.strength==0)):
            self.strength +=1
        elif ((change > 60) & (change <=75) & (self.strength==self.max_strength)) | ((change >75) & (change <=90) & (self.strength>0)):
            self.strength -=1
        elif ((change > 90) & (change <=95) & (self.strength<self.max_strength)) | ((change >95) & (change <=100) & (self.strength==0)):
            self.strength = min(self.strength+2, self.max_strength)
        elif change>90:
            self.strength = max(self.strength-2, 0)
            
        'direction is where the wind is coming from compared to the car, so front, back or side'
        '60% chance it does not change, 20% chance it changes to one of the other options'
        change = random.random()*100;
        if change>40:            
            self.direction = random.randrange(0,3, 1)  
            
        return self 
            
class RoadNetwork():
    
    def __init__(self, locations, roads):        
        self.locations = locations
        self.roads = roads    
        
    def driveTo(self, vehicle, destination):
        location = self.getLocationOf(vehicle)
        location.leaving(vehicle, destination)
    
    def getLocationOf(self, vehicle):
        for loc in self.locations:
            if vehicle in loc.vehicles:
                return loc
            
    def getLocation(self, name):
        for loc in self.locations:
            if loc.name == name:
                return loc
        
    def getRoutesFromTo(self, start, destination):
        routes = []
        for item in start.graph:            
            if item == destination:
                routes.append([destination])
            else:
                routes.extend(self.getRoutesFromToHelper(item, destination, [start]))
        return routes
    
    def getRoutesFromToHelper(self, start, destination, visited):
        routes = []  
        tempV = []
        tempV.extend(visited)
        tempV.append(start)        
        for item in start.graph:
            if item == destination:
                tR = [start, destination]        
                routes.append(tR)
            elif not visited.__contains__(item):
                tempRoutes = self.getRoutesFromToHelper(item, destination, tempV)   
                for r in tempRoutes:                    
                    tR = [start]                    
                    tR.extend(r)  
                    routes.append(tR)
        return routes
    
    
class Location():    
    
    def __init__(self, name):        
        self.name = name        
        self.vehicles = []
    
    def setRoads(self, roads):
        self.graph = {}
        for r in roads:
            self.graph.__setitem__(r.getOther(self), r)
    
    def offersRefuel(self):
        return False
    
    def addVehicle(self, vehicle):
        self.vehicles.append(vehicle)
        vehicle.routePlanner.updateCurrentLocation(self)
        
    def leaving(self, vehicle, destination):
        self.graph.get(destination).travelTo(destination, self.vehicles.pop(self.vehicles.index(vehicle)))        
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

class FuelStation(Location):
    
    def __init__(self, name):
        Location.__init__(self, name)
   
    def offersRefuel(self):
        return True
   
    def refuel(self, vehicle):
        vehicle.fuelTank.fill()
   
   
class Road():
    
    def __init__(self, locLeft, locRight, distance, minSpeed, maxSpeed, steepness):
        self.locLeft = locLeft
        self.locRight = locRight
        self.distance = distance
        self.minSpeed = minSpeed
        self.maxSpeed = maxSpeed
        'steepness should be considered going from left to right'
        'so if steepness is 15 degrees and you are going from left to right then you are going up and meeting resistance'
        'but if you are going from right to left then you are going downhill'
        self.steepness = steepness
    
    def getOther(self, location):
        if location == self.locLeft:
            return self.locRight
        else:
            return self.locLeft 
        
    def travelTo(self, location, vehicle):
        if location == self.locLeft:
            self.locLeft.addVehicle(vehicle)
        elif location == self.locRight:
            self.locRight.addVehicle(vehicle)
        
    def __str__(self):
        return self.locLeft.__str__()+"->"+self.locRight.__str__()
    
    def __repr__(self):
        return self.locLeft.__str__()+"->"+self.locRight.__str__()
   
   
def main():
    'create the locations of the network'
    l1 = Location("A")
    l2 = Location("B")
    l3 = Location("C")
    l4 = Location("D")
    l5 = Location("E")
    l6 = Location("F")
    l7 = Location("G")
    l8 = Location("H")
    l9 = Location("I")
    l10 = Location("J")
    l11 = Location("K")
    l12 = Location("L")
    f1 = FuelStation("M")
    f2 = FuelStation("N")
    
    'create the roads connecting these locations'
    r1 = Road(l1, l2, 20, 120, 180, 0)
    r2 = Road(l1, l3, 40, 40, 60, 0)    
    r3 = Road(l1, l4, 35, 30, 50, 0)    
    r4 = Road(l2, l3, 20, 60, 80, 0)
    r5 = Road(l2, l9, 18, 30, 45, 15)    
    r6 = Road(l3, l4, 35, 60, 80, 0)
    r7 = Road(l3, l10, 60, 100, 140, 0)    
    r8 = Road(l4, l5, 15, 50, 60, 0)    
    r9 = Road(l5, l6, 50, 50, 60, 10)
    r10 = Road(l5, l11, 53, 100, 140, 0)    
    r11 = Road(l6, l7, 12, 30, 50, 10)
    r12 = Road(l6, f2, 5, 60, 80, 5) 
    r13 = Road(l7, l8, 8, 30, 45, -12)
    r14 = Road(l8, l11, 10, 10, 30, -30)
    r15 = Road(l8, f2, 5, 60, 80, 5)
    r16 = Road(l9, l10, 12, 30, 40, -20)
    r17 = Road(l10, f1, 10, 60, 90, 0)
    r18 = Road(l11, f1, 20, 60, 90, 0)
    r19 = Road(l11, l12, 120, 120, 180, 0)    
    
    'add the roads to the locations, to they know which roads they have and which locations they border'
    l1.setRoads({r1, r2, r3})
    l2.setRoads({r1, r4, r5})
    l3.setRoads({r2, r4, r6, r7})
    l4.setRoads({r3, r6, r8})
    l5.setRoads({r8, r9, r10})
    l6.setRoads({r9, r11, r12})
    l7.setRoads({r11, r13})
    l8.setRoads({r13, r14, r15})
    l9.setRoads({r5, r16})
    l10.setRoads({r7, r16, r17})
    l11.setRoads({r10, r14, r18, r19})    
    l12.setRoads({r19})
    f1.setRoads({r17,r18})
    f2.setRoads({r12, r15})
    
    network = RoadNetwork([l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, f1, f2], [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19])
    
    world = World(network)    
    v = vehicle.Vehicle(world, [l5, l10, l12, l6])
    world.addVehicle(v, l1)    
    
    vehicleRUM = VehicleRUM(v, "efficient")
    v.drive()

if __name__ == "__main__":
    main()      
            