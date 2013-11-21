import errno
import socket
import sys


if sys.version_info[0] == 3:
    if sys.version_info[1] < 3:
        raise ValueError('Requires Python >= 3.3 for new OSError subclasses')

    BlockingIOError = BlockingIOError
    ChildProcessError = ChildProcessError
    ConnectionError = ConnectionError
    BrokenPipeError = BrokenPipeError
    ConnectionAbortedError = ConnectionAbortedError
    ConnectionRefusedError = ConnectionRefusedError
    ConnectionResetError = ConnectionResetError
    FileExistsError = FileExistsError
    FileNotFoundError = FileNotFoundError
    InterruptedError = InterruptedError
    IsADirectoryError = IsADirectoryError
    NotADirectoryError = NotADirectoryError
    PermissionError = PermissionError
    ProcessLookupError = ProcessLookupError
    TimeoutError = TimeoutError

else:
    class _ErrnoMeta(type):
        def __instancecheck__(cls, inst):
            return (isinstance(inst, EnvironmentError)
                    and inst.errno in cls._errnos)

        def __subclasscheck__(cls, C):
            exc_type, exc_value, exc_tb = sys.exc_info()
            # if there's a current exception of the same type, assume we're
            # called to check "except C:" and test the exception instance
            if C is exc_type:
                return cls.__instancecheck__(exc_value)
            else:
                return super(_ErrnoMeta, cls).__subclasscheck__(C)


    class BlockingIOError(socket.error):
        __metaclass__ = _ErrnoMeta
        _errnos = (
            errno.EAGAIN,
            errno.EALREADY,
            errno.EWOULDBLOCK,
            errno.EINPROGRESS,
        )


    class ChildProcessError(OSError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.ECHILD,)


    class ConnectionError(socket.error):
        __metaclass__ = _ErrnoMeta
        # TODO could detect from subclasses
        _errnos = (
            errno.EPIPE, errno.ESHUTDOWN, # BrokenPipeError
            errno.ECONNABORTED, # ConnectionAbortedError
            errno.ECONNREFUSED, # ConnectionRefusedError
            errno.ECONNRESET, # ConnectionResetError
        )


    class BrokenPipeError(ConnectionError):
        _errnos = (errno.EPIPE, errno.ESHUTDOWN)


    class ConnectionAbortedError(ConnectionError):
        _errnos = (errno.ECONNABORTED,)


    class ConnectionRefusedError(ConnectionError):
        _errnos = (errno.ECONNREFUSED,)


    class ConnectionResetError(ConnectionError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.ECONNRESET,)


    class FileExistsError(OSError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.EEXIST,)


    class FileNotFoundError(IOError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.ENOENT,)


    class InterruptedError(OSError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.EINTR,)


    class IsADirectoryError(IOError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.EISDIR,)


    class NotADirectoryError(OSError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.ENOTDIR,)


    class PermissionError(IOError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.EACCES, errno.EPERM)


    class ProcessLookupError(OSError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.ESRCH,)


    class TimeoutError(IOError):
        __metaclass__ = _ErrnoMeta
        _errnos = (errno.ETIMEDOUT,)
