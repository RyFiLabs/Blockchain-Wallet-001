{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2625bb6d-020b-434f-847e-370679a31c44",
   "metadata": {},
   "outputs": [],
   "source": [
    "75 lines (62 sloc)  2.58 KB\n",
    "   \n",
    "import subprocess\n",
    "import json\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bd6add65-93d0-4dce-b2d3-e4ab5add4052",
   "metadata": {},
   "outputs": [],
   "source": [
    "from constants import BTC, BTCTEST, ETH\n",
    "from pprint import pprint"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "734bcafc-b618-493e-a0dd-f41ec3bfd68d",
   "metadata": {},
   "outputs": [],
   "source": [
    "from bit import PrivateKeyTestnet\n",
    "from bit.network import NetworkAPI"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f5442006-cd0f-4dda-ba68-58dd48e22072",
   "metadata": {},
   "outputs": [],
   "source": [
    "from web3 import Web3, middleware, Account\n",
    "from web3.gas_strategies.time_based import medium_gas_price_strategy\n",
    "from web3.middleware import geth_poa_middleware"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "745ec338-639a-4e4d-a8a5-356f21d64553",
   "metadata": {},
   "outputs": [],
   "source": [
    "# connect Web3\n",
    "w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER', 'http://localhost:8545')))\n",
    "\n",
    "# enable PoA middleware\n",
    "w3.middleware_stack.inject(geth_poa_middleware, layer=0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5442a4e2-408c-444f-8567-3119797c9109",
   "metadata": {},
   "outputs": [],
   "source": [
    "# set gas price strategy to built-in \"medium\" algorithm (est ~5min per tx)\n",
    "# see https://web3py.readthedocs.io/en/stable/gas_price.html?highlight=gas\n",
    "# see https://ethgasstation.info/ API for a more accurate strategy\n",
    "w3.eth.setGasPriceStrategy(medium_gas_price_strategy)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "71c4f635-ae42-41d5-9a8c-5a0a53cb78f5",
   "metadata": {},
   "outputs": [],
   "source": [
    "# including a mnemonic with prefunded test tokens for testing\n",
    "mnemonic = os.getenv(\"MNEMONIC\", \"later trouble diary worry divide quantum shift term pepper glass gown rotate\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "39a7a624-5020-4f31-b6ed-b27eeeffe7ae",
   "metadata": {},
   "outputs": [],
   "source": [
    "def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):\n",
    "    p = subprocess.Popen(\n",
    "        f\"./derive -g --mnemonic='{mnemonic}' --coin={coin} --numderive={depth} --format=json\",\n",
    "        stdout=subprocess.PIPE,\n",
    "        shell=True)\n",
    "    (output, err) = p.communicate()\n",
    "    p_status = p.wait()\n",
    "    return json.loads(output)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "13ec7059-44c8-4740-9759-88fd32fa9223",
   "metadata": {},
   "outputs": [],
   "source": [
    "def priv_key_to_account(coin, priv_key):\n",
    "    if coin == ETH:\n",
    "        return Account.privateKeyToAccount(priv_key)\n",
    "    if coin == BTCTEST:\n",
    "        return PrivateKeyTestnet(priv_key)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "34a3afd8-d77c-443a-925d-132b984f8636",
   "metadata": {},
   "outputs": [],
   "source": [
    "def create_tx(coin, account, to, amount):\n",
    "    if coin == ETH:\n",
    "        value = w3.toWei(amount, \"ether\") # convert 1.2 ETH to 120000000000 wei\n",
    "        gasEstimate = w3.eth.estimateGas({ \"to\": to, \"from\": account.address, \"amount\": value })\n",
    "        return {\n",
    "            \"to\": to,\n",
    "            \"from\": account.address,\n",
    "            \"value\": value,\n",
    "            \"gas\": gasEstimate,\n",
    "            \"gasPrice\": w3.eth.generateGasPrice(),\n",
    "            \"nonce\": w3.eth.getTransactionCount(account.address),\n",
    "            \"chainId\": w3.net.chainId\n",
    "        }\n",
    "    if coin == BTCTEST:\n",
    "        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ceb5daea-500f-4b71-a196-654bcea60e26",
   "metadata": {},
   "outputs": [],
   "source": [
    "def send_tx(coin, account, to, amount):\n",
    "    if coin == ETH:\n",
    "        raw_tx = create_tx(coin, account, to, amount)\n",
    "        signed = account.signTransaction(raw_tx)\n",
    "        return w3.eth.sendRawTransaction(signed.rawTransaction)\n",
    "    if coin == BTCTEST:\n",
    "        raw_tx = create_tx(coin, account, to, amount)\n",
    "        signed = account.sign_transaction(raw_tx)\n",
    "        return NetworkAPI.broadcast_tx_testnet(signed)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "03259031-300e-4b3d-b27f-916282b6b537",
   "metadata": {},
   "outputs": [],
   "source": [
    "coins = {\n",
    "    ETH: derive_wallets(coin=ETH),\n",
    "    BTCTEST: derive_wallets(coin=BTCTEST),\n",
    "}\n",
    "\n",
    "pprint(coins)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7ac2c7b6-11b1-4dd7-a8af-c55da75956f8",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
