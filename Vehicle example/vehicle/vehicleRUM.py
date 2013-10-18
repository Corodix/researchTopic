from springpython.aop import *
from vehicle import *
from abc import ABCMeta

class vechileRUM():
    
    def __init__(self):
        self.stoppedState = stoppedState()
        self.activeState = activeState()
        self.visitingState = visitingState()
        self.initState = True
        self.currState = self.stoppedState
    
    def switch(self, action, source):
        print(action)
        if action=="on":
            if self.currState==self.stoppedState:
                self.switchTo(self.activeState, source)
        if action=="off":
            if (self.currState == self.activeState) | (self.currState == self.visitingState):
                self.switchTo(self.stoppedState, source) 
        if action=="visit":
            print("visit switch")
            if self.currState == self.activeState:
                print("time to switch to visiting")
                self.switchTo(self.visitingState, source) 
                
    def switchTo(self, nextSate, source):
        if self.initState:
            self.initState = False
        else:
            self.currState.exit()
        nextSate.enter(source)
        self.currState = nextSate

class RUMState():
    __metaclass__ = ABCMeta
    
    def monitor(self):
        return
    
    def optimizer(self):
        return
    
    def enter(self, targetInstance):
        return
    
    def exit(self):
        return
    
    
class stoppedState(RUMState):
    
    def monitor(self):
        print("turning vehicle off?")
        self.oldOff()
    
    def optimizer(self):
        return 
    
    def enter(self, targetInstance):
        print("entering stopped state")
        self.targetInstance = targetInstance
        self.oldOff = getattr(self.targetInstance, "off")
        setattr(self.targetInstance, "off", self.monitor) 
    
    def exit(self):
        setattr(self.targetInstance, "off", self.oldOff) 
        print("exiting stopped state")

class activeState(RUMState):
    
    def monitor(self):
        print("turning vehicle on?")
        self.oldOn()
    
    def optimizer(self):
        return 
    
    def enter(self, targetInstance):
        print("entering active state")
        self.targetInstance = targetInstance
        self.oldOn = getattr(self.targetInstance, "on")
        setattr(self.targetInstance, "on", self.monitor) 
    
    def exit(self):
        setattr(self.targetInstance, "on", self.oldOn) 
        print("exited active state")
    
class visitingState(RUMState):
    
    def __init__(self):
        self.initial = True
    
    def monitor(self):
        print("vehicle is visiting")
        if self.initial:
            self.energy = getattr(self.targetInstance, "energy") 
            self.location = getattr(self.targetInstance, "currentLocation")        
            self.initial = False
        else:    
            self.oldEnergy = self.energy
            self.energy = getattr(self.targetInstance, "energy") 
            oldLocation = self.location
            self.location = getattr(self.targetInstance, "currentLocation")        
            self.distance = getattr(self.targetInstance, "getDistance")(oldLocation, self.location)        
            self.consumed_energy = self.oldEnergy - self.energy               
            self.optimizer()               
            print(getattr(self.targetInstance, "margin"), getattr(self.targetInstance, "threshold"))      
        self.oldVisit()
    
    def optimizer(self):
        if(self.distance>0)&(self.consumed_energy>0):
            self.optimizeMargin()
        if(self.consumed_energy<0):
            self.optimizeThreshold()    
        return 
    
    def optimizeMargin(self):
        'check how much the energy cost deviated from expected, then adjust the margin to compensate'
        lastMargin = self.consumed_energy/self.distance
        if lastMargin>getattr(self.targetInstance, "margin"):
            setattr(self.targetInstance, "margin", lastMargin)  
            
    def optimizeThreshold(self):
        'check if we could have actually made the trip without refueling, if so adjust threshold' 
        originalDest = getattr(self.targetInstance, "getClosest")(getattr(self.targetInstance, "locsToBeVisited"))
        totalDistance = self.distance + (getattr(self.targetInstance, "getDistance")(originalDest, self.location)*getattr(self.targetInstance, "margin"))
        if totalDistance < self.oldEnergy:
            newThreshold = (totalDistance + getattr(self.targetInstance, "threshold"))/2
            setattr(self.targetInstance, "threshold", newThreshold)    
    
    def enter(self, targetInstance):
        print("entered visiting state")
        self.targetInstance = targetInstance
        self.oldVisit = getattr(self.targetInstance, "visit")
        setattr(self.targetInstance, "visit", self.monitor)   
    
    def exit(self):
        setattr(self.targetInstance, "visit", self.oldVisit) 
        print("existed visiting state")
    
    
      



class interceptor(MethodInterceptor):
    
    def __init__(self):
        self.RUM = vechileRUM()
    
    def invoke(self, invocation):
        if invocation.method_name == "on":
            self.RUM.switch("on", invocation.instance)
        else:
            if invocation.method_name == "off":
                self.RUM.switch("off", invocation.instance)    
            else:
                if invocation.method_name == "visit": 
                    self.RUM.switch("visit", invocation.instance)
        invocation.proceed()

    
                
            
            
            