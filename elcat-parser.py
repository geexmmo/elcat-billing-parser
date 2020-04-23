import logging
import argparse
import os.path
from include.sqlite_db import Sqlite_inittable, Sqlite_insert, Sqlite_count, Sqlite_select_all
from include.config_parser import Config_parser
from include.billing_parser import Get_account_data
from include.send_notification import RocketChat_send

#   Settings
# SQLite database file name
dbfilename = "./elcat-accounts.sqlite"
# Monthly payment calculated from usd price
usd_price = 81
# Default text field used in config file parsing
defaultuniq = 'fromdomain'
# Rocketchat hook url
Rocketchat_url = "https://url_here"

# logging format
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format,datefmt="%H:%M:%S")

# parsing arguments
parser = argparse.ArgumentParser(description='Parses account data from elcat.kg billing system. \n')
parser.add_argument('--parse_file', metavar='file', help='Parse file to get credentials and add them to database')
parser.add_argument('--parse_uniq', metavar='unique option', help='Unique option in section of a file that will be parsed, sections without it will be ignored.')
parser.add_argument('--create_db', action='store_true', help='Initiates db file, run if you dont have db file.')
parser.add_argument('--add_account', metavar='login', help='Manually add phone account to database.')
parser.add_argument('--name', metavar='name', help='name to add with --add_account')
parser.add_argument('--password', metavar='password', help='password to add with --add_account')

args = parser.parse_args()

def Check_if_creating_database():
# Checking if db file does not exist already so we dont overwrite it by accident
    if args.create_db == True:
        print(args.create_db)
        if os.path.exists(dbfilename) == False:
            logging.info("Creating new db file...")
            Sqlite_inittable(dbfilename)
        else:
            logging.error("Error: Database file already existing")
            exit(0)
    else:
        if os.path.exists(dbfilename) == False: 
            logging.info("No database file existing and none will be created (--create_db not specified)")
            exit(0)

def Check_if_adding_account():
# Checking if add_account data is specified, that means we need to add new account to database
    if args.add_account != None:
        if args.password != None:
            if args.name != None:
                logging.info("Adding account %s, number: %s @ %s", args.name, args.add_account, args.password)
                Sqlite_insert(dbfilename, args.name, args.add_account, args.password)
            else:
                logging.warn("Adding account with no name! number: %s @ %s", args.add_account, args.password)
                Sqlite_insert(dbfilename, 'no name', args.add_account, args.password)
        else:
            logging.error("Error: --password should be specified when adding new account")
            exit(0)

def Check_if_parsing_files():
# Checking if accounts_from_file data is specified
    if args.parse_file != None:
        if args.parse_uniq != None:
            dic=Config_parser(args.parse_file, args.parse_uniq)
            logging.info("Parsing done, found %s accounts with keyword %s", len(dic), args.parse_uniq)
            for i in dic.keys():
                 Sqlite_insert(dbfilename, i,dic.get(i)[0],dic.get(i)[1])
            exit(0)
        else:
            logging.info("Parsing, unique keyword defaulted to 'fromdomain'.")
            dic=Config_parser(args.parse_file, defaultuniq)
            logging.info("Parsing done, found %s accounts", len(dic))
            for i in dic.keys():
                 Sqlite_insert(dbfilename, i,dic.get(i)[0],dic.get(i)[1])
            exit(0)
    else:
        if args.create_db == False and args.add_account == None: logging.info("No flags specified, running checks on accounts that are already in database.")


Check_if_creating_database()
Check_if_adding_account()
Check_if_parsing_files()

number_in_db=Sqlite_count(dbfilename)
if number_in_db < 1:
    logging.info("Numbers in database: %s, nothing to do.", number_in_db)
    exit(0)
else: pass

logging.info("%s numbers is database.", number_in_db)

final_data = {0 : {'account_internal_name':'',
                     'account_id':'',
                     'account_name':'',
                     'account_balance':'',
                     'account_status':'',
                     'account_services':['']}
             }

accounts_dir=Sqlite_select_all(dbfilename)
counter=0

for i in accounts_dir:
    account_data=Get_account_data(i[2], i[3])
    
    # Check there is duplicate number in account, array creation will be skipped ( so only unique accounts will be processed further )
    for v in final_data:
        if final_data[v]['account_id'] == account_data['account_id']:
            dups=bool(True)
            break
        else: 
            dups=bool(False)

    if dups == False:
        final_data[counter] = {}
        final_data[counter]['account_internal_name'] = i[1]
        final_data[counter]['account_id'] = account_data['account_id']
        final_data[counter]['account_name'] = account_data['account_name']
        final_data[counter]['account_balance'] = account_data['account_balance']
        final_data[counter]['account_status'] = account_data['account_status']
        final_data[counter]['account_services'] = account_data['account_services']
        final_data[counter]['sessid'] = account_data['sessid']
        counter += 1
    else:
        pass

RocketChat_send(Rocketchat_url, final_data, usd_price)