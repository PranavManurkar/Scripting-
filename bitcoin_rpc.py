from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time
rpc_user = "gammacrew"
rpc_password = "1234"
rpc_port = 18443
rpc_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}"
rpc = AuthServiceProxy(rpc_url)

wallet_name = "gammacrew_wallet"
try:
    rpc.loadwallet(wallet_name)
    print(f"Loaded wallet: {wallet_name}")
except JSONRPCException:
    rpc.createwallet(wallet_name)
    print(f"Created new wallet: {wallet_name}")

print(rpc.getbalance())
if rpc.getbalance() < 1:
    default_addr = rpc.getnewaddress()
    rpc.generatetoaddress(101, default_addr)
    print("Mined 101 blocks to fund the wallet")


address_A = rpc.getnewaddress("Address_A", "legacy")
address_B = rpc.getnewaddress("Address_B", "legacy")
address_C = rpc.getnewaddress("Address_C", "legacy")
print("\nGenerated legacy addresses:")
print("  Address A:", address_A)
print("  Address B:", address_B)
print("  Address C:", address_C)

txid_fund_A = rpc.sendtoaddress(address_A, 6.0)
print("\nSent 10 BTC to Address A. Funding txid:", txid_fund_A)

rpc.generatetoaddress(1, address_A)
time.sleep(1)

utxos_A = rpc.listunspent(1, 9999999, [address_A])
if not utxos_A:
    print("No UTXO found for Address A. Exiting.")
    exit(1)


utxo_A = utxos_A[0]
input_txid = utxo_A["txid"]
input_vout = utxo_A["vout"]
input_amount = utxo_A["amount"]

send_amount = 1.0    
fee = 0.0001         
change_amount = float(input_amount) - send_amount - fee
if change_amount < 0:
    print("Insufficient funds in selected UTXO.")
    exit(1)
inputs = [{"txid": input_txid, "vout": input_vout}]
outputs = {address_B: send_amount}
if change_amount > 0:
    outputs[address_A] = change_amount

raw_tx_A_B = rpc.createrawtransaction(inputs, outputs)
print("\nCreated raw transaction for A->B.")
signed_tx_A_B = rpc.signrawtransactionwithwallet(raw_tx_A_B)
if not signed_tx_A_B.get("complete"):
    print("Error signing the transaction from A to B!")
    exit(1)

txid_A_B = rpc.sendrawtransaction(signed_tx_A_B["hex"])
print("Broadcasted transaction from A to B. txid:", txid_A_B)

rpc.generatetoaddress(1, address_A)
time.sleep(1)
decoded_tx_A_B = rpc.decoderawtransaction(signed_tx_A_B["hex"])
scriptPubKey_B = None
for vout in decoded_tx_A_B["vout"]:
    if address_B in vout["scriptPubKey"].get("address", []):
        scriptPubKey_B = vout["scriptPubKey"]["hex"]
        break

if scriptPubKey_B:
    print("Decoded ScriptPubKey for Address B (challenge script):", scriptPubKey_B)
else:
    print("Could not locate ScriptPubKey for Address B in transaction A->B.")
utxos_B = rpc.listunspent(1, 9999999, [address_B])
if not utxos_B:
    print("No UTXOs found for Address B. Exiting.")
    exit(1)

utxo_B = utxos_B[0]
input_txid_B = utxo_B["txid"]
input_vout_B = utxo_B["vout"]
input_amount_B = utxo_B["amount"]
send_amount_B = 0.9  
fee_B = 0.0001
change_amount_B = float(input_amount_B) - send_amount_B - fee_B
print("changeamt: ", change_amount_B)
if change_amount_B < 0:
    print("Insufficient funds in selected UTXO for transaction B->C")
    exit(1)

inputs_B = [{"txid": input_txid_B, "vout": input_vout_B}]
outputs_B = {address_C: send_amount_B}
if change_amount_B > 0:
    outputs_B[address_B] = round(change_amount_B, 8)

raw_tx_B_C = rpc.createrawtransaction(inputs_B, outputs_B)
print("\nCreated raw transaction for B->C.")

signed_tx_B_C = rpc.signrawtransactionwithwallet(raw_tx_B_C)
if not signed_tx_B_C.get("complete"):
    print("Error signing the transaction from B to C!")
    exit(1)

txid_B_C = rpc.sendrawtransaction(signed_tx_B_C["hex"])
print("Broadcasted transaction from B to C. txid:", txid_B_C)
rpc.generatetoaddress(1, address_B)
time.sleep(1)

decoded_tx_B_C = rpc.decoderawtransaction(signed_tx_B_C["hex"])
scriptSig_B = decoded_tx_B_C["vin"][0]["scriptSig"]["hex"]
