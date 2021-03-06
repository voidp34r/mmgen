#!/usr/bin/env python
#
# mmgen = Multi-Mode GENerator, command-line Bitcoin cold storage solution
# Copyright (C)2013-2018 The MMGen Project <mmgen@tuta.io>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
test.py:  Shared routines for the test suites
"""

import os
from binascii import hexlify

from mmgen.common import *

def path_join(*args,**kwargs):
	if not 'decode' in kwargs: kwargs['decode'] = True
	assert type(kwargs['decode']) == bool
	assert kwargs.keys() == ['decode']
	ret = os.path.join(*[a.encode('utf8') for a in args])
	return ret.decode('utf8') if kwargs['decode'] else ret

def cleandir(d):
	from shutil import rmtree
	try:    files = [f.decode('utf8') for f in os.listdir(d)]
	except: return

	gmsg(u"Cleaning directory '{}'".format(d))
	for f in files:
		try:
			os.unlink(path_join(d,f,decode=False))
		except:
			rmtree(path_join(d,f,decode=False))

def getrandnum(n): return int(hexlify(os.urandom(n)),16)
def getrandhex(n): return hexlify(os.urandom(n))
def getrandstr(num_chars,no_space=False):
	n,m = 95,32
	if no_space: n,m = 94,33
	return ''.join([chr(ord(i)%n+m) for i in list(os.urandom(num_chars))])

def mk_tmpdir(d):
	try: os.mkdir(d,0755)
	except OSError as e:
		if e.errno != 17: raise
	else:
		vmsg(u"Created directory '{}'".format(d))

def mk_tmpdir_path(path,cfg):
	try:
		name = os.path.split(cfg['tmpdir'])[-1]
		src = os.path.join(path,name)
		try:
			os.unlink(cfg['tmpdir'])
		except OSError as e:
			if e.errno != 2: raise
		finally:
			os.mkdir(src)
			os.symlink(src,cfg['tmpdir'])
	except OSError as e:
		if e.errno != 17: raise
	else: msg("Created directory '{}'".format(cfg['tmpdir']))

def get_tmpfile_fn(cfg,fn):
	return os.path.join(cfg['tmpdir'],fn)

def write_to_tmpfile(cfg,fn,data,binary=False):
	write_data_to_file(
		os.path.join(cfg['tmpdir'],fn),
		data,
		silent=True,
		binary=binary
	)

def read_from_file(fn,binary=False):
	from mmgen.util import get_data_from_file
	return get_data_from_file(fn,silent=True,binary=binary)

def read_from_tmpfile(cfg,fn,binary=False):
	return read_from_file(os.path.join(cfg['tmpdir'],fn),binary=binary)

def ok():
	if opt.profile: return
	if opt.verbose or opt.exact_output:
		gmsg('OK')
	else: msg(' OK')

def ok_or_die(val,chk_func,s,skip_ok=False):
	try: ret = chk_func(val)
	except: ret = False
	if ret:
		if not skip_ok: ok()
	else:
		rdie(3,"Returned value '{}' is not a {}".format((val,s)))

def cmp_or_die(s,t,skip_ok=False):
	if s == t:
		if not skip_ok: ok()
	else:
		m = 'ERROR: recoded data:\n{}\ndiffers from original data:\n{}'
		rdie(3,m.format(repr(t),repr(s)))

def init_coverage():
	coverdir = os.path.join('test','trace')
	acc_file = os.path.join('test','trace.acc')
	try: os.mkdir(coverdir,0755)
	except: pass
	return coverdir,acc_file
