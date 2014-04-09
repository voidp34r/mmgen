#!/usr/bin/env python
#
# mmgen = Multi-Mode GENerator, command-line Bitcoin cold storage solution
# Copyright (C) 2013 by philemon <mmgen-py@yandex.com>
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
term.py:  Terminal-handling routines for the mmgen suite
"""

import sys, os, struct

def msg(s):   sys.stderr.write(s + "\n")
def msg_r(s): sys.stderr.write(s)

def _kb_hold_protect_unix():

	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	tty.setcbreak(fd)

	timeout = float(0.3)

	try:
		while True:
			key = select([sys.stdin], [], [], timeout)[0]
			if key: sys.stdin.read(1)
			else: break
	except KeyboardInterrupt:
		msg("\nUser interrupt")
		sys.exit(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _get_keypress_unix(prompt="",immed_chars=""):

	msg_r(prompt)
	timeout = float(0.3)

	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	tty.setcbreak(fd)

	try:
		while True:
			select([sys.stdin], [], [], False)
			ch = sys.stdin.read(1)
			if immed_chars == "ALL" or ch in immed_chars:
				return ch
			if immed_chars == "ALL_EXCEPT_ENTER" and not ch in "\n\r":
				return ch
			second_key = select([sys.stdin], [], [], timeout)[0]
			if second_key: continue
			else: return ch
	except KeyboardInterrupt:
		msg("\nUser interrupt")
		sys.exit(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _kb_hold_protect_mswin():

	timeout = float(0.5)

	try:
		while True:
			hit_time = time.time()
			while True:
				if msvcrt.kbhit():
					msvcrt.getch()
					break
				if float(time.time() - hit_time) > timeout:
					return
	except KeyboardInterrupt:
		msg("\nUser interrupt")
		sys.exit(1)


def _get_keypress_mswin(prompt="",immed_chars=""):

	msg_r(prompt)
	timeout = float(0.5)

	try:
		while True:
			if msvcrt.kbhit():
				ch = msvcrt.getch()

				if ord(ch) == 3: raise KeyboardInterrupt

				if immed_chars == "ALL" or ch in immed_chars:
					return ch
				if immed_chars == "ALL_EXCEPT_ENTER" and not ch in "\n\r":
					return ch

				hit_time = time.time()

				while True:
					if msvcrt.kbhit(): break
					if float(time.time() - hit_time) > timeout:
						return ch
	except KeyboardInterrupt:
		msg("\nUser interrupt")
		sys.exit(1)


def _get_terminal_size_linux():

	def ioctl_GWINSZ(fd):
		try:
			import fcntl
			import termios
			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
			return cr
		except:
			pass

	cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)

	if not cr:
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			cr = ioctl_GWINSZ(fd)
			os.close(fd)
		except:
			pass

	if not cr:
		try:
			cr = (os.environ['LINES'], os.environ['COLUMNS'])
		except:
			return 80,25

	return int(cr[1]), int(cr[0])


def _get_terminal_size_mswin():
	try:
		from ctypes import windll, create_string_buffer
		# stdin handle is -10
		# stdout handle is -11
		# stderr handle is -12
		h = windll.kernel32.GetStdHandle(-12)
		csbi = create_string_buffer(22)
		res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
		if res:
			(bufx, bufy, curx, cury, wattr,
			 left, top, right, bottom,
			 maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
			sizex = right - left + 1
			sizey = bottom - top + 1
			return sizex, sizey
	except:
		return 80,25

try:
	import tty, termios
	from select import select
	get_char = _get_keypress_unix
	kb_hold_protect = _kb_hold_protect_unix
	get_terminal_size = _get_terminal_size_linux
except:
	try:
		import msvcrt, time
		get_char = _get_keypress_mswin
		kb_hold_protect = _kb_hold_protect_mswin
		get_terminal_size = _get_terminal_size_mswin
	except:
		if not sys.platform.startswith("linux") \
				and not sys.platform.startswith("win"):
			msg("Unsupported platform: %s" % sys.platform)
			msg("This program currently runs only on Linux and Windows")
		else:
			msg("Unable to set terminal mode")
		sys.exit(2)

if __name__ == "__main__":
	print "columns: {}, rows: {}".format(*get_terminal_size())
