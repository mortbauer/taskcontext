from __future__ import annotations
import logging
import importlib


from friendly_states import AttributeState
from friendly_states.core import StateMeta


import taskcontext.core as core 
core = importlib.reload(core)


logging.basicConfig(level=logging.INFO)


class CubeMachine(AttributeState):
    is_machine = True

    class Summary:
        Init: [Vrp]
        Vrp: [Sys, Init]
        Sys: [Diag, Vrp]
        Diag: [Shell, Sys]
        Shell: [Container, Yangsh, Diag]
        Container: [Shell]
        Yangsh: [Shell]


class Init(CubeMachine):
    def login(self) -> [Vrp]:
        print("Login")

class Vrp(CubeMachine):
    def enter_sys(self) -> [Sys]:
        print("Enter sys")

    def logout(self) -> [Init]:
        print("Logout")

class Sys(CubeMachine):
    def enter_diag(self) -> [Diag]:
        print("Enter diag")

    def leave_sys(self) -> [Vrp]:
        print("Leave sys")

class Diag(CubeMachine):
    def enter_shell(self) -> [Shell]:
        print("Enter shell")

    def leave_diag(self) -> [Sys]:
        print("Leave diag")

class Shell(CubeMachine):
    def enter_container(self) -> [Container]:
        print("Enter container")

    def enter_yangsh(self) -> [Yangsh]:
        print("Enter yangsh")

    def leave_shell(self) -> [Diag]:
        print("Leave shell")

class Container(CubeMachine):
    def leave_container(self) -> [Shell]:
        print("Leave container")

class Yangsh(CubeMachine):
    def leave_yangsh(self) -> [Shell]:
        print("Leave yangsh")


CubeMachine.complete()

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
    m = core.TaskManager(CubeMachine)
    with m.want(state,do_in_container.desired_state):
        do_in_container(state)
        with m.want(state,do_in_shell.desired_state):
            do_in_shell(state)

def run_automatic():
    state = State(Init)
    m = core.TaskManager(CubeMachine)
    tasks = [
        do_in_container,
        do_in_shell,
        do_in_yangsh,
    ]
    m.run_tasks(state,[(t,t.desired_state) for t in tasks])

if __name__ == '__main__':
    run_manual()
