from abc import *
import abc
import types

class RUM():
    
    def __init__(self, component):
        self.component = component
        self.index = 0
        self.transitions = []
        
    def switchMethods(self, original, replacement):
        storage = getattr(self.component, original)
        setattr(self.component, original, replacement) 
        return storage
    
    def stateChangeCatcherBeforeAndAfter(self, name, variables):
        
        'create dynamic replacement function at runtime'
        func_str = "def "
        func_str += name+"BeforeAndAfterReplacement"
        func_str += "(self, *args):"
        func_str += "\n\t"
        func_str += "old = {}"
        func_str += "\n\t"
        for var in variables:
            func_str += "old['"+var+"'] = self.component."+var
            func_str += "\n\t"
        func_str += "self."+name+"(*args)"
        func_str += "\n\t"
        func_str += "new = {}"
        func_str += "\n\t"
        for var in variables:
            func_str += "new['"+var+"'] = self.component."+var
            func_str += "\n\t"
        func_str += "self.checkAndTransit(old, new, '"+name+"')"
        func_str += "\n"
        
        'use exec to define the function'
        exec(func_str)
        
        'add the function as a method to this class'
        set_self = "self."+name+"BeforeAndAfterReplacement"+" = types.MethodType("+name+"BeforeAndAfterReplacement, self)"
        exec(set_self)
        
        'retrieve the original method'
        temp = getattr(self.component, name)
        
        'replace it with the new function'
        set_replacement = "setattr(self.component, name, self."+name+"BeforeAndAfterReplacement)"
        exec(set_replacement) 
        
        'add the original method to this class so it can be called by the function defined earlier'
        set_original = "self."+name+"=temp"
        exec(set_original)
     
    def addStates(self, states):
        self.states = states
        self.state = None
        
    def setInitialState(self, state):
        if self.state == None:
            self.state = self.states.get(state)
        
    def addTransition(self, transition):
        self.transitions.append(transition)
        
    def checkAndTransit(self, oldVars, newVars, methodName):
        for transition in self.transitions:
            if self.states.get(transition.currState) == self.state:
                if transition.shouldTransit(oldVars, newVars, methodName):
                    self.state = self.states.get(transition.nextState)
                    return
        
class Transition():
    
    def __init__(self, currState, nextState, rules):
        self.currState = currState
        self.nextState = nextState
        self.rules = rules
        
    'returns true if the current state warrants a transit to the nextState'
    def shouldTransit(self, oldVars, newVars, methodName):
        transit = True
        for rule in self.rules:
            transit &= rule.validates(oldVars, newVars, methodName)
        return transit
   
class Rule():    
    
    def __init__(self, expression):
        self.expression = expression
    
    def validates(self, oldVariables, newVariables, methodName):
        expr = ""
        expr += self.expression
        expr = self.loadVar(expr, oldVariables, "old:")
        expr = self.loadVar(expr, newVariables, "new:")
        expr = self.loadMethodNames(expr, methodName)     
        return eval(expr)
    
    def loadVar(self, expr, variables, keyword):
        'search for keyword (old: or new:), replace it with the corresponding variable'
        result = ""
        words = expr.split()
        for word in words:
            if word.startswith(keyword):
                result += variables.get(word.replace(keyword, "")).__str__()+" "
            else:
                result += word+" "
        return result
                
    def loadMethodNames(self, expr, methodName):
        'search for methodName:, replace it with the methodName variable'
        result = ""
        words = expr.split()
        for word in words:
            if word.startswith("methodName:"):
                result += word.replace("methodName:", "'"+methodName+"'") +" "
            else:
                result += word+" "
        return result
