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
walletgen.py:  Routines used for seed generation and wallet creation
"""

import sys
import mmgen.config as g
from mmgen.util import msg, msg_r, qmsg, qmsg_r, get_char, prompt_and_get_char
from binascii import hexlify

def get_random_data_from_user(opts):

	ulen = opts['usr_randlen']

	if g.quiet:
		msg("Enter %s random symbols" % ulen)
	else:
		msg("""
We're going to be paranoid and not fully trust your OS's random number
generator.  Please type %s symbols on your keyboard.  Type slowly and choose
your symbols carefully for maximum randomness.  Try to use both upper and
lowercase as well as punctuation and numerals.  What you type will not be
displayed on the screen.
""" % ulen)

	prompt = "You may begin typing.  %s symbols left: "
	msg_r(prompt % ulen)

	import time
	# time.clock() always returns zero, so we'll use time.time()
	saved_time = time.time()

	user_rand_data,intervals = "",[]

	for i in range(ulen):
		user_rand_data += get_char(immed_chars="ALL")
		msg_r("\r" + prompt % (ulen - i - 1))
		now = time.time()
		intervals.append(now - saved_time)
		saved_time = now

	if g.quiet:
		msg_r("\r")
	else:
		msg_r("\rThank you.  That's enough." + " "*15 + "\n\n")

	prompt = "User random data successfully acquired.  Press ENTER to continue"
	prompt_and_get_char(prompt,"",enter_ok=True)

	return user_rand_data, ["{:.22f}".format(i) for i in intervals]


def display_os_random_data(os_rand_data):
	print "Rand1: {}\nRand2: {}".format(
			*[hexlify(i) for i in os_rand_data])


def display_user_random_data(user_rand_data,intervals_fmt):
	msg("\nUser random data: " + user_rand_data)
	msg("Keystroke time intervals:")
	for i in range(0,len(intervals_fmt),3):
		msg("  " + " ".join(intervals_fmt[i:i+3]))
