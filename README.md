# MilkSad_dummy

I have found some interesting notes [[1]](https://milksad.info/) about "fresh" ***weak RNG*** utilization in old and well known Libbitcoin Explorer and decided to try to compose some simple brutforce tool - just in educational perspective.

Read the [article]((https://milksad.info/)) - guys made an amazing job investigating the problem.

In short, there was a popular command line tool to manage the BTC wallets, including such an operations as generating new wallets (seed, private keys,...).

Some version of the program relied on algorithmical random number generator seeded with value taken from system time ***truncated to 32 bits***. 
Again, for being understood right - the program that was advertised as example for being used to generate seeds(private keys) provided the seed (private key) generation using 32 bit ***~~ random number***.

32 bits =~ 4 * E09 --> 4 billion combinations ??

Seems like it could be easily brutted with an efficient code. One could propose here to make an efficient bruteforce - cutting out the code for seed generation looping it with linear search from 0 to 2^32 (or maybe even fake the time - trying all time values). That would be the right way to bruteforce.

Anyway, i considered that we could simply run bx tool multiple times with different system values (just run it over the day) relying on the idea that 32 bit truncation of the system time changing over the day (or month) will smoothly fill the [0, 2^32] interval. So i've composed a simple python script that will run the ***bx*** requesting it to make the private key and dumping it to the file. The script collect private keys till some threshold reached - then it run the [***brainflayer***](https://github.com/ryancdotorg/brainflayer) in order to check if generated private keys hold some non-zero balance.

The script could be found here in the folder "MilkSad_fun" - ***bx_brute.py***. It requires the ***bx-linux-x64-qrcode_3_2*** (i have attached compiled for linux binaries in the same folder that i have took from [here](https://github.com/libbitcoin/libbitcoin-explorer) i guess..), ***brainflayer*** (if have attached sources as zip archive - ***brainflayer.zip***, could be simply unzipped and used as is or recompilled - but better get that from brainflayer github) and ***040823BF.blf*** file for being used with brainflayer - the bloom filter of BTC addresses. 040823BF.blf is too big for being attached in GitHub - so i have uploaded it in free [filehosting](https://file.io/Ctx3Lne61khS), but you could also download the necceser file in [telegram group] (https://t.me/Blockchain_BTC_ETH_DUMPS)

## UPDATE - better brute script
Check the folder MilkSad_v2 - the script ***bx_brute_v2.py***. It requires several files - the list of funded BTC, BCH, LTC, DOGE addresses that generally could be taken in [here](https://t.me/Blockchain_BTC_ETH_DUMPS) or [HERE](https://uploadnow.io/f/csHbfsV) (but this link will soon expire) or msg me. This script will work a bit fast than previous + it will check P2PKH addresses (compressed\uncompressed) and BECH32 addresses (bc1...) for multiple networks (BTC, BCH, LTC, DOGE) and it can be easily extended to other networks of your desire. All databses are holded in RAM during the execution - each thread of the script access same database from RAM. Theese four (BTC, BCH, LTC, DOGE) databases require around 14 GB - 16 GB of RAM and works just fine on my 16 GB RAM Ubuntu machine.

***Remember - stealing is unEthical thing and i do not recommend you to do this. (In contrast to redeeming the Crypto Puzzle revenues - check my other GitHub repositories).
Given ideas and scripts here are purely for education purpose.***

Any ideas\questions or propositions you may send to generalizatorSUB@gmail.com.

## P.S.
Thank you for spending time on my notes, i hope it was not totally useless and you've found something interesting. 

-------------------------------------------------------------------------
### References:
[1] Milk Sad investigation (Vulnerability CVE-2023-39910) - https://milksad.info/

[2] bx (libbitcoin-explorer) - https://github.com/libbitcoin/libbitcoin-explorer
 
[3] BrainFlayer - https://github.com/ryancdotorg/brainflayer

[4] 040823BF.blf - https://file.io/8C5mUAGIqpm7

[4'] Telegram channel with fresh BTC addresses:balances databases - https://t.me/Blockchain_BTC_ETH_DUMPS

-------------------------------------------------------------------------
### Support
I am poor Ukrainian student (evacuated to safe place) that will really appreciate any donations.
 
P.S. Successfully evacuated from occupied regions of Ukraine.

**BTC**:  `1QKjnfVsTT1KXzHgAFUbTy3QbJ2Hgy96WU`

**LTC**:  `LNQopZ7ozXPQtWpCPrS4mGGYRaE8iaj3BE`

**DOGE**: `DQvfzvVyb4tnBpkd3DRUfbwJjgPSjadDTb`
 
 **BSV**: `1E56gGQ1rYG4kkRo5qPLMK7PHcpVYj15Pv`
