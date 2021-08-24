# -*- coding: utf-8 -*-
#
# Copyright (c) 2021~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import *

from .baselock import BaseLock

class _EasyRLock(BaseLock):
    def __init__(self, acquire, release):
        self.__locked_count = 0
        self.__acquire = acquire
        self.__release = release

    def _locked_count(self) -> int:
        return self.__locked_count

    def _acquire_with_no_wait(self) -> bool:
        if self.__locked_count > 0 or self.__acquire():
            self.__locked_count += 1
            return True
        return False

    def _release_with_no_wait(self) -> None:
        self.__locked_count -= 1
        if self.__locked_count == 0:
            self.__release()


def make_rlock(acquire: Callable[[], bool], release: Callable[[], None]) -> BaseLock:
    return _EasyRLock(acquire, release)
