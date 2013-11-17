'Gearbox, Engine, FuelTank, RoutePlanner, Vehicle'

class Vehicle():
    
    def __init__(self, world, destinations):
        self.engine = Engine()
        self.gearbox = GearBox(6)
        self.fuelTank = FuelTank(100)
        self.world = world
        self.routePlanner = RoutePlanner(destinations, world)
        self.wheels = Wheels(2.09)
        
    def incThrottle(self, amount):
        self.engine.incThrottle(amount)
        
    def decThrottle(self, amount):
        self.engine.decThrottle(amount)
        
    def stop(self):
        self.engine.stop()
        
    def engineOn(self):
        self.engine.engineOn()
        
    def engineOff(self):
        self.engine.engineOff()
        
    def incGear(self):
        self.gearbox.incGear()
        
    def decGear(self):
        self.gearbox.decGear()
        
    def drive(self):
        while len(self.routePlanner.destinations)>0:            
            route = self.routePlanner.getRouteToNext()
            print(route)
            'call world to driveTo for each of the ?'
            for loc in route:
                self.world.driveTo(self, loc)
        
class GearBox():
    
    def __init__(self, maxGears):
        self.maxGears = maxGears
        self.gear = 1
        
    def incGear(self):
        self.gear = min(self.gear+1, self.maxGears)
        
    def decGear(self):
        self.gear = max(self.gear-1, 1)
        
class FuelTank():
    
    'contains liters of fuel'    
    def __init__(self, maxFuel):
        self.maxFuel = maxFuel
        self.fuelLevel = maxFuel
        
    def full(self):
        return self.fuelLevel==self.maxFuel

    def empty(self):
        return self.fuelLevel==0
    
    def refuel(self):
        self.fuelLevel = self.maxFuel
        
    def supplyFuel(self, amount):
        self.fuelLevel = min(self.fuelLevel-amount,0)
        
class Engine():
    
    def __init__(self):
        self.throttle = 0
        self.status = "off"
        
    def engineOn(self):
        self.status = "on"

    def engineOff(self):
        self.stop()
        self.status = "off"
        
    def incThrottle(self, amount):
        self.throttle = min(self.throttle+amount, 100)
        
    def decThrottle(self, amount):
        self.throttle = max(self.throttle-amount, 0)
        
    def stop(self):
        self.decThrottle(self.throttle)
        
class RoutePlanner():
    
    def __init__(self, destinations, world):
        self.destinations = destinations
        self.world = world
    
    def getRouteToNext(self):
        'find a route to the next destination'
        'this takes the route with the lowest amount of stops'
        print("a")
        print(self.currentLocation)
        print(self.destinations.__getitem__(0))
        routes = self.world.roadNetwork.getRoutesFromTo(self.currentLocation, self.destinations.__getitem__(0))
        print("b")
        route = self.getBestRoute(routes)
        print("c")
        return route
        
    def getBestRoute(self, routes):
        'simply pick the first route with the fewest amount of nodes in it'
        size = 999
        route = []
        for r in routes:
            if len(r) < size:
                size = len(r)
                route = r
        return route
        
    def updateCurrentLocation(self, location):
        self.currentLocation = location        
        if location in self.destinations:
            self.destinations.remove(location)
        
class Wheels():
    
    def __init__(self, circumference):
        'in m'
        self.circumference = circumference        
        
        