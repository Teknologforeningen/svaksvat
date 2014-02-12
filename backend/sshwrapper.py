"""
Platform independent ssh port forwarding

Much code stolen from the paramiko example
"""
import select
try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

import paramiko

SSH_PORT = 22
DEFAULT_PORT = 5432


class ForwardServer (SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler (SocketServer.BaseRequestHandler):

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host,
                                                    self.chain_port),
                                                   self.request.getpeername())
        except Exception as e:
            print('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                            self.chain_port,
                                                            repr(e)))
            return
        if chan is None:
            print('Incoming request to %s:%d was rejected by the SSH server.'
                  % (self.chain_host, self.chain_port))
            return

        print('Connected!  Tunnel open %r -> %r -> %r' %
              (self.request.getpeername(),
               chan.getpeername(), (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        print('Tunnel closed from %r' % (peername,))


def forward_tunnel(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHander (Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    ForwardServer(('', local_port), SubHander).serve_forever()


def connect_ssh(server, login, password, port=SSH_PORT):
    """Return a paramiko.SSHClient on successfull connection, otherwise returns
    None
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    print('Connecting to ssh host %s:%d ...' % (server, port))
    try:
        client.connect(server, port, login, password=password)
        print("Connection successful")
        return client
    except Exception as e:
        print('*** Failed to connect to %s:%d: %r' % (server, port, e))
        return None


def portforward(client, threadfinishedmutex,
                remote_host,
                local_port=DEFAULT_PORT,
                remote_port=DEFAULT_PORT):
    """Neverending portforwarding thread. Locks threadfinishedmutex
    on failure.

    client has to be a connected paramiko.SSHClient."""

    print('Now forwarding port %d to %s:%d ...' % (local_port, remote_host,
                                                   remote_port))

    try:
        forward_tunnel(local_port, remote_host, remote_port,
                       client.get_transport())
        threadfinishedmutex.acquire()
    except Exception as e:
        threadfinishedmutex.acquire()
        raise e
