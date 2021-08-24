# -*- coding: utf-8 -*-
#
# Copyright (c) 2021~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import abc
import time
import asyncio

class BaseLock(abc.ABC):
    '''
    The base lock class.
    '''

    interval = 0.1

    @abc.abstractmethod
    def _locked_count(self) -> int:
        'get the locked count.'
        raise NotImplementedError

    @abc.abstractmethod
    def _acquire_with_no_wait(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def _release_with_no_wait(self) -> None:
        raise NotImplementedError

    def _acquire_with_blocked(self) -> bool:
        while not self._acquire_with_no_wait():
            time.sleep(self.interval)
        return True

    def _acquire_with_timeout(self, timeout: float) -> bool:
        end = time.monotonic() + timeout
        while end >= time.monotonic():
            if self._acquire_with_no_wait():
                return True
            time.sleep(self.interval)
        return False

    async def _acquire_with_no_wait_async(self) -> bool:
        return self._acquire_with_no_wait()

    async def _release_with_no_wait_async(self) -> None:
        return self._release_with_no_wait()

    async def _acquire_with_blocked_async(self) -> bool:
        while not await self._acquire_with_no_wait_async():
            await asyncio.sleep(self.interval)
        return True

    async def _acquire_with_timeout_async(self, timeout: float):
        # if subclass overrided `_acquire_with_blocked_async`,
        # `wait_for` should has better performance than `sleep`
        try:
            return await asyncio.wait_for(self._acquire_with_blocked_async(), timeout)
        except asyncio.TimeoutError:
            return False

    # sync lock

    def __enter__(self):
        self.acquire(True, None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self, blocking: bool = True, timeout: float = None) -> bool:
        if blocking:
            if timeout is None or timeout < 0:
                return self._acquire_with_blocked()
            elif timeout == 0:
                return self._acquire_with_no_wait()
            else:
                return self._acquire_with_timeout(timeout)
        else:
            if timeout is None or timeout < 0:
                return self._acquire_with_no_wait()
            else:
                raise ValueError('timeout is not supported in non-blocking mode')

    def release(self) -> None:
        if not self.locked():
            raise RuntimeError('cannot release un-acquired lock')
        self._release_with_no_wait()

    def locked(self) -> bool:
        return self._locked_count() > 0

    # async lock

    def __aenter__(self):
        return self.acquire_async(True, None)

    def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.release_async()

    def acquire_async(self, blocking: bool = True, timeout: float = None):
        if blocking:
            if timeout is None or timeout < 0:
                return self._acquire_with_blocked_async()
            elif timeout == 0:
                return self._acquire_with_no_wait_async()
            else:
                return self._acquire_with_timeout_async(timeout)
        else:
            if timeout is None or timeout < 0:
                return self._acquire_with_no_wait_async()
            else:
                raise ValueError('timeout is not supported in non-blocking mode')

    def release_async(self):
        if not self.locked():
            raise RuntimeError('cannot release un-acquired lock')
        return self._release_with_no_wait_async()

__all__ = (
    'BaseLock',
)
