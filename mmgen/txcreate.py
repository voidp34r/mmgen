#!/usr/bin/env python
#
# mmgen = Multi-Mode GENerator, command-line Bitcoin cold storage solution
# Copyright (C)2013-2016 Philemon <mmgen-py@yandex.com>
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
txcreate: Create a Bitcoin transaction to and from MMGen- or non-MMGen inputs
          and outputs
"""

from mmgen.common import *
from mmgen.tx import *
from mmgen.tw import *

pnm = g.proj_name

txcreate_notes = """
The transaction's outputs are specified on the command line, while its inputs
are chosen from a list of the user's unpent outputs via an interactive menu.

If the transaction fee is not specified by the user, it will be calculated
using bitcoind's "estimatefee" function for the default (or user-specified)
number of confirmations.  If "estimatefee" fails, the global default fee of
{g.tx_fee} BTC will be used.

Dynamic fees will be multiplied by the value of '--tx-fee-adj', if specified.

Ages of transactions are approximate based on an average block discovery
interval of {g.mins_per_block} minutes.

All addresses on the command line can be either Bitcoin addresses or {pnm}
addresses of the form <seed ID>:<index>.

To send the value of all inputs (minus TX fee) to a single output, specify
one address with no amount on the command line.
""".format(g=g,pnm=pnm)

wmsg = {
	'addr_in_addrfile_only': """
Warning: output address {mmgenaddr} is not in the tracking wallet, which means
its balance will not be tracked.  You're strongly advised to import the address
into your tracking wallet before broadcasting this transaction.
""".strip(),
	'addr_not_found': """
No data for {pnm} address {mmgenaddr} could be found in either the tracking
wallet or the supplied address file.  Please import this address into your
tracking wallet, or supply an address file for it on the command line.
""".strip(),
	'addr_not_found_no_addrfile': """
No data for {pnm} address {mmgenaddr} could be found in the tracking wallet.
Please import this address into your tracking wallet or supply an address file
for it on the command line.
""".strip(),
	'non_mmgen_inputs': """
NOTE: This transaction includes non-{pnm} inputs, which makes the signing
process more complicated.  When signing the transaction, keys for non-{pnm}
inputs must be supplied to '{pnl}-txsign' in a file with the '--keys-from-file'
option.
Selected non-{pnm} inputs: %s
""".strip().format(pnm=pnm,pnl=pnm.lower()),
	'not_enough_btc': """
Not enough BTC in the inputs for this transaction (%s BTC)
""".strip(),
	'throwaway_change': """
ERROR: This transaction produces change (%s BTC); however, no change address
was specified.
""".strip(),
}

def select_unspent(unspent,prompt):
	while True:
		reply = my_raw_input(prompt).strip()
		if reply:
			selected = AddrIdxList(fmt_str=','.join(reply.split()),on_fail='return')
			if selected:
				if selected[-1] <= len(unspent):
					return selected
				msg('Unspent output number must be <= %s' % len(unspent))

def mmaddr2baddr(c,mmaddr,ad_w,ad_f):

	# assume mmaddr has already been checked
	btc_addr = ad_w.mmaddr2btcaddr(mmaddr)

	if not btc_addr:
		if ad_f:
			btc_addr = ad_f.mmaddr2btcaddr(mmaddr)
			if btc_addr:
				msg(wmsg['addr_in_addrfile_only'].format(mmgenaddr=mmaddr))
				if not keypress_confirm('Continue anyway?'):
					sys.exit(1)
			else:
				die(2,wmsg['addr_not_found'].format(pnm=pnm,mmgenaddr=mmaddr))
		else:
			die(2,wmsg['addr_not_found_no_addrfile'].format(pnm=pnm,mmgenaddr=mmaddr))

	return BTCAddr(btc_addr)

def get_fee_estimate():
	if 'tx_fee' in opt.set_by_user: # TODO
		return None
	else:
		ret = c.estimatefee(opt.tx_confs)
		if ret != -1:
			return BTCAmt(ret)
		else:
			m = """
Fee estimation failed!
Your possible courses of action (from best to worst):
    1) Re-run script with a different '--tx-confs' parameter (now '{c}')
    2) Re-run script with the '--tx-fee' option (specify fee manually)
    3) Accept the global default fee of {f} BTC
Accept the global default fee of {f} BTC?
""".format(c=opt.tx_confs,f=opt.tx_fee).strip()
			if keypress_confirm(m):
				return None
			else:
				die(1,'Exiting at user request')

def txcreate(opt,cmd_args,do_info=False,caller='txcreate'):

	tx = MMGenTX()

	if opt.comment_file: tx.add_comment(opt.comment_file)

	c = bitcoin_connection()

	if not do_info:
		from mmgen.addr import AddrList,AddrData
		addrfiles = [a for a in cmd_args if get_extension(a) == AddrList.ext]
		cmd_args = set(cmd_args) - set(addrfiles)

		ad_f = AddrData()
		for a in addrfiles:
			check_infile(a)
			ad_f.add(AddrList(a))

		ad_w = AddrData(source='tw')

		for a in cmd_args:
			if ',' in a:
				a1,a2 = a.split(',',1)
				if is_btc_addr(a1):
					btc_addr = BTCAddr(a1)
				elif is_mmgen_id(a1):
					btc_addr = mmaddr2baddr(c,a1,ad_w,ad_f)
				else:
					die(2,"%s: unrecognized subargument in argument '%s'" % (a1,a))
				tx.add_output(btc_addr,BTCAmt(a2))
			elif is_mmgen_id(a) or is_btc_addr(a):
				if tx.change_addr:
					die(2,'ERROR: More than one change address specified: %s, %s' %
							(change_addr, a))
				tx.change_addr = mmaddr2baddr(c,a,ad_w,ad_f) if is_mmgen_id(a) else BTCAddr(a)
				tx.add_output(tx.change_addr,BTCAmt('0'))
			else:
				die(2,'%s: unrecognized argument' % a)

		if not tx.outputs:
			die(2,'At least one output must be specified on the command line')

		if opt.tx_fee > tx.max_fee:
			die(2,'Transaction fee too large: %s > %s' % (opt.tx_fee,tx.max_fee))

		fee_estimate = get_fee_estimate()

	tw = MMGenTrackingWallet(minconf=opt.minconf)
	tw.view_and_sort()
	tw.display_total()

	if do_info: sys.exit()

	tx.send_amt = tx.sum_outputs()

	msg('Total amount to spend: %s' % ('Unknown','%s BTC'%tx.send_amt.hl())[bool(tx.send_amt)])

	while True:
		sel_nums = select_unspent(tw.unspent,
				'Enter a range or space-separated list of outputs to spend: ')
		msg('Selected output%s: %s' % (
				('s','')[len(sel_nums)==1],
				' '.join(str(i) for i in sel_nums)
			))
		sel_unspent = [tw.unspent[i-1] for i in sel_nums]

		non_mmaddrs = [i for i in sel_unspent if i.mmid == None]
		if non_mmaddrs and caller != 'txdo':
			msg(wmsg['non_mmgen_inputs'] % ', '.join(set(sorted([a.addr.hl() for a in non_mmaddrs]))))
			if not keypress_confirm('Accept?'):
				continue

		tx.copy_inputs_from_tw(sel_unspent)      # makes tx.inputs

		tx.calculate_size_and_fee(fee_estimate)  # sets tx.size, tx.fee

		change_amt = tx.sum_inputs() - tx.send_amt - tx.fee

		if change_amt >= 0:
			prompt = 'Transaction produces %s BTC in change.  OK?' % change_amt.hl()
			if keypress_confirm(prompt,default_yes=True):
				break
		else:
			msg(wmsg['not_enough_btc'] % change_amt)

	if change_amt > 0:
		change_amt = BTCAmt(change_amt)
		if not tx.change_addr:
			die(2,wmsg['throwaway_change'] % change_amt)
		tx.del_output(tx.change_addr)
		tx.add_output(BTCAddr(tx.change_addr),change_amt)
	elif tx.change_addr:
		msg('Warning: Change address will be unused as transaction produces no change')
		tx.del_output(tx.change_addr)

	if not tx.send_amt:
		tx.send_amt = change_amt

	dmsg('tx: %s' % tx)

	tx.add_comment()   # edits an existing comment
	tx.create_raw(c)   # creates tx.hex, tx.txid
	tx.add_mmaddrs_to_outputs(ad_w,ad_f)
	tx.add_timestamp()
	tx.add_blockcount(c)

	qmsg('Transaction successfully created')

	dmsg('TX (final): %s' % tx)

	tx.view_with_prompt('View decoded transaction?')

	return tx