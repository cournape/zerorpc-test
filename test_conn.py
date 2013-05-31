import argparse
import hashlib
import random
import string
import sys

from cStringIO import StringIO

import zerorpc

def client_main(namespace):
    url = "tcp://{}:{}".format(namespace.host, namespace.port)

    print "Connecting to {}".format(url)

    c = zerorpc.Client()
    c.connect(url)

    print "testing echo"
    print c.echo("hello")

    n = namespace.size

    s = StringIO()
    for i in range(n):
        data = "a" * 1024
        s.write(data)
    data = s.getvalue()
    md5 = hashlib.md5(data).hexdigest()

    print "sending"
    print c.send(data, md5)
    print "done"

class TestService(object):
    def echo(self, s):
        return s

    def send(self, data, md5):
        print "received a message of {} kbytes".format(len(data) / 1024)
        if hashlib.md5(data).hexdigest() == md5:
            return True
        else:
            return False

def server_main(namespace):
    url = "tcp://{}:{}".format(namespace.interface, namespace.port)

    print "Listening to {}".format(url)

    server = zerorpc.Server(TestService())
    server.bind(url)
    server.run()

def main():
    argv = sys.argv[1:]

    p = argparse.ArgumentParser()
    subparsers = p.add_subparsers()

    client_p = subparsers.add_parser("client")
    client_p.add_argument("--host", default="localhost")
    client_p.add_argument("--port", default=5555, type=int)
    client_p.add_argument("--size", default=1, help="payload size (in kb)", type=int)
    client_p.set_defaults(func=client_main)

    server_p = subparsers.add_parser("server")
    server_p.add_argument("--interface", default="127.0.0.1")
    server_p.add_argument("--port", default=5555, type=int)
    server_p.set_defaults(func=server_main)

    namespace = p.parse_args(argv)
    namespace.func(namespace)

if __name__ == "__main__":
    main()
