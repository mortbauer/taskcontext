from io import StringIO
from unittest.mock import MagicMock, patch
from taskcontext.example import *

def test_example_run_manual():
    with patch('sys.stdout', new_callable=StringIO) as stdout:
        run_manual()
        assert stdout.getvalue().splitlines() == [
                'Login',
                'Enter sys',
                'Enter diag',
                'Enter shell',
                'Enter container',
                'do only in container',
                'Leave container',
                'do only in shell',
                'Leave shell',
                'Leave diag',
                'Leave sys',
                'Logout',
            ]

def test_example_run_automatic():
    with patch('sys.stdout', new_callable=StringIO) as stdout:
        run_automatic()
        assert stdout.getvalue().splitlines() == [
                'Login',
                'Enter sys',
                'Enter diag',
                'Enter shell',
                'Enter container',
                'do only in container',
                'Leave container',
                'do only in shell',
                'Enter yangsh',
                'do only in yangsh',
                'Leave yangsh',
                'Leave shell',
                'Leave diag',
                'Leave sys',
                'Logout',
            ]



