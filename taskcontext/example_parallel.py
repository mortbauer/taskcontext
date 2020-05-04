from __future__ import annotations
import logging
import importlib


from friendly_states import AttributeState
from friendly_states.core import StateMeta


import taskcontext.core as core 
core = importlib.reload(core)


logging.basicConfig(level=logging.INFO)


class SFTPMachine(AttributeState):
    is_machine = True
    attr_name = 'sftp_state'

    class Summary:
        SFTPEnabled:[]
        SFTPDisabled:[]
   
class SFTPEnabled(SFTPMachine):
    def transfer_files(self,path):
        pass

class SFTPDisabled(SFTPMachine):
    pass

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

    def enable_sftp(self) -> [SFTPEnabled]:
        print('Enable sftp')

    def disable_sftp(self) -> [SFTPDisabled]:
        print('Disable sftp')


class Sys(CubeMachine):
    def enter_diag(self) -> [Diag]:
        print("Enter diag")

    def leave_sys(self) -> [Vrp]:
        print("Leave sys")


CubeMachine.complete()

class State:
    def __init__(self,initial:StateMeta):
        self.state = initial 


@core.needs_state(Sys)
def do_in_sys(state:State):
    print('do only in sys')


def run_manual():
    state = State(Init)
    m = core.TaskManager(CubeMachine)
    with m.want(state,do_in_sys.desired_state):
        do_in_sys(state)

def run_automatic():
    state = State(Init)
    m = core.TaskManager(CubeMachine)
    tasks = [
        do_in_sys,
    ]
    m.run_tasks(state,[(t,t.desired_state) for t in tasks])

if __name__ == '__main__':
    run_manual()

