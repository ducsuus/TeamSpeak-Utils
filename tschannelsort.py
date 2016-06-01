import telnetlib

host = "ducsuus.com"
port = "10011"

password = "yHYtaVwx"

t = telnetlib.Telnet(host, port)

t.write(("login serveradmin " + password + "\n").encode())
t.write(("use 1\n").encode())
#"login serveradmin yHYtaVwx\nclientmove clid=28 cid=1200\n

t.write(("clientkick clid=34\n").encode())
