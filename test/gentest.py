#!/usr/bin/python

# Chdir to repo root.
# Since script is not in repo root, fix sys.path so that modules are
# imported from repo, not system.
import sys,os
pn = os.path.dirname(sys.argv[0])
os.chdir(os.path.join(pn,os.pardir))
sys.path.__setitem__(0,os.path.abspath(os.curdir))

from binascii import hexlify

import mmgen.opt as opt
import mmgen.config as g
from mmgen.util import msg,msg_r,msgrepr,msgrepr_exit,red,green
from mmgen.bitcoin import hextowif,privnum2addr

rounds = 100
opts_data = {
	'desc': "Test addresses generated by {} against output of 'keyconv'".format(g.proj_name),
	'usage':"[options] [rounds]",
	'options': """
-h, --help         Print this help message
-s, --system       Test scripts and modules installed on system rather than
                   those in the repo root
""",
	'notes': """

'keyconv' is the address generation utility from the well-known vanitygen
package.  If it's installed on your system, {pnm} will use it by default to
generate Bitcoin addresses.  Otherwise, it falls back on its own internal
routines, which use the Python ecdsa library.

rounds is {} by default.
""".format(rounds,pnm=g.proj_name)
}
cmd_args = opt.opts.init(opts_data,add_opts=["exact_output"])

if len(cmd_args) == 1:
	try:
		rounds = int(cmd_args[0])
		assert rounds > 0
	except:
		msg("'rounds' must be a positive integer")
		sys.exit(1)

elif len(cmd_args) > 1:
	opt.opts.usage(opts_data)

if opt.system: sys.path.pop(0)

from mmgen.addr import test_for_keyconv
if not test_for_keyconv(silent=True):
	msg(
"To run this test, you must install 'keyconv' from the vanitygen package.")
	sys.exit(1)

msg(green("Comparing {}'s internally generated addresses against output of 'keyconv'").format(g.proj_name))

from subprocess import check_output
for i in range(1,rounds+1):
	msg_r("\rRound %s/%s " % (i,rounds))
	sec = hexlify(os.urandom(32))
	wif = hextowif(sec)
	a = privnum2addr(int(sec,16))
	b = check_output(["keyconv", wif]).split()[1]
	if a != b:
		msg_r(red("\nERROR: Addresses do not match!"))
		msg("""
  sec key: {}
  WIF key: {}
  {pnm}:   {}
  keyconv: {}
""".format(sec,wif,a,b,pnm=g.proj_name).rstrip())
		sys.exit(3)

msg(green("\nOK"))