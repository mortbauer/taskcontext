Developing
##########

Install extras::

    python -m pip install .[test] .[lint]


Testing
#######


https://pypi.org/project/tox-pyenv/

Ideas
#####

Parallel States
***************

To model a parallel substate, for example you have a `MenuMachine` and only in
the specific menu `SFTPState` it is possible to change the `SFTPState`. The
`SFTPState` would be a substate which lives indipendently (parallel) from the
main `MenuMachine` state, however it can only be changed when being when the
`MenuMachine` is in the `SFTPMenu` state.

It could look something like::

    class SFTPMenu(MenuMachine):
        def enable_sftp(self) -> Prallel(SFTPEnabled):
            pass

        def disable_sftp(self) -> Prallel(SFTPDisabled):
            pass

calling `enable_sftp` or `disable_sftp` would not change the main menu state,
which would still be in `SFTPMenu` but the substate would change.

The object carrying the state would probably have multiple attribs, like
`menustate` and `sftpstate`. 

Automatic Transitions
*********************

I created this module for automatic transitions, it however only works
transparently if there is only one transitions to each state, my current
solution is::

    class MyState(MyMachine):
        def transition_which_is_not_normal_path(self):
            self.state(MyState,NewState)

which works but is not transparent, better would be something like::

    class MyState(MyMachine):
        def transition_which_is_not_normal_path(self) -> NoAutoTrans(NewState):
            self.state(MyState,NewState)


And to have an easier auto transition it would be great to maybe set some key
in the Machine to do auto transitions if possible and then::

    MyState(stateobj)

would automaticallly transition if it wouldn't be in the correct state.
