# This file is placed in the Public Domain.
#
# pylint: disable=C,I,R
# flake8: noqa=E501


"configure tests"


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 5:
        session.exitstatus = 0
