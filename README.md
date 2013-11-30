#  mmgen = Multi-Mode GENerator
## a Bitcoin cold storage solution for the command line

NOTE: For the time being, MMGen should be considered Alpha software.
Downloading and testing it out is easy, risk-free and encouraged.
However, spending significant amounts of BTC into your mmgen-generated
addresses is done at your own risk.

### Features:

> As with all deterministic wallets, mmgen can generate an unlimited number
> of address/key pairs from a single seed.  You back up your wallet only once.

> With MMGen you can choose from four different ways to access your Bitcoins:

>> 1) an encrypted wallet (the AES 256 key is generated from your
>> password using the crack-resistant scrypt hash function.  The
>> wallet's password and hash strength can be changed);

>> 2) a short, human-readable seed file (unencrypted);

>> 3) an Electrum-like mnemonic of 12, 18 or 24 words; or

>> 4) a brainwallet password (recommended for expert users only).

> Furthermore, these methods can all be combined.  If you forget your
> mnemonic, for example, you can regenerate it and your keys from a
> stored wallet or seed.  Correspondingly, a lost wallet or seed can be
> recovered from the mnemonic.

> The wallet and seed are short, simple text files suitable for printing
> or even writing out by hand.  Built-in checksums are used to verify
> they've been correctly copied.  The base-58-encoded seed is short
> enough to memorize, providing another brain storage alternative.

> Implemented as a suite of lightweight python scripts with a
> command-line interface, MMGen demands practically no system resources.
> Yet in tandem with a bitcoind enabled for watch-only addresses
> (see below), it provides a complete solution for securely
> storing Bitcoins offline and tracking and spending them online.


### Instructions for Linux/Unix:

### Download/Install:
>  Install the ecdsa, scrypt and pycrypto modules:

            sudo pip install ecdsa scrypt pycrypto

>  Install mmgen:

            git clone https://github.com/mmgen/mmgen.git
            cd mmgen; sudo ./setup.py install

>  Install vanitygen (optional but recommended):

            git clone https://github.com/samr7/vanitygen.git
            (build and put the 'keyconv' executable in your path)

### Getting Started:
> On your offline computer:

> Generate a wallet with a random seed:

            $ mmgen-walletgen
            ...
            Wallet saved to file '89ABCDEF-76543210[256,3].dat'

> "89ABCDEF" is the Seed ID; "76543210" is the Key ID.  These are
> randomly generated, so your IDs will naturally be different than the
> fictitious ones used in this example.

> The Seed ID never changes and will be used to identify all
> keys/addresses generated by this wallet.  The Key ID changes when the
> wallet's password or hash preset are changed.

> "256" is the seed length; "3" is the scrypt hash preset.  These are
> configurable.


> Generate ten addresses with the wallet:

            $ mmgen-addrgen 89ABCDEF-76543210[256,3].dat 1-10
            ...
            Address data saved to file '89ABCDEF[1-10].addrs'


> Note that the address range, "1-10", is included in the resulting filename.

            $ cat '89ABCDEF[1-10].addrs'
            89ABCDEF {
              1     16bNmyYISiptuvJG3X7MPwiiS4HYvD7ksE
              2     1AmkUxrfy5dMrfmeYwTxLxfIswUCcpeysc
              3     1HgYCsfqYzIg7LVVfDTp7gYJocJEiDAy6N
              4     14Tu3z1tiexXDonNsFIkvzqutE5E3pTK8s
              5     1PeI55vtp2bX2uKDkAAR2c6ekHNYe4Hcq7
              6     1FEqfEsSILwXPfMvVvVuUovzTaaST62Mnf
              7     1LTTzuhMqPLwQ4IGCwwugny6ZMtUQJSJ1
              8     1F9495H8EJLb54wirgZkVgI47SP7M2RQWv
              9     1JbrCyt7BdxRE9GX1N7GiEct8UnIjPmpYd
              10    1H7vVTk4ejUbQXw45I6g5qvPBSe9bsjDqh
            }


> To store your Bitcoins, spend them into these addresses from whatever
> wallets/software you're currently using.  If you have lots of BTC,
> generate many addresses so that each address will have only a
> relatively small balance.

### Spending your stored coins:
> Take address 1 out of cold storage by generating a key for it:

            $ mmgen-keygen 89ABCDEF-76543210[256,3].dat 1
            ...
            Key data saved to file '89ABCDEF[1].akeys'

            $ cat 89ABCDEF[1].akeys
            89ABCDEF {
              1  sec:  5JCAfK1pjRoJgmpmd2HEMNwHxAzprGIXeQt8dz5qt3iLvU2KCbS
                 addr: 16bNmyYISiptuvJG3X7MPwiiS4HYvD7ksE
            }

> Save the .akeys file to a USB stick and transfer it to your online computer.

> On your online computer, import the secret key into a running bitcoind
> or bitcoin-qt:

            $ bitcoind importprivkey 5JCAfK1pjRoJgmpmd2HEMNwHxAzprGIXeQt8dz5qt3iLvU2KCbS

> You're done!  This address' balance can now be spent.

> OPTIONAL: To track balances without exposing secret keys on your
> online computer, download and compile sipa's bitcoind patched for
> watch-only addresses:

	        $ git clone https://github.com/sipa/bitcoin
            $ git branch mywatchonly remotes/origin/watchonly
            $ git checkout mywatchonly
            (build, install)

> With your newly-compiled bitcoind running, import the addresses from
> '89ABCDEF[1-10].addrs' to track their balances:

            $ bitcoind importaddress 16bNmyYISiptuvJG3X7MPwiiS4HYvD7ksE
            $ bitcoind importaddress 1AmkUxrfy5dMrfmeYwTxLxfIswUCcpeysc
            $ ...

### Using the mnemonic and seed features:

> Using our example above,

> Generate a mnemonic from the wallet:

            $ mmgen-walletchk -m '89ABCDEF-76543210[256,3].dat'
            ...
            Mnemonic data saved to file '89ABCDEF.words'

            $ cat 89ABCDEF.words
            pleasure tumble spider laughter many stumble secret bother
            after search float absent path strong curtain savior
            worst suspend bright touch away dirty measure thorn

> Note: a 128- or 192-bit seed will generate a shorter mnemonic of 12 or
> 18 words.  You may generate a wallet with a these seed lengths by
> using the `-l` option of `mmgen-walletgen`.  Whether you consider
> 128 bits of entropy enough is your call.  It's probably adequate for
> the foreseeable future.

> Generate addresses 1-11 using the mnemonic instead of the wallet:

            $ mmgen-addrgen -m 89ABCDEF.words 1-11
            ...
            Address data saved to file '89ABCDEF[1-11].addrs'

> Compare the first ten addresses with those earlier generated from the
> wallet.  You'll see they're the same.

> Recover a lost wallet using the mnemonic:

            $ mmgen-walletgen -m 89ABCDEF.words
            ...
            Wallet saved to file '89ABCDEF-01234567[256,3].dat'

> Note that the regenerated wallet has a different Key ID but
> of course the same Seed ID.

> Seeds are generated and input the same way as mnemonics.  Just change
> the `-m` option to `-s` in the preceding commands.

> A seed file for a 256-bit seed looks like this:

            $ cat 8B7392ED.mmseed
            f4c84b C5ZT wWpT Jsoi wRVw 2dm9 Aftd WLb8 FggQ eC8h Szjd da9L

> And for a 128-bit seed:

            $ cat 8E0DFB78.mmseed
            0fe02f XnyC NfPH piuW dQ2d nM47 VU

> The latter is short enough to be memorized or written down.

> The first word in the seed file is a checksum.
> To check that you've written or memorized the seed correctly (should
> you choose to do so), compare it with the first 6 characters of a
> sha256 hash of the remainder of the line (with spaces removed).

#### Mnemonics and seeds — additional information:
> Mnemonic and seed data may be entered at a prompt instead of from a
> file.  Just omit the filename on the command line.

> Mnemonic and seed data may be printed to standard output instead of a
> file using the `-S` option of `mmgen-walletchk`.

> Mnemonic and seed files may be output to a directory of your choice
> using the `-d` option of `mmgen-walletchk`.

> Bear in mind that mnemonic and seed data is unencrypted.  If it's
> compromised, your Bitcoins can easily be stolen.  Make sure no one's
> looking over your shoulder when you print mnemonic or seed data to
> screen.  Securely delete your mnemonic and seed files.  In Linux, you
> can achieve additional security by writing the files to volatile
> memory in '/dev/shm' instead of disk.

### Vanitygen note:
> When available, the 'keyconv' utility from the vanitygen package is
> used to generate addresses as it's much faster than the python ecdsa
> library.

### Test suite:
> To see what tests are available, run the scripts in the 'tests'
> directory with no arguments.  Some may find the following tests
> interesting:

>> Compare 10 addresses generated by 'keyconv' with internally-generated ones:
>>> `tests/bitcoin.py keyconv_compare_randloop 10`

>> Perform 1000 hex -> base58 -> hex conversions, comparing results stringwise:
>>> `tests/bitcoin.py hextob58_pad_randloop 1000`

>> Generate a 12-word mnemonic for a random 128-bit seed:
>>> `tests/mnemonic.py random128`

>> Ditto, for a random 192-bit seed:
>>> `tests/mnemonic.py random192`

>> Ditto, for a random 256-bit seed:
>>> `tests/mnemonic.py random256`
