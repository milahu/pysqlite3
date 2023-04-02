#!/bin/sh
# tb: https://docs.pytest.org/en/7.1.x/how-to/output.html#modifying-python-traceback-printing
exec python -m pytest --tb=native
