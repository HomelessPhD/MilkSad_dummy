import os
from itertools import repeat
from threading import Thread
from threading import Event
import time

import codecs
import hashlib
import base58
import ecdsa
import gc

from segwit_addr import encode as P2WPKH_encode

from datetime import datetime
def log_str(logfile_name, string_to_log):
    with open(logfile_name, 'a') as f:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f.write(dt_string+': '+string_to_log+'\n')

logfile_name = 'LOG_milking.log'

def pubKey_to_p2pkhAddress(public_key, networks_bytes = [b'00']):
            # Compute the hash: public key bytes -> sha256 -> RIPEMD160
    public_key_bytes = codecs.decode(public_key, 'hex')
            # Run SHA256 for the public key
    sha256_bpk = hashlib.sha256(public_key_bytes)
    sha256_bpk_digest = sha256_bpk.digest()
            # Run ripemd160 for the SHA256
    ripemd160_bpk = hashlib.new('ripemd160')
    ripemd160_bpk.update(sha256_bpk_digest)
    ripemd160_bpk_digest = ripemd160_bpk.digest()
    ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
    
        # process ripemd160 - for all networks
    address_list = []
    for network_byte in networks_bytes:
                # Add network byte
        network_bitcoin_public_key = network_byte +  ripemd160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key, 'hex')
                # Double SHA256 to get checksum
        sha256_nbpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_nbpk_digest = sha256_nbpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_nbpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_2_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
        checksum = sha256_2_hex[:8]
                # Concatenate public key and checksum to get the address
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
        address = base58.b58encode(bytes(bytearray.fromhex(address_hex))).decode('utf-8')  
          
        address_list.append(address)
    return address_list, ripemd160_bpk_hex

def pk_to_addresses(priv_key, networks_bytes = [b'00'], networks_HRPs = ['bc']): 
    private_key_bytes = codecs.decode(priv_key, 'hex')
        # Get ECDSA public key (paired to given private key)
    key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
    key_bytes = key.to_string()
    
            # -------UNCOMPRESSED P2PKH address--------
    key_hex = codecs.encode(key_bytes, 'hex')
        # Add bitcoin byte '04' that denote UNCOMPRESSED public key
    bitcoin_byte = b'04'
    public_key = bitcoin_byte + key_hex
    P2PKH_unc_addr_list,_ = pubKey_to_p2pkhAddress(public_key, networks_bytes)
    
            # -----COMPRESSED P2PKH address -------------
    if key_bytes[-1] & 1:
        bitcoin_byte = b'03'
    else:
        bitcoin_byte = b'02' 
    key_hex = codecs.encode(key_bytes[0:32], 'hex')
    public_key = bitcoin_byte + key_hex    
    P2PKH_c_addr_list, ripemd160_bpk_hex = pubKey_to_p2pkhAddress(public_key, networks_bytes)    

            # -----P2WPKH address -------------
    P2WPKH_addr_list = []
    for hrp in networks_HRPs:
        P2WPKH_addr_list.append( P2WPKH_encode(hrp, 0, [int(ripemd160_bpk_hex[2*n:2*(n+1)], 16) for n in range(0,20)]) )
         
    return (P2PKH_unc_addr_list, P2PKH_c_addr_list, P2WPKH_addr_list)


def load_address_balance_set(filename, label='COIN'):
        # Download the BTC,LTC,... addresses database (funded addresses)
    print(f'Download the {label} balances database....\n')
    num_lines = 0
    with open(filename, 'r') as fp:
        num_lines = sum(1 for line in fp)
    
    count = 0
    COIN_set = set()
    with open(filename, 'r') as fp:
        while True:
            count += 1
        
            address_line = fp.readline()  
        
            if not  address_line:
                break       
            addr_bal =  address_line.rstrip('\n').strip(' ').split('\t')
            #BTC_dictionary[addr_bal[0]] = addr_bal[1]
            COIN_set.add(addr_bal[0])
        
            if((count % 1000000) == 0):
                print(f'{round(100*(count/num_lines),2)} %')
                gc.collect()
        print(f'{round(100*(count/num_lines),2)} %')
    gc.collect()

    #COIN_dictionary = {}
    #with open('bitcoin_addresses_and_balance_04.08.23.txt', 'r') as fp:
    #    address_lines = fp.readlines()    
    #    COIN_dictionary = { al.rstrip('\n').strip(' ').split('\t')[0]:al.rstrip('\n').strip(' ').split('\t')[1] for al in address_lines}            
    print(f'{label} balance database loaded and prepared to use\n')
    
    return COIN_set


def t_job(t_id, T_off_ev, funded_addrs_sets):
    pk_list = []
    for _ in repeat(0):
        failsafe_file_closing_flag = 1
        start = time.time()
        
        log_str(logfile_name, f'{t_id} Initiate priv-key generation \ verification')
        for k in range(0, 10):
            out_s = os.popen("for i in `seq 1 1 1000`; do ./bx-linux-x64-qrcode_3_2 seed | ./bx-linux-x64-qrcode_3_2 ec-new; done").read()
            pk_list.extend(out_s.split('\n')[:-1])
                
            with open('failsafe_MILK.txt', 'r') as f:
                failsafe_file_closing_flag = int(next(f))
                if failsafe_file_closing_flag:
                    break

            if T_off_ev.is_set():
                break
            
        for pk in pk_list:
            address_unc, address_c, address_p2wpkh = pk_to_addresses(pk, networks_bytes = [b'00', b'30',b'1e'], networks_HRPs = ['bc','ltc','bc'])
            
            idx = (0,0, 1, 2)
            labels = ('BTC','BCH','LTC','DOGE')
            for li in range(0, len(labels)):
                if address_unc[idx[li]] in funded_addrs_sets[labels[li]]:
                    log_str(logfile_name,          f"{t_id} FOUND SMTH. {address_unc[idx[li]]}: {pk} | UNcompressed  | {labels[li]}")
                    log_str('LOG_brainflayer_{t_id}.txt', f"FOUND SMTH. {address_unc[idx[li]]}: {pk} | UNcompressed  | {labels[li]}")
                if address_c[idx[li]] in funded_addrs_sets[labels[li]]:
                    log_str(logfile_name,          f"{t_id} FOUND SMTH. {address_c[idx[li]]}: {pk} | compressed  | {labels[li]}")
                    log_str('LOG_brainflayer_{t_id}.txt', f"FOUND SMTH. {address_c[idx[li]]}: {pk} | compressed  | {labels[li]}")         
                if address_p2wpkh[idx[li]] in funded_addrs_sets[labels[li]]:
                    log_str(logfile_name,          f"{t_id} FOUND SMTH. {address_p2wpkh[idx[li]]}: {pk} | P2WPKH  | {labels[li]}")
                    log_str('LOG_brainflayer_{t_id}.txt', f"FOUND SMTH. {address_p2wpkh[idx[li]]}: {pk} | P2WPKH  | {labels[li]}") 
                

        end = time.time()
        log_str(logfile_name, f'{t_id} ........ priv-key generation \ verification... {round(len(pk_list) / (end-start), 2)} keys/s, {len(pk_list)} keys DONE') 
        pk_list.clear()
        
        if failsafe_file_closing_flag:        
            log_str(logfile_name, f'{t_id} Finishing by failsafe')
            break
        if T_off_ev.is_set():        
            log_str(logfile_name, f'{t_id} Finishing by event')
            break

BTC_set = load_address_balance_set('bitcoin_addresses_and_balance_22.08.23.txt', label='BTC')
BCH_set = load_address_balance_set('bitcoin_cash_addresses_and_balance_16.08.23.txt', label='BCH')
LTC_set = load_address_balance_set('litecoin_addresses_and_balance_15.08.23.txt',label='LTC')
DOGE_set = load_address_balance_set('dogecoin_addresses_and_balance_15.08.23.txt',label='DOGE')

t_num = 4

t = [0] * t_num
T_off_ev = Event()
T_off_ev.clear()
with open('failsafe_MILK.txt', 'w') as f:
    f.write('%d' % 0)
    
for i in range(t_num):
    t[i] = Thread(target = t_job, args=(i, T_off_ev, {'BTC':BTC_set,'BCH':BCH_set, 'LTC':LTC_set, 'DOGE':DOGE_set} ))
    t[i].start()
    time.sleep(10)
    
cmd = ''
while cmd != 'exit':
    cmd = input("Enter exit to finish...")

print('Main stopping threads')
T_off_ev.set()

for i in range(t_num):
    t[i].join()
