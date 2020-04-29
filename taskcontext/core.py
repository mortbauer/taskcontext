from __future__ import annotations
import logging
from typing import Any, Callable
from friendly_states import BaseState
from friendly_states.core import StateMeta
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


class TaskContext(ContextDecorator):
    def __init__(self,taskmanager:TaskManager,stateobj:Any, desired_state:StateMeta):
        self._taskmanager = taskmanager
        self._stateobj = stateobj
        self._machine = taskmanager.machine(stateobj)
        self.orig_state = self._machine.get_state()
        self.desired_state = desired_state

    def __enter__(self):
        logger.debug('trying to enter %s',self.desired_state)
        try: 
            transitions = self._taskmanager.calc_transitions(self._machine.get_state(),self.desired_state)
            logger.debug('entering desired context %s needs: %s',self.desired_state,transitions)
            for state,trans_name in transitions:
                logger.debug('executing transition %s in state %s',trans_name,state)
                getattr(state(self._stateobj),trans_name)()
        except Exception:
            logger.info('failed entering the task context, rolling back')
            self._go_back_to_orig()
            raise

    def __exit__(self,*args):
        self._go_back_to_orig()

    def _go_back_to_orig(self):
        try:
            transitions = self._taskmanager.calc_transitions(self._machine.get_state(),self.orig_state)
            logger.debug('leaving desired context %s needs: %s',self.desired_state,transitions)
            for state,trans_name in transitions:
                getattr(state(self._stateobj),trans_name)()
        except Exception:
            logger.exception('failed leaving the task context')


class TaskManager:
   
    def __init__(self, machine: StateMeta):
        self.machine = machine
        self._ctx = None
        self.graph = nx.DiGraph()
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
 
    def want(self,stateobj:Any,desired_state:StateMeta) -> TaskContext:
        if self._ctx is None:
            self._ctx = TaskContext(self,stateobj,desired_state)
        else:
            self._ctx.desired_state = desired_state
        return self._ctx

    def run_tasks(self,stateobj:Any,tasks):
        with ExitStack() as stack:
            for task,desired_state in tasks:
                stack.enter_context(self.want(stateobj,desired_state))
                yield task(stateobj)
                logger.debug('result from %s was %s',task,res)
