import contextlib
import errno
import os
import signal
import socket
import struct


def builtin_base(exc_type):
    for cls in exc_type.mro():
        if cls.__module__ != 'py3oserror':
            return cls


# pytest.raises isn't catching these errors on Python 2.6
# implement a simple version with standard exception-catching semantics
# also checks that the base class of the fake exception matches the real one
@contextlib.contextmanager
def raises(exc_type, check_base=True):
    try:
        yield
    except exc_type as e:
        if check_base:
            assert type(e) is builtin_base(exc_type)
    else:
        raise AssertionError('Expected %s to be raised' % exc_type.__name__)


def raise_errno(exc_type, err):
    raise exc_type(err, os.strerror(err))


def test_blocking_io():
    from py3oserror import BlockingIOError

    left, right = socket.socketpair()
    left.setblocking(0)

    with raises(BlockingIOError):
        left.recv(1)


def test_child_process():
    from py3oserror import ChildProcessError
    with raises(ChildProcessError):
        os.waitpid(-1, 0)


def test_connection_error():
    from py3oserror import ConnectionError

    left, right = socket.socketpair()
    right.close()

    with raises(ConnectionError, check_base=False):
        left.send(b'x')


def test_broken_pipe():
    from py3oserror import BrokenPipeError

    left, right = socket.socketpair()
    right.close()

    with raises(BrokenPipeError):
        left.send(b'x')


def test_connection_aborted():
    from py3oserror import ConnectionAbortedError

    with raises(ConnectionAbortedError):
        # TODO real-world example
        raise_errno(socket.error, errno.ECONNABORTED)


def test_connection_refused():
    from py3oserror import ConnectionRefusedError

    # find an available address and then close the connection to make sure
    # it's unbound
    sock = socket.socket()
    try:
        sock.bind(('', 0))
        addr = sock.getsockname()
    finally:
        sock.close()

    with raises(ConnectionRefusedError):
        socket.create_connection(addr)


def test_connection_reset():
    from py3oserror import ConnectionResetError

    # connect a client and server socket
    listener = socket.socket()
    client = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    client.connect(listener.getsockname())
    server, _ = listener.accept()

    # force server to reset the connection
    server.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                      struct.pack('ii', 1, 0))
    server = None

    with raises(ConnectionResetError):
        client.recv(1)


def test_file_exists_error(tmpdir):
    from py3oserror import FileExistsError
    with raises(FileExistsError):
        os.mkdir(str(tmpdir))


def test_file_not_found_error():
    from py3oserror import FileNotFoundError
    with raises(FileNotFoundError):
        open('does-not-exist.txt')


@contextlib.contextmanager
def sig_handler(signum, handler):
    orig = signal.signal(signum, handler)
    try:
        yield handler
    finally:
        signal.signal(signum, orig)


def test_interrupted():
    from py3oserror import InterruptedError

    left, right = os.pipe()

    with sig_handler(signal.SIGALRM, lambda n,f: None):
        signal.setitimer(signal.ITIMER_REAL, 0.1)

        with raises(InterruptedError):
            os.read(left, 1)


def test_is_a_directory():
    from py3oserror import IsADirectoryError
    with raises(IsADirectoryError):
        open(os.path.dirname(__file__))


def test_not_a_directory():
    from py3oserror import NotADirectoryError
    with raises(NotADirectoryError):
        os.listdir(__file__)


def test_permission(tmpdir):
    from py3oserror import PermissionError

    path = str(tmpdir.join('test.txt'))

    # just create the file
    with open(path, 'w'):
        pass

    # make it read-only
    os.chmod(path, 0o400)

    with raises(PermissionError):
        open(path, 'w')


def test_process_lookup():
    from py3oserror import ProcessLookupError

    # get a pid that we know has exited, so that the signal will fail
    pid = os.fork()
    if pid == 0:
        os._exit(0)
    os.waitpid(pid, 0)

    with raises(ProcessLookupError):
        os.kill(pid, signal.SIG_DFL)


def test_timeout():
    from py3oserror import TimeoutError
    with raises(TimeoutError):
        # TODO real-world example
        raise_errno(IOError, errno.ETIMEDOUT)
