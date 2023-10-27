
from re import compile
from typing import Optional

from statement_file_processor.data_types.card_number_value import CardNumberValue

MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

class MIME_TYPES:
    PDF_MIME_TYPE = "application/pdf"
    CSV_MIME_TYPE = "application/csv"
    TXT_MIME_TYPE = "application/txt"

#CSV Fields for Bank Record Processor
class CSVFieldsBankRecordProcessor:
    DATE = 'DATE'
    DESC = 'Narration'
    VALUE_DATE = 'Value Dat'
    DEBIT = 'Debit Amount'
    CREDIT =  'Credit Amount'
    REF_NO = 'Chq/Ref Number'
    CLOSING_BAL = 'Closing Balance'


class APIErrors:
    APINFOUND = 'API Not Found'
    INTERROR = "Internal Error While Processing the Request"
    REQUESTERROR = "Request is not correct"

class PDF_STATEMENT_PROCESSOR:
    AMOUNT_LINE_START_REGEX = ['^Amount \(Rs.\)']
    DATE_LINE_START_REGEX = ['^Date$']


class HDFC_CC_STATEMENT_PROCESSOR:
    AMOUNT_LINE_START_REGEX = ['^Amount \(in Rs.\)']
    AMOUNT_LINE_STOP_REGEX = ['Page [d] of [d]','SMS EMI','^Opening Balance$']
    STATEMENT_AMOUNT_LINE_START_REGEX = ['^Opening$']
    STATEMENT_AMOUNT_LINE_STOP_REGEX = ['^Overlimit$']
    DESCRIPTION_LINE_START_REGEX = ['Transaction Description$']
    DESCRIPTION_LINE_STOP_REGEX = ['^Amount \(in Rs.\)$','(^Domestic Transactions$)']
    DESCRIPTION_LINE_NO_MATCH_REGEX = [ '^HARIKRISHNAN$',
                                        '^(\d{2})/(\d{2})/(\d{4})$', 
                                        '^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2})$',
                                        '^([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9]$',
                                        '^([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9] Cr$',
                                        '^Feature Reward$',
                                        '^null$',
                                        '^Points$']
    DATE_LINE_STOP_REGEX = ['^Transaction details from', '^Opening Balance$']
    ACCOUNT_DETAILS_LINE_START_REGEX  = ['^Statement for HDFC Bank Credit Card$']
    ACCOUNT_DETAILS_LINE_STOP_REGEX   = ['^Payment Due Date$']
    ACCOUNT_DETAILS_LINE_MATCH_REGEX  = ['Card No:']

    def process_card_number(line):
        return CardNumberValue().card_number(
            ''.join(line.split('Card No:')[1].split(' ')))
    





class HSBC_CC_STATEMENT_PROCESSOR:
    #TODO: Merge amount line and description line rgexes finally
    AMOUNT_LINE_START_REGEX = [
        "^TRANSACTION DETAILS$",
        "^AMOUNT \( \)",
        "^AMOUNTS \(",
        '^"We request you make timely'
        "^NET OUTSTANDING BALANCE$"
        ]
    AMOUNT_LINE_STOP_REGEX = [
        # "^# International Spends$",
        "^DATE$",
        # "^TOTAL PURCHASE OUTSTANDING$",
        # "^TOTAL CASH OUTSTANDING$",
        # "^CREDIT CARD STATEMENT$",
        "^Opening balance \(",
        "^Your nominated Bank account$",
        "^Minimal payment due \(",
        "^Minimum payment due \(",
        "^Credit limit \("

        ]
    
    AMOUNT_LINE_NO_MATCH_REGEX = ['^(\d{10})$','^([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9] USD$']
    STATEMENT_AMOUNT_LINE_START_REGEX = ['^Opening balance \(']
    STATEMENT_AMOUNT_LINE_STOP_REGEX = ['^ACCOUNT SUMMARY$']
    STATEMENT_AMOUNT_LINE_MATCH_REGEX = ['^`([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9]']
    SERIAL_LINE_START_REGEX = ['^Amount \(in`\)$','^Transaction Details$']
    SERIAL_LINE_STOP_REGEX = ['Page (\d{1}) of (\d{1})']
    SERIAL_LINE_MATCH_REGEX = ['^(\d{10})$']
    DESCRIPTION_LINE_START_REGEX = [
        "^TRANSACTION DETAILS$"
        ]
    DESCRIPTION_LINE_STOP_REGEX = [
        # "^# International Spends$",
        "^DATE$",
        "^TOTAL PURCHASE OUTSTANDING$",
        "^TOTAL BALANCE TRANSFER OUTSTANDING$",
        "^TOTAL CASH OUTSTANDING$",
        "^CREDIT CARD STATEMENT$",
        '^"We request you make timely',
         "^Your nominated Bank account",
         "^Please note that your account balance",
         "^The  Bonus Rewards  program  is  valid"
        ]
    
    DESCRIPTION_LINE_NOT_MATCH_REGEX = [
        "^AMOUNTS \(",
        "^AMOUNT \(",
        "^OPENING BALANCE$",
        "^PURCHASES & INSTALLMENTS$",
        "^Interest Rate applicable :",
        "^\d{2}xx xxxx xxxx \d{4}", # Removing account number/card number
        "^XX XXXX XXXX$",
        "^CASH TRANSACTIONS$",
        # "^TO \d{4} \d{4} \d{4} \d{4}$",
        "^\d\w{2}\s*OF\s*\d?\s*INSTALLMENTS$",#When prointing installments details getting overflow to next line
        "^\d{2}\w{3}$", #Removing dates for eg: 05FEB,10JAN..etc
        ]
    DESCRIPTION_LINE_OVER_FLOW_MATCH_REGEX = [
        "^\d\w{2}\s*OF\s*\d?\s*INSTALLMENTS$"
    ]
    STATEMENT_PERIOD_MATCH_REGEX = [
        "^\d{2}\s\w{3}\s\d{4}\s*To\s\d{2}\s\w{3}\s\d{4}$"
        # 11 APR 2015  To 10 MAY 2015
    ]
    DATE_LINE_START_REGEX = [
        "^DATE$",
        "^TOTAL LOAN OUTSTANDING$",
        # "^Interest Rate applicable"
        ]
    DATE_LINE_STOP_REGEX = [
        # "^TRANSACTION DETAILS$",
        "^NET OUTSTANDING BALANCE$",
        ]
    DATE_LINE_MATCH_REGEX = [
        "^\d{2}\w{3}$"
    ]

    ACCOUNT_NUMBER_LINE_MATCH_REGEX = ["^\d{4}X{8}\d{4}$"]

    def process_statement_year(line):
        #^\d{2}\s\w{3}\s\d{4}\s*To\s\d{2}\s\w{3}\s\d{4}$ --> the last \d{4} corresponds to year
        return line.split(' ')[-1]
    
    def pre_process_date_line(line,year):
        (date,month) = compile("^(\d{2})(\w{3})$").search(line).groups()
        month = MONTHS.index(month) + 1
        return "%s/%s/%s"%(date,month,year)
    
    def pre_process_date_function(year):
        return lambda x: HSBC_CC_STATEMENT_PROCESSOR.pre_process_date_line(x,year)


    # def process_card_number(line):
    #     return CardNumberValue().cardNumber(line)
    
    # statement_amount_pre_process = lambda x: x.replace('`','')
    # serial_number_fetch = lambda x:x


