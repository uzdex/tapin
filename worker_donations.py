import yaml
from pprint import pprint
import sys
import json
from bitshares import BitShares
from bitshares.account import Account
from bitshares.blockchain import Blockchain
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

config = yaml.load(open("config.yml").read())
log = logging.getLogger(__name__)

# Logging
log_handler_mail = SMTPHandler(config["mail_host"].split(":"),
                               config["mail_from"],
                               config["admins"],
                               '[faucet] Donation Error',
                               (config["mail_user"],
                                config["mail_pass"]))
log_handler_mail.setFormatter(logging.Formatter(
    "Message type:       %(levelname)s\n" +
    "Location:           %(pathname)s:%(lineno)d\n" +
    "Module:             %(module)s\n" +
    "Function:           %(funcName)s\n" +
    "Time:               %(asctime)s\n" +
    "\n" +
    "Message:\n" +
    "\n" +
    "%(message)s\n"
))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler_mail.setLevel(logging.WARN)
log_handler_stdout = logging.StreamHandler(sys.stdout)
log_handler_stdout.setFormatter(formatter)
log.addHandler(log_handler_mail)
log.addHandler(log_handler_stdout)

from graphenebase.base58 import known_prefixes
from bitsharesbase.chains import known_chains

known_prefixes.append('UZDE')
known_chains['UZDE'] = {}
known_chains['UZDE']['core_symbol'] = 'UZDE'
known_chains['UZDE']['prefix'] = 'UZDE'
known_chains['UZDE']['chain_id'] = 'd04cbbace494915fe0d78e49ae9bb65fc79ca8b6d4f8c26b1b973a230b2d1e73'

bitshares = BitShares(
    config["witness_url"],
    keys=[config["wif"]],
    nobroadcast=False
)


def run(begin=None, end=None):

    blockchain = Blockchain(
        mode="head",
        bitshares_instance=bitshares
    )

    for op in blockchain.stream(
        opNames=["account_create"],
        start=int(begin) if begin else None,
        stop=int(end) if end else None,
    ):
        blockid = op.get("block_num")
        timestamp = op.get("timestamp")

        if not blockid % 100:
            print("Blockid: %d (%s)" % (blockid, timestamp), flush=True)

        try:
            pprint(bitshares.transfer(
                op["name"],
                config["donation_amount"], config["donation_asset"],
                account=config["registrar"]
            ))
        except Exception as e:
            log.error(str(e))
            pass


if __name__ == '__main__':
    run()
