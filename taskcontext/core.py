from __future__ import annotations
import logging
from typing import Any, Callable
from friendly_states.core import StateMeta, BaseState
import networkx as nx
from functools import wraps
from contextlib import contextmanager,ContextDecorator, ExitStack

logger = logging.getLogger(__name__)


class WrongState(Exception):
    pass

def needs_state(desired_state):
    """ Check we are in the right state """
    def decorator(func):
        if hasattr(func,'desired_state'):
            raise Exception('Forbidden to override desired state')
        func.desired_state = desired_state
        @wraps(func)
        def wrapper(obj,*args,**kwargs):
            if obj.state != desired_state:
                raise WrongState(f'state is "{obj.state}" but wants "{desired_state}"')
            return func(obj,*args,**kwargs)
        return wrapper
    return decorator

class AttributeState(BaseState):
    """
    A simple base state class which keeps the state in an attribute of the object.
    This is the most common base class for machines.

    By default the attribute is named 'state', this can be overridden with the
    attr_name attribute on this class.
    """

    attr_name = "state"

    def get_state(self):
        return getattr(self.obj, self.attr_name)

    def set_state(self, previous_state, new_state):
        setattr(self.obj, self.attr_name, new_state)


class OrigContext(ContextDecorator):
    def __init__(self,taskmanager:TaskManager,stateobj:Any):
        self._taskmanager = taskmanager
        self._stateobj = stateobj
        self._machine = taskmanager.machine(stateobj)
        self.orig_sate = None

    def __enter__(self):
        self.orig_state = self._machine.get_state()

    def __exit__(self,*args):
        self._go_back_to_orig()

    def _go_back_to_orig(self):
        logger.debug('trying to go back to %s',self.orig_state)
        self._taskmanager.auto_transit_to(self._stateobj,self.orig_state)


class TaskContext(OrigContext):
    def __init__(self,taskmanager:TaskManager,stateobj:Any, desired_state:StateMeta):
        super(TaskContext,self).__init__(taskmanager,stateobj)
        self.desired_state = desired_state

    def __enter__(self):
        super(TaskContext,self).__enter__()
        logger.debug('trying to enter %s',self.desired_state)
        try: 
            self._taskmanager.auto_transit_to(self._stateobj,self.desired_state)
        except Exception:
            logger.info('failed entering the task context, rolling back')
            self._go_back_to_orig()
            raise

  

class TaskManager:
   
    def __init__(self, machine: StateMeta = None):
        self._ctx = None
        self.graph = nx.DiGraph()
        if machine is not None:
            self.init(machine)

    def init(self,machine: StateMeta):
        self.machine = machine
        for state in machine.states:
            for transition in state.transitions:
                output_state = next(iter(transition.output_states))
                self.graph.add_edge(state,output_state,transition=transition)

    def calc_transitions(self,orig_sate:StateMeta,desired_state:StateMeta):
        states = nx.shortest_path(self.graph,orig_sate,desired_state)
        needed_transitions = []
        for i,state in enumerate(states[:-1]):
            edge_data = self.graph.get_edge_data(state,states[i+1])
            needed_transitions.append((state,edge_data['transition'].__name__))
        return needed_transitions
 
    def auto_transit_to(self,stateobj:Any,desired_state:StateMeta):
        orig_state = self.machine(stateobj).get_state()
        logger.debug('orig state is %s, desired_state is %s',orig_state,desired_state)
        transitions = self.calc_transitions(orig_state,desired_state)
        logger.debug('to transit to %s we need to apply: %s',desired_state,transitions)
        for state,trans_name in transitions:
            getattr(state(stateobj),trans_name)()

    def want(self,stateobj:Any,desired_state:StateMeta) -> TaskContext:
        if self._ctx is None:
            self._ctx = TaskContext(self,stateobj,desired_state)
        else:
            self._ctx.desired_state = desired_state
        return self._ctx

    def run_tasks(self,stateobj:Any,tasks):
        with OrigContext(self,stateobj):
            for task,desired_state in tasks:
                self.auto_transit_to(stateobj,desired_state)
                yield task(stateobj)
