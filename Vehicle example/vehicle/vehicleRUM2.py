from vehicle import *
from abc import ABCMeta

class RUM():
    __metaclass__ = ABCMeta
    
    def optimizer(self):
        return
    
    def switchTo(self, nextState):
        return

'-------Battery RUM & states -------'
    
class batteryRUM(RUM):    
    
    def __init__(self, source):
        self.consume = getattr(source, "consume")
        setattr(source, "consume", self.monitor) 
        self.source = source
        self.fullState = batteryAlmostFullState()
        self.quarterEmptyState = batteryQuarterEmptyState()
        self.halfEmptyState = batteryHalfEmptyState()
        self.almostEmptyState = batteryAlmostEmptyState()
        self.emptyState = batteryEmptyState()
        
        if self.source.energy==source.energy_full:
            self.currentState = self.fullState
            self.nextState = self.quarterEmptyState
        elif self.source.energy>=(self.source.energy_full/4.0*3.0):
            self.currentState = self.quarterEmptyState
            self.nextState = self.halfEmptyState
        elif self.source.energy>=(self.source.energy_full/2.0):
            self.currentState = self.halfEmptyState
            self.nextState = self.almostEmptyState            
        elif self.source.energy>=(self.source.energy_full/4.0):
            self.currentState = self.almostEmptyState
            self.nextState = self.emptyState 
        else:
            self.currentState = self.emptyState 
            self.nextState = self.emptyState        
    
    def switchTo(self, nextState):        
        self.currentState = nextState
        if nextState == self.quarterEmptyState:
            self.nextState = self.halfEmptyState
        elif nextState == self.halfEmptyState:
            self.nextState = self.almostEmptyState
        else:
            self.nextState = self.emptyState  
        print(self.currentState)      
    
    def monitor(self, amount):
        self.consume(amount)
        self.currentState.energy = self.source.energy
        if self.source.energy<self.currentState.energyMin:
            self.switchTo(self.nextState)
        return
    
    def getEnergy(self):
        return self.currentState.energy    
    
    def setRouteRUM(self, routeRUM):
        self.routeRUM = routeRUM
        
    def setEngineRUM(self, engineRUM):
        self.engineRUM = engineRUM
    
    def optimizer(self):
        routeProgress = self.routeRUM.currentState        
        
        if (self.currentState == self.quarterEmptyState) & (routeProgress != self.routeRUM.quarterCompletedState):                
            'optimizations possible, let route optimizer handle it'
            self.routeRUM.optimizer()
        elif (self.currentState  == self.halfEmptyState) & (routeProgress != self.routeRUM.halfCompletedState):
            'optimizations possible, let route optimizer handle it'
            self.routeRUM.optimizer()
        elif (self.currentState  == self.almostEmptyState) & (routeProgress != self.batteryRUM.threeQuarterCompletedState):
            'optimizations possible, let route optimizer handle it'
            self.routeRUM.optimizer()
        else:
            return 

class batteryState():
    __metaclass__ = ABCMeta
     
    def __init__(self, energy, maxEnergy, minEnergy):
        self.energy = energy
        self.energyMax = maxEnergy
        self.energyMin = minEnergy

class batteryAlmostFullState(batteryState):
    
    def __init__(self):
        batteryState.__init__(self, 100.0, 100.0, 75.0)
        
class batteryQuarterEmptyState(batteryState):
    
    def __init__(self):
        batteryState.__init__(self, 75.0, 75.0, 50.0)

class batteryHalfEmptyState(batteryState):

    def __init__(self):
        batteryState.__init__(self, 50.0, 50.0, 25.0)

    
class batteryAlmostEmptyState(batteryState):

    def __init__(self):
        batteryState.__init__(self, 25.0, 25.0, 0.0)

class batteryEmptyState(batteryState):

    def __init__(self):
        batteryState.__init__(self, 0.0, 0.0, 0.0)
    

'-------Route RUM & states -------'

class routeRUM(RUM):    
    
    def __init__(self, source):
        self.visited = getattr(source, "visited")
        setattr(source, "visited", self.monitor) 
        self.source = source
        
        'init states'
        visits = self.source.getRoute().size()
        distance = self.source.getRemainingDistance()
        
        self.totallyUncompletedState = routeAlmostTotallyUncompletedState(distance, visits)
        self.quarterCompletedState = routeQuarterCompletedState(distance, visits)
        self.halfCompletedState = routeHalfCompletedState(distance, visits)
        self.threeQuarterCompletedState = routeThreeQuarterCompletedState(distance, visits)
        self.routeCompletedState = routeCompletedState(distance, visits)
        'set current and next state'
        self.currentState = self.totallyUncompletedState 
        self.nextState = self.quarterCompletedState    
     
    
    def switchTo(self, nextState):      
        nextState.remDistance = self.currentState.remDistance
        nextState.remVisits = self.currentState.remVisits  
        self.currentState = nextState
        
        if nextState == self.quarterCompletedState:
            self.nextState = self.halfCompletedState
        elif nextState == self.halfCompletedState:
            self.nextState = self.threeQuarterCompletedState
        elif nextState == self.threeQuarterCompletedState:
            self.nextState = self.routeCompletedState
        else:
            self.nextState = self.routeCompletedState 
        print(self.currentState, self.currentState.remVisits, self.currentState.remDistance)
    
    def monitor(self):
        self.visited()
        self.currentState.remDistance = self.source.getRemainingDistance()
        self.currentState.remVisits = self.source.getRoute().size()
        if self.currentState.remVisits<=self.currentState.minRemVisits:
            self.switchTo(self.nextState)
            self.optimizer()
        return
    
        
    def setBatteryRUM(self, batteryRUM):
        self.batteryRUM = batteryRUM
        
    def setEngineRUM(self, engineRUM):
        self.engineRUM = engineRUM
    
    def optimizer(self):
        'check with batteryRUM how much of the battery is remaining, compare to route remaining'
        'if % route remaining far more than % energy remaining, optimize for effiency'
        'if % energy remaining far more than % route remaining, optimize for speed (but not to much,'
        'as it is looking at the amount of stops, not the actual distance (TODO, change this?)'
        
        batteryLevel = self.batteryRUM.currentState        
        
        if self.currentState == self.quarterCompletedState:
            if batteryLevel == self.batteryRUM.fullState:
                self.optimizeSpeed()
            elif batteryLevel != self.batteryRUM.quarterEmptyState:    
                self.optimizeEfficiency() 
        elif self.currentState  == self.halfCompletedState:
            if (batteryLevel == self.batteryRUM.fullState) | (batteryLevel == self.batteryRUM.quarterEmptyState):
                self.optimizeSpeed()
            elif batteryLevel != self.batteryRUM.halfEmptyState:
                self.optimizeEfficiency() 
        elif self.currentState  == self.threeQuarterCompletedState:
            if (batteryLevel == self.batteryRUM.fullState) | (batteryLevel == self.batteryRUM.quarterEmptyState) | (batteryLevel == self.batteryRUM.almostEmptyState):
                self.optimizeSpeed()
            elif batteryLevel != self.batteryRUM.halfEmptyState:
                self.optimizeEfficiency() 
        else:
            return 

    
    def optimizeSpeed(self):
        'sacrifice fuel efficiency for speed'
        self.engineRUM.optimizeSpeed()
    
    def optimizeEfficiency(self):
        'optimize route for distance if possible, else'
        'sacrifice speed for fuel efficiency'
        self.engineRUM.optimizeEfficiency()


class routeState():
    __metaclass__ = ABCMeta
    def __init__(self, remDistance, remVisits, maxRemVisits, minRemVisits):
        self.remDistance = remDistance
        self.remVisits = remVisits
        self.maxRemVisits = maxRemVisits
        self.minRemVisits = minRemVisits

class routeAlmostTotallyUncompletedState(routeState):
    
    def __init__(self, distance, visits):
        routeState.__init__(self, distance, visits, 100.0, visits/4*3)

class routeQuarterCompletedState(routeState):

    def __init__(self, distance, visits):
        routeState.__init__(self, distance, visits/4*3, visits/4*3, visits/4*2)
    
class routeHalfCompletedState(routeState):

    def __init__(self, distance, visits):
        routeState.__init__(self, distance, visits/4*2, visits/4*2, visits/4)

class routeThreeQuarterCompletedState(routeState):

    def __init__(self, distance, visits):
        routeState.__init__(self, distance, visits/4, visits/4, 0)

class routeCompletedState(routeState):
    def __init__(self, distance, visits):
        routeState.__init__(self, 0.0, 0, 0, 0)
    
 
    
'-------Engine RUM & states -------'

class engineRUM(RUM):

    def __init__(self, source):
        self.setGear = getattr(source, "setGear")
        setattr(source, "setGear", self.monitorGear) 
        self.setSpeed = getattr(source, "setSpeed")
        setattr(source, "setSpeed", self.monitorSpeed)
        self.turnOff = getattr(source, "turnOff")
        setattr(source, "turnOff", self.monitorOff)  
        self.turnOn = getattr(source, "turnOn")
        setattr(source, "turnOn", self.monitorOn)  
        self.source = source
        
        'init states'
        speed = self.source.speed
        self.optimizedThrottle = -1
        
        self.offState = engineOffState()
        self.idleState = engineIdleState()
        self.drivingFirstGearState = engineFirstGearState(speed)
        self.drivingSecondGearState = engineSecondGearState(speed)
        self.drivingThirdGearState = engineThirdGearState(speed)
        self.drivingFourthGearState = engineFourthGearState(speed)
        self.drivingFifthGearState = engineFifthGearState(speed)
        self.drivingSixthGearState = engineSixthGearState(speed)
        
        'set current state'
        self.currentState = self.offState
    
    def switchTo(self, nextState): 
        nextState.speed = self.currentState.speed
        self.currentState = nextState   
        print(self.currentState)  
    
    def monitorGear(self, gear):
        self.setGear(gear)        
        if gear != self.currentState.gear:
            if gear==1:
                self.switchTo(self.drivingFirstGearState)        
            elif gear==2:
                self.switchTo(self.drivingSecondGearState)
            elif gear==3:
                self.switchTo(self.drivingThirdGearState)
            elif gear==4:
                self.switchTo(self.drivingFourthGearState)
            elif gear==5:
                self.switchTo(self.drivingFifthGearState)
            elif gear==6:
                self.switchTo(self.drivingSixthGearState)      
 
    def monitorSpeed(self, throttle): 
        self.setSpeed(throttle)    
        self.currentState.speed = self.source.speed
   
    def monitorOn(self):     
        self.turnOn() 
        self.switchTo(self.idleState)
    
    def monitorOff(self):
        self.turnOff()
        self.switchTo(self.offState)
        
    def setBatteryRUM(self, batteryRUM):
        self.batteryRUM = batteryRUM
        
    def setRouteRUM(self, engineRUM):
        self.engineRUM = engineRUM
    
    def optimizeSpeed(self):
        'sacrifice fuel efficiency for speed'        
        'if already at max gear, increase speed to max'
        if self.currentState == self.drivingSixthGearState:
            self.setSpeed(100)
        else:
            consumption = self.currentState.getConsumption()
            if(consumption<10):
                self.monitorGear(6)
                self.monitorSpeed(40)
            else:                
                'else move to max gear, increase speed so that consumption is slightly (10%) up' 
                self.monitorSpeed((consumption-10)*11+40)               
    
    def optimizeEfficiency(self):
        'sacrifice speed for fuel efficiency'
        'if at optimal speed, move to minimum speed'
        if self.currentState.speed<=self.currentState.optimalSpeed:
            self.monitorSpeed(20)
        else:     
            'if above optimal speed, move to gear 6 and optimal speed'
            self.monitorGear(6)
            self.monitorSpeed(40)
        print("optimize Efficiency",self.source.gear, self.source.speed)
            
class engineState():
    __metaclass__ = ABCMeta
    def __init__(self, gear, speed, maxSpeed, minSpeed, optimalSpeed):
        self.gear = gear
        self.speed = speed
        self.maxSpeed = maxSpeed
        self.minSpeed = minSpeed
        self.optimalSpeed = optimalSpeed

class engineOffState(engineState):
    
    def __init__(self):
        engineState.__init__(self, 0, 0, 0, 0, 0)
        
    def getConsumption(self):
        return 0

class engineIdleState(engineState):
    
    def __init__(self):
        engineState.__init__(self, 1, 0, 0, 0, 0)
        
    def getConsumption(self):
        return 0.01

class engineFirstGearState(engineState):
    
    def __init__(self, speed):
        engineState.__init__(self, 1, speed, 8, 16, 10)
        
    def getConsumption(self):
        if self.speed<10:   
            return ((self.speed-10)/10.0/0.1*5+100)*10/100
        else:
            return ((self.speed-10)/10.0/0.1*15+100)*10/100
        
class engineSecondGearState(engineState):
    
    def __init__(self, speed):
        engineState.__init__(self, 2, speed, 16, 32, 20)
        
    def getConsumption(self):
        if self.speed<20:   
            return ((self.speed-20)/20.0/0.1*5+100)*10/100
        else:
            return ((self.speed-20)/20.0/0.1*15+100)*10/100
        
class engineThirdGearState(engineState):
    
    def __init__(self, speed):
        engineState.__init__(self, 3, speed, 28, 56, 35)
        
    def getConsumption(self):
        if self.speed<35:   
            return ((self.speed-35)/35.0/0.1*5+100)*10/100
        else:
            return ((self.speed-35)/35.0/0.1*15+100)*10/100
        
class engineFourthGearState(engineState):
    
    def __init__(self, speed):
        engineState.__init__(self, 4, speed, 36, 72, 45)
        
    def getConsumption(self):
        if self.speed<45:   
            return ((self.speed-45)/45.0/0.1*5+100)*10/100
        else:
            return ((self.speed-45)/45.0/0.1*15+100)*10/100
        
class engineFifthGearState(engineState):
    
    def __init__(self, speed):
        engineState.__init__(self, 5, speed, 48, 96, 60)
        
    def getConsumption(self):
        if self.speed<60:   
            return ((self.speed-60)/60.0/0.1*5+100)*10/100
        else:
            return ((self.speed-60)/60.0/0.1*15+100)*10/100
        
class engineSixthGearState(engineState):
    
    def __init__(self, speed):
        engineState.__init__(self, 6, speed, 64, 128, 80)

    def getConsumption(self):
        if self.speed<80:   
            return ((self.speed-80)/80.0/0.1*5+100)*10/100
        else:
            return ((self.speed-80)/80.0/0.1*15+100)*10/100
            
            
            