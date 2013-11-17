from abc import *
import itertools
from RUM import *

class VehicleRUM(RUM):

    'autopilot is the optimizer'
    'engine is an EngineRUM'
    'gearbox is a GearBoxRUM'

    def __init__(self, vehicle, drivingPolicy):
        RUM.__init__(self, vehicle)
        RUM.switchMethods(self, "drive", self.drive) 
        
        self.engineRUM = EngineRUM(vehicle.engine)
        self.gearboxRUM = GearBoxRUM(vehicle.gearbox)
        
        self.drivingPolicies = {"speed" : SpeedyDriver(vehicle.routePlanner),
                           "efficient" : EfficientDriver(vehicle.routePlanner)}       

        self.driver = self.drivingPolicies.get(drivingPolicy)
        self.driver.prepareARoute()
        
    def drive(self):
        self.driver.drive(self.component, self.engineRUM, self.gearboxRUM)
         
class EngineRUM(RUM):

    'change engine state depending on throttle and engineOff/engineOn'

    def __init__(self, engine):
        RUM.__init__(self, engine)
        self.stateChangeCatcherBeforeAndAfter("incThrottle", ["throttle"])
        self.stateChangeCatcherBeforeAndAfter("decThrottle", ["throttle"])
        self.stateChangeCatcherBeforeAndAfter("engineOn", [])
        self.stateChangeCatcherBeforeAndAfter("engineOff", [])
        self.addStates({"off" : EngineOffState(),
                        "stationary" : EngineStationaryState(),
                        "driving" : EngineDrivingState()})
        self.setInitialState("off")
        
        self.addTransition(Transition("off", "stationary", [Rule("methodName: == 'engineOn'")]))
        self.addTransition(Transition("stationary", "off", [Rule("methodName: == 'engineOff'")]))
        self.addTransition(Transition("driving", "off", [Rule("methodName: == 'engineOff'")]))
        self.addTransition(Transition("stationary", "driving", [Rule("old:throttle == 0"), Rule("new:throttle > 0")]))
        self.addTransition(Transition("driving", "stationary", [Rule("old:throttle > 0"), Rule("new:throttle == 0")]))
        
        'self.inc = RUM.switchMethods(self, "incThrottle", self.throttleIncrease)' 
        'self.dec = RUM.switchMethods(self, "decThrottle", self.throttleDecrease)'
        'self.on = RUM.switchMethods(self, "engineOn", self.engineOn)'
        'self.off = RUM.switchMethods(self, "engineOff", self.engineOff)'
        
    '''def throttleIncrease(self, amount):
        throttle = self.component.throttle
        self.inc(amount)
        if (self.component.throttle > 0) & (throttle == 0):
            self.state = self.states.get("driving")
        
    def throttleDecrease(self, amount):
        throttle = self.component.throttle
        self.dec(amount)
        if (throttle > 0) & (self.component.throttle==0):
            self.state = self.states.get("stationary")     
        
    def engineOn(self):
        self.on()
        if self.component.status == "on":
            if self.component.throttle==0:
                self.state = self.states.get("stationary")
            else:
                self.state = self.states.get("driving")
        
    def engineOff(self):
        self.off()
        if self.component.status == "off":
            self.state = self.states.get("off")'''

    def getFuelConsumptionPerSecond(self):
        return self.state.getFuelConsumption(self.component.throttle)
    
    def getRPM(self):
        'resistances like wind/steepness should be added to this as they affect RPM production?'
        return self.state.getRPM(self.component.throttle)
    
    def getRequiredThrottleForRPM(self, RPM):
        'use the driving state as the requestee clearly wants to drive if it is requesting what rpm it should use'
        return self.states.get("driving").getRequiredThrottleForRPM(RPM)


    
class GearBoxRUM(RUM):
    
    'change gear state whenever the car changes gear'
   
    def __init__(self, gearBox):
        RUM.__init__(self, gearBox)
        self.stateChangeCatcherBeforeAndAfter("incGear", ["gear"])
        self.stateChangeCatcherBeforeAndAfter("decGear", ["gear"])
        self.addStates({1 : GearBoxState(2.97, 10),
                        2 : GearBoxState(2.07, 17),
                        3 : GearBoxState(1.43, 25),
                        4 : GearBoxState(1, 37),
                        5 : GearBoxState(0.84, 44),
                        6 : GearBoxState(0.56, 65)})
        self.setInitialState(1)
        
        self.addTransition(Transition(1, 2, [Rule("old:gear == 1"), Rule("new:gear == 2")]))
        self.addTransition(Transition(2, 3, [Rule("old:gear == 2"), Rule("new:gear == 3")]))
        self.addTransition(Transition(3, 4, [Rule("old:gear == 3"), Rule("new:gear == 4")]))
        self.addTransition(Transition(4, 5, [Rule("old:gear == 4"), Rule("new:gear == 5")]))
        self.addTransition(Transition(5, 6, [Rule("old:gear == 5"), Rule("new:gear == 6")]))
        self.addTransition(Transition(6, 5, [Rule("old:gear == 6"), Rule("new:gear == 5")]))
        self.addTransition(Transition(5, 4, [Rule("old:gear == 5"), Rule("new:gear == 4")]))
        self.addTransition(Transition(4, 3, [Rule("old:gear == 4"), Rule("new:gear == 3")]))
        self.addTransition(Transition(3, 2, [Rule("old:gear == 3"), Rule("new:gear == 2")]))
        self.addTransition(Transition(2, 1, [Rule("old:gear == 2"), Rule("new:gear == 1")]))
        
        
    '''def gearIncrease(self):
        currentGear = self.component.currentGear
        self.inc()
        if currentGear != self.component.currentGear:
            self.gearChange()
            
    def gearDecrease(self):
        currentGear = self.component.currentGear
        self.dec()
        if currentGear != self.component.currentGear:
            self.gearChange()          
    
    def gearChange(self):
        self.gear = self.gears.get(self.component.currentGear)'''
        
    def getWheelRPM(self, RPM):
        return self.state.getWheelRPM(RPM)
    
    def getRequiredRPM(self, desiredWRPM):
        return self.state.getRequiredRPM(desiredWRPM)
    
    def getMinimumRequiredSpeed(self, gear):
        return self.states.get(gear).min_req_speed
    
    
class GearBoxState():    
    'the gearbox turns RPM from the engine into wheel rotations per minute (WRPM)'
    'gear ratio information was taken from: http://en.wikipedia.org/wiki/Gear_ratio'
    'thus the gear ratios are based on the 2004 Chevrolet Corvette C5 Z06'
    
    differentialRatio = 3.42

    def __init__(self, ratio, min_req_speed):
        self.ratio = ratio    
        self.min_req_speed = min_req_speed

    def getWheelRPM(self, RPM):
        'first translate the engine RPM produced into rotation per minute of the transmission'
        TRPM = RPM/self.ratio           
        'then translate the TRPM into rotations of the wheel per minute'
        WRPM = TRPM/self.differentialRatio
        return WRPM   
    
    def getRequiredRPM(self, desiredWRPM):
        return desiredWRPM*self.differentialRatio*self.ratio

class EngineState():    
    __metaclass__ = ABCMeta
    
    'the engine turns fuel into RPM (rotations per minute)'
    
    def __init__(self):
        return 'yes, totally redundant method here'
    
    @abc.abstractmethod
    def getFuelConsumption(self, throttle):
        return
    
    'resistance should be added to this as it reduces engine RPM'
    @abc.abstractmethod
    def getRPM(self, throttle):
        return
    
    'returns the throttle required to reach the desired amount of RPM'
    @abc.abstractmethod
    def getRequiredThrottleForRPM(self, RPM):
        return 0

class EngineOffState(EngineState):    
    
    'RPM = 0'
    'fuel = 0'
    
    def __init__(self):
        EngineState.__init__(self)
    
    def getFuelConsumption(self, throttle):
        return 0
    
    def getRPM(self, throttle):
        return 0
    
    def getRequiredThrottleForRPM(self, RPM):
        return 0

class EngineStationaryState(EngineState):
    
    'RPM = 900'
    'fuel = 1.0/3600.0'
    
    def __init__(self):
        EngineState.__init__(self)
    
    def getFuelConsumption(self, throttle):
        return 1.0/3600.0
    
    def getRPM(self, throttle):
        return 900
    
    def getRequiredThrottleForRPM(self, RPM):
        return 0

class EngineDrivingState(EngineState):
      
    'RPM>900, RPM<=4000'
    'Fuel>1.0/3600.0, Fuel <=20.0/3600.0'

    def __init__(self):
        EngineState.__init__(self)

    def getFuelConsumption(self, throttle):
        'assuming linear relation between throttle and fuel consumption'
        return (throttle/(100.0/19.0)+1)/3600.0

    def getRPM(self, throttle):
        'assuming linear relation between throttle and rpm (for now)'
        return throttle/(100.0/3100.0)+900
    
    def getRequiredThrottleForRPM(self, RPM):
        return (RPM-900)*(100.0/3100.0)



    

class Driver():    
    __metaclass__ = ABCMeta
    
    def __init__(self, routePlanner):
        self.routePlanner = routePlanner
        self.fuelConsumed = 0
        self.timeElapsed = 0
        
    @abc.abstractmethod
    def prepareARoute(self):
        return
    
    @abc.abstractmethod
    def drive(self, vehicle, engineRUM, gearboxRUM):
        return
    
    def switchToGear(self, desiredGear, vehicle):
        currentGear = vehicle.gearbox.gear
        while(currentGear > desiredGear):
            vehicle.decGear()
            currentGear = vehicle.gearbox.gear
        while(currentGear < desiredGear):
            vehicle.incGear()
            currentGear = vehicle.gearbox.gear
            
    def switchThrottleTo(self, desiredThrottle, vehicle):
        currentThrottle = vehicle.engine.throttle
        if(currentThrottle > desiredThrottle):
            vehicle.decThrottle(currentThrottle-desiredThrottle)
        elif(currentThrottle < desiredThrottle):
            vehicle.incThrottle(desiredThrottle-currentThrottle)
            
    def determineOptimalGear(self, desiredSpeed, gearboxRUM):
        'go for the highest possible gear'
        optimalGear = 1
        if desiredSpeed > gearboxRUM.getMinimumRequiredSpeed(6):
            optimalGear = 6
        elif desiredSpeed > gearboxRUM.getMinimumRequiredSpeed(5):
            optimalGear = 5
        elif desiredSpeed > gearboxRUM.getMinimumRequiredSpeed(4):
            optimalGear = 4
        elif desiredSpeed > gearboxRUM.getMinimumRequiredSpeed(3):
            optimalGear = 3
        elif desiredSpeed > gearboxRUM.getMinimumRequiredSpeed(2):
            optimalGear = 2
        return optimalGear  
        
    def determineRequiredThrottle(self, vehicle, desiredspeed, engineRUM, gearboxRUM):
        desiredRPM = self.determineRequiredRPM(vehicle, desiredspeed, gearboxRUM)
        return engineRUM.getRequiredThrottleForRPM(desiredRPM)
            
    def determineRequiredRPM(self, vehicle, desiredSpeed, gearboxRUM):
        reqWheelRPM = desiredSpeed*1000/60/vehicle.wheels.circumference
        return gearboxRUM.getRequiredRPM(reqWheelRPM)       
            
    def getResistances(self, routePlanner, road):
        weather = self.routePlanner.world.weather.getWeather()
        resistance = road.steepness
        if weather.direction == weather.direction_front:
            resistance += pow(weather.strength,2)
        elif weather.direction == weather.direction_side:
            resistance += weather.strength
        else:
            resistance -= pow(weather.strength, 1.5)
        return 1+resistance/100
    
    def getFuelCost(self, speed, road, weather, engineRUM, gearboxRUM, vehicle):
        timeElapsed = (road.distance*1000)/speed        
        resistance = road.steepness
        if weather.direction == weather.direction_front:
            resistance += pow(weather.strength,2)
        elif weather.direction == weather.direction_side:
            resistance += weather.strength
        else:
            resistance -= pow(weather.strength, 1.5)
        resistance = 1+resistance/100        
        
        resistance = self.getResistances(self.routePlanner, road)
        'determine fuel consumption at this speed, highest gear is best'
        prefGear = self.determineOptimalGear(speed, gearboxRUM)
        'now set gear to this, make backup of gearboxRum so changes can be reverted later!'
        gearboxState = getattr(gearboxRUM, 'state')
        gearboxStates = getattr(gearboxRUM, 'states')
        gearboxChanged = False
        if(gearboxState != gearboxStates.get(prefGear)):
            gearboxChanged = True
            setattr(gearboxRUM, 'state', gearboxStates.get(prefGear))
        
        prefThrottle = self.determineRequiredThrottle(vehicle, speed, engineRUM, gearboxRUM)*resistance
        'set throttle to this, make backup of engineRUMs throttle setting so changes can be reverted later!'
        throttle = getattr(engineRUM.component, 'throttle')
        engineThrottleChanged = False
        if(throttle != prefThrottle):
            engineThrottleChanged = True
            setattr(engineRUM.component, 'throttle', prefThrottle)        
        
        fuelConsumed = (engineRUM.getFuelConsumptionPerSecond()*timeElapsed)
        
        'return engine and gearbox rums to their proper states'
        if gearboxChanged:
            setattr(gearboxRUM, 'state', gearboxState)
        if engineThrottleChanged:
            setattr(engineRUM.component, 'throttle', throttle)

        return fuelConsumed
    
    def getDistance(self, route, start):
        distance = 0
        current = start
        for node in route:
            while(current != node):
                road = current.graph.get(node)
                distance += road.distance
                if(road.getOther(current) == node):                
                    current = node
                else:
                    current = road.getOther(current)
        return distance   
    
    def getTime(self, route, start):
        time = 0
        current = start
        for node in route:
            while(current != node):
                road = current.graph.get(node)
                time += road.distance/road.maxSpeed
                if(road.getOther(current) == node):                
                    current = node
                else:
                    current = road.getOther(current)
        return time
    
    
    
class SpeedyDriver(Driver):
    'gets to his destinations as fast as possible'
    'thus highest gear and as much throttle as can be used without going over max speed'
    def __init__(self, routePlanner):
        Driver.__init__(self, routePlanner)
        
    def prepareARoute(self):
        'add information to all locations about which way to go to get somewhere else the fastest'
        'then determine the fastest route that can be used by the car and set the destinations in the correct order'
        network = self.routePlanner.world.roadNetwork
        locations = network.locations
        graphs = {}
        for node in locations:
            graph = {}
            for destination in locations:
                if node != destination:
                    graph[destination] = self.selectFastestRoad(network.getRoutesFromTo(node, destination), node)
            graphs[node] = graph    
            
        for node in locations:
            node.graph = graphs.get(node)            
        
        'the locations now all have routing information, traversing the graph is now much easier'
        'now we just need to determine the fastest way to visit all the destinations'
        'TODO!'                  
        self.orderDestinations()     
        
    def orderDestinations(self):
        destinations = self.routePlanner.destinations 
        orders = []
        orders.extend(itertools.permutations(destinations, len(destinations)))         
        routeTuple = self.selectFastestRoute(orders , self.routePlanner.currentLocation)
        route = []
        for i in routeTuple:
            route.append(i)            
        self.routePlanner.destinations = route
    
    def selectFastestRoute(self, routes, start):
        time = -1
        for route in routes:
            t = self.getTime(route, start)
            if (t<time) | (time == -1):
                result = route
                time = t
        return result
    
    def selectFastestRoad(self, routes, start):
        'from all these routes, select the fastest route and then return the first road that belongs to it'
        route = routes[0]
        time = self.getTime(route, start)
        for r in routes:
            t = self.getTime(r, start)
            if t < time:
                time = t
                route = r
        return start.graph.get(route[0])
        
    def drive(self, vehicle, engineRUM, gearboxRUM):
        vehicle.engineOn()          
        while len(self.routePlanner.destinations)>0: 
            destination = self.routePlanner.destinations[0]
            while self.routePlanner.currentLocation != destination:
                'TODO: should incorporate a stillGoodRoute check, to confirm that we wont go out of fuel before reaching a fuel station'
                
                
                road = self.routePlanner.currentLocation.graph.get(destination)       
                'the speed this driver desires'         
                maxAllowedSpeed = road.maxSpeed
                'calculate the resistance'
                resistance = self.getResistances(self.routePlanner, road)
                'determine the gear that should be used, adjust it to that'                
                self.switchToGear(self.determineOptimalGear(maxAllowedSpeed, gearboxRUM), vehicle)
                'determine required RPM and adjust throttle to reach it'
                self.switchThrottleTo(self.determineRequiredThrottle(vehicle, maxAllowedSpeed, engineRUM, gearboxRUM), vehicle)
                'finally determine our current speed in m/s and then drive over this road'
                speed = gearboxRUM.getWheelRPM(engineRUM.getRPM()/resistance)*vehicle.wheels.circumference/60
                self.routePlanner.world.driveVehicleTo(vehicle, road.getOther(self.routePlanner.currentLocation))
                
                'adjust elapsted time and fuel'
                distance = road.distance
                if(speed==0):
                    speed = 1
                timeElapsed = (distance*1000)/speed
                fuelConsumed = (engineRUM.getFuelConsumptionPerSecond()*timeElapsed)
                
                print("driven "+distance.__str__()+" km at speed "+speed.__str__()+" m/s. time elapsed: "+timeElapsed.__str__()+" second. fuel consumed: "+fuelConsumed.__str__())
                
                vehicle.fuelTank.supplyFuel(fuelConsumed)
                self.fuelConsumed += fuelConsumed
                self.timeElapsed += timeElapsed
        vehicle.engineOff()
        print("fuel consumed: "+self.fuelConsumed.__str__())
        print("time elapsed:" +self.timeElapsed.__str__())
        

class EfficientDriver(Driver):
    'gets to his destinations using as little fuel as possible'
    'highest possible gear with lowest possible RPM, without going below minimum speed'
    def __init__(self, routePlanner):
        Driver.__init__(self, routePlanner)

    def prepareARoute(self):
        'add information to all locations about which way to go to get somewhere else the fastest'
        'then determine the fastest route that can be used by the car and set the destinations in the correct order'
        network = self.routePlanner.world.roadNetwork
        locations = network.locations
        graphs = {}
        for node in locations:
            graph = {}
            for destination in locations:
                if node != destination:
                    graph[destination] = self.selectShortestRoad(network.getRoutesFromTo(node, destination), node)
            graphs[node] = graph    
            
        for node in locations:
            node.graph = graphs.get(node)            
        
        'the locations now all have routing information, traversing the graph is now much easier'
        'now we just need to determine the fastest way to visit all the destinations'
        'TODO!'                  
        self.orderDestinations()
    
    def orderDestinations(self):
        destinations = self.routePlanner.destinations 
        orders = []
        orders.extend(itertools.permutations(destinations, len(destinations)))         
        routeTuple = self.selectShortestRoute(orders , self.routePlanner.currentLocation)
        route = []
        for i in routeTuple:
            route.append(i)            
        self.routePlanner.destinations = route
    
    def selectShortestRoute(self, routes, start):
        distance = -1
        for route in routes:
            d = self.getDistance(route, start)
            if (d<distance) | (distance == -1):
                result = route
                distance = d
        return result    

    def selectShortestRoad(self, routes, start):
        'from all these routes, select the fastest route and then return the first road that belongs to it'
        route = routes[0]
        distance = self.getDistance(route, start)
        for r in routes:
            d = self.getDistance(r, start)
            if d < distance:
                distance = d
                route = r
        return start.graph.get(route[0])

    def preferredSpeed(self, minS, midS, maxS, road, weather, engineRUM, gearboxRUM, vehicle):
        minF = self.getFuelCost(minS, road, weather, engineRUM, gearboxRUM, vehicle)
        midF = self.getFuelCost(midS, road, weather, engineRUM, gearboxRUM, vehicle)
        maxF = self.getFuelCost(maxS, road, weather, engineRUM, gearboxRUM, vehicle)
        if minF < maxF:
            if (midS > minS+1) & (midS != minS):
                result = self.preferredSpeed(minS, (minS+midS)/2, midS, road, weather, engineRUM, gearboxRUM, vehicle)
            elif minF < midF:
                result = minS
            else:
                result = midS
        elif (midS < maxS-1) & (midS != maxS):
            result = self.preferredSpeed(midS, (midS+maxS)/2, maxS, road, weather, engineRUM, gearboxRUM, vehicle)
        elif maxF < midF:
            result = maxS
        else:
            result = midS      
        return result    
    
    'TODO, is far from efficient at the moment, needs to be better able to determine the speed it needs'    
    def drive(self, vehicle, engineRUM, gearboxRUM):
        vehicle.engineOn()
        while len(self.routePlanner.destinations)>0:
            destination = self.routePlanner.destinations[0]
            while self.routePlanner.currentLocation != destination:    
                'TODO: should incorporate a stillGoodRoute check, to confirm that we wont go out of fuel before reaching a fuel station'                
                road = self.routePlanner.currentLocation.graph.get(destination)       
                'the speed this driver desires'  
                preferredSpeed = self.preferredSpeed(road.minSpeed, (road.minSpeed+road.maxSpeed)/2 ,road.maxSpeed, road, self.routePlanner.world.weather, engineRUM, gearboxRUM, vehicle)   

                'calculate the resistance'
                resistance = self.getResistances(self.routePlanner, road)
                'determine the gear that should be used, adjust it to that'                
                self.switchToGear(self.determineOptimalGear(preferredSpeed, gearboxRUM), vehicle)
                'determine required RPM and adjust throttle to reach it'
                self.switchThrottleTo(self.determineRequiredThrottle(vehicle, preferredSpeed, engineRUM, gearboxRUM)*resistance, vehicle)
                'finally determine our current speed in m/s and then drive over this road'
                speed = gearboxRUM.getWheelRPM(engineRUM.getRPM())*vehicle.wheels.circumference/60
                self.routePlanner.world.driveVehicleTo(vehicle, road.getOther(self.routePlanner.currentLocation))
                
                'adjust elapsted time and fuel'
                distance = road.distance
                if(speed==0):
                    speed = 1
                timeElapsed = (distance*1000)/speed
                fuelConsumed = (engineRUM.getFuelConsumptionPerSecond()*timeElapsed)
                
                print("driven "+distance.__str__()+" km at speed "+speed.__str__()+" m/s. time elapsed: "+timeElapsed.__str__()+" second. fuel consumed: "+fuelConsumed.__str__())
                
                vehicle.fuelTank.supplyFuel(fuelConsumed)
                self.fuelConsumed += fuelConsumed
                self.timeElapsed += timeElapsed                   
               
        vehicle.engineOff()
        print("fuel consumed: "+self.fuelConsumed.__str__())
        print("time elapsed:" +self.timeElapsed.__str__())   
        
        
        
        