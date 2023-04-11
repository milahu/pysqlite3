#!/bin/sh
# tb: https://docs.pytest.org/en/7.1.x/how-to/output.html#modifying-python-traceback-printing
# capture=no: show output of print()
exec python -m pytest --tb=native --verbose --capture=no
