
import logging
import re
from urllib import request, parse, error

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")

billing_url="https://login.elcat.kg/cgi-bin/clients/"

def  Get_session_id(login, password):
    post_data={ 'action':'validate',
                'language':'ru',
                'login':login,
                'password':password }

    post_data_encoded=parse.urlencode(post_data)
    post_data_encoded=post_data_encoded.encode('ascii')
    req=request.Request(billing_url + "login?language=ru",post_data_encoded)
    try:
        with request.urlopen(req) as response:
            page=response.read()
    except error.HTTPError as e:
        logging.info("HTTP ERROR: %s", e.code)
        return(e.code)
    else:
        try:
            sessid_body=page.decode('ascii')
        except UnicodeDecodeError:
            logging.error("Page decoding error, check supplied credentials")
            return None

    sessid = re.compile('(?<=session_id=)[A-Za-z0-9]+')
    sessid = sessid.search(sessid_body)

    if sessid:
        sessid = sessid.group(0)
        return sessid
    else:
        logging.error("Unable to retreive session_id for %s from page", login)

def Parse_stats(sessid):
    if sessid:
        pass
    else:
        logging.error("Parser got empty session_id")
        return None
    return_dict = {}

    req=request.Request(billing_url + "deal_account?session_id=" + sessid)
    try:
        with request.urlopen(req) as response:
            page=response.read()
    except error.HTTPError as e:
        logging.info("HTTP ERROR: %s", e.code)
    else:
        page=page.decode('Windows-1251')
    

    account_id = re.compile(r'(?<=[ДОГОВОР\s])[0-9]+')
    account_id = account_id.search(page)
    if account_id:
        return_dict['account_id'] = account_id.group(0)
    else:
        logging.error("Unable to retreive account_id for %s", sessid)

    account_name = re.compile(r'Наименование&nbsp;</td>\n\s*<td>&nbsp;([\w\s]*(?=</td))')
    account_name = account_name.search(page)
    if account_name:
        # Regex splits result in enclosed group, real data is there
        return_dict['account_name'] = account_name.group(1)
    else:
        logging.error("Unable to retreive account_name for %s", sessid)

    account_balance = re.compile(r'Сумма на счету&nbsp;</td>\n\s*<td>&nbsp;([\d.]*(?=</td))')
    account_balance = account_balance.search(page)
    if account_balance:
        # Regex splits result in enclosed group, real data is there
        return_dict['account_balance'] = int(float(account_balance.group(1)))
    else:
        logging.error("Unable to retreive account_balance for %s", sessid)

    account_status = re.compile(r'Статус&nbsp;</td>\n\s*<td>&nbsp;(\w+(?=</td))')
    account_status = account_status.search(page)
    if account_status:
        # Regex splits result in enclosed group, real data is there
        return_dict['account_status'] = account_status.group(1)
    else:
        logging.error("Unable to retreive account_status for %s", sessid)

    account_services = re.compile(r'session_id=[\w]*&service_id=\d*">([\d]*(?=</a>))')
    account_services = account_services.findall(page)
    if account_services:
        # Regex creates list of items if got multiple matches
        return_dict['account_services'] = account_services
        return_dict['sessid'] = sessid
        pass
    else:
        logging.error("Unable to retreive account_services for %s", sessid)

    return return_dict

def Get_account_data(login, password):
    # Returns all of the information about specified account in dictionary
    # dict is structured as:
    # {'account_id':'id', 'account_name':'name', 'account_balance':'summ', 'account_status':'status', 'account_services':['phone1','phone2']}
    return Parse_stats(Get_session_id(login, password))

