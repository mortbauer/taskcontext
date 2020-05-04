from __future__ import annotations
import logging
import importlib


from friendly_states import AttributeState
from friendly_states.core import StateMeta


import taskcontext.core as core 
core = importlib.reload(core)


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class AutoTransitMixin:
    def __init__(self,state):
        self.obj = state
        desired = type(self)
        if self.get_state() != desired:
            logger.info('autotransit from %s to %s',self.get_state(),desired)
            self.taskmanager.auto_transit_to(state,desired)
        super(AutoTransitMixin,self).__init__(state)


class CubeMachine(AttributeState):
    is_machine = True
    taskmanager = core.TaskManager()

    class Summary:
        Init: [Vrp]
        Vrp: [Sys, Init]
        Sys: [Diag, Vrp]
        Diag: [Shell, Sys]
        Shell: [Container, Yangsh, Diag]
        Container: [Shell]
        Yangsh: [Shell]


class Init(AutoTransitMixin,CubeMachine):
    def login(self) -> [Vrp]:
        print("Login")

class Vrp(AutoTransitMixin,CubeMachine):
    def enter_sys(self) -> [Sys]:
        print("Enter sys")

    def logout(self) -> [Init]:
        print("Logout")


class Sys(AutoTransitMixin,CubeMachine):
    def enter_diag(self) -> [Diag]:
        print("Enter diag")

    def leave_sys(self) -> [Vrp]:
        print("Leave sys")

class Diag(AutoTransitMixin,CubeMachine):
    def enter_shell(self) -> [Shell]:
        print("Enter shell")

    def leave_diag(self) -> [Sys]:
        print("Leave diag")

class Shell(AutoTransitMixin,CubeMachine):
    def enter_container(self) -> [Container]:
        print("Enter container")

    def enter_yangsh(self) -> [Yangsh]:
        print("Enter yangsh")

    def leave_shell(self) -> [Diag]:
        print("Leave shell")

class Container(AutoTransitMixin,CubeMachine):
    def leave_container(self) -> [Shell]:
        print("Leave container")

class Yangsh(AutoTransitMixin,CubeMachine):
    def leave_yangsh(self) -> [Shell]:
        print("Leave yangsh")


CubeMachine.complete()
CubeMachine.taskmanager.init(CubeMachine)

class State:
    def __init__(self,initial:StateMeta):
        self.state = initial 


@core.needs_state(Shell)
def do_in_shell(state:State):
    print('do only in shell')

@core.needs_state(Container)
def do_in_container(state:State):
    print('do only in container')

@core.needs_state(Yangsh)
def do_in_yangsh(state:State):
    print('do only in yangsh')


def run_manual():
    state = State(Init)
    try:
        Container(state)
        do_in_container(state)
        Shell(state)
        do_in_shell(state)
    finally:
        CubeMachine.taskmanager.auto_transit_to(state,Init)

def run_automatic():
    state = State(Init)
    m = core.TaskManager(CubeMachine)
    tasks = [
        do_in_container,
        do_in_shell,
        do_in_yangsh,
    ]
    for res in m.run_tasks(state,[(t,t.desired_state) for t in tasks]):
        pass

if __name__ == '__main__':
    run_manual()
