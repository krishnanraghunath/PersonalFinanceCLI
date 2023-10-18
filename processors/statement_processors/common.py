from PersonalFinanceCLI.models.transactions.CardNumberValue import CardNumberValue
from re import compile

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

class KOTAK_CC_STATEMENT_PROCESSOR:
    AMOUNT_LINE_START_REGEX = ['^Amount \(Rs.\)']
    AMOUNT_LINE_STOP_REGEX = ['Page [d] of [d]','SMS EMI']
    AMOUNT_LINE_MATCH_REGEX = ['^([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9]']
    DESCRIPTION_LINE_START_REGEX = ['^Transaction details from']
    DESCRIPTION_LINE_STOP_REGEX = [
                            '^Total Purchase \& Other Charges$',
                            '^Spends Area$',
                            '^CRN: [0-9]+$']
    DESCRIPTION_LINE_NO_MATCH_REGEX = [
                        '^(^Primary Card Transactions-)',
                        '^(^Retail Purchases and Cash Transactions)',
                        '^(^IN)$',
                        '^(^BANGALORE)$',
                        '^(^Bengaluru)$',
                        '^(^MUMBAI)$',
                        '^(^MYSORE)$',
                        '^(^BANGALORE IN)$',
                        '^(^BENGALURU IN)$',
                        '^(^MALAPPURAM IN)$',
                        '^(^DEVASANDRA IN)$',
                        '^(^PALAKKAD)$',
                        '^(^THRISSUR)$',
                        '^KANNUR$',
                        '^COCHIN$',
                        '^WWW[.]MOBIKWIK[.] IN',
                        '^[0-9]{2}-[\w]+-[2][0-9]{3}$',
                        '^\([0-9]+[.][0-9]{2}[ ][A-Z]{3}\)$',
                        '^(^Other Fees and Charges)$',
                        '^(^EMI and Loans)$',
                        '^(^Payments and Other Credits)$',
                        # 'Convert to EMI\)$',
                        '^IN \(.Convert to EMI\)$',
                        '^BANGALORE IN \(.Convert to EMI\)$',
                        '^My Rewards$',
                        '^Opening Balance$',
                        '^Earned this month$',
                        '^Redeemed this month$',
                        '^Expired this month$',
                        '^Expiring next month$',
                        '^Closing Balance$',
                        '^[+-]?([0-9]+\.?[0-9]*|\.[0-9]+)$'
                        ]
    DATE_LINE_START_REGEX = ['^Date$']
    DATE_LINE_STOP_REGEX =  ['^Transaction details from']
    ACCOUNT_DETAILS_LINE_START_REGEX  = ['^Total Credit Limit$']
    ACCOUNT_DETAILS_LINE_STOP_REGEX   = ['^Retail Purchases and Cash Transactions$']
    ACCOUNT_DETAILS_LINE_MATCH_REGEX  = ['^Primary Card Transactions-']

    def process_card_number(line):
        try:
            return CardNumberValue().cardNumber(line.split(' ')[-1])
        except:
            return None


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
        return CardNumberValue().cardNumber(
            ''.join(line.split('Card No:')[1].split(' ')))
    
class ICICI_CC_STATEMENT_PROCESSOR:
    AMOUNT_LINE_START_REGEX = [
        'International Spends$',
        'Transaction Details',
        "^State Code: \d{2}$",
        ]
    AMOUNT_LINE_STOP_REGEX = [
        'Earned',
        '^No. of Installments$',
        'Page (\d{1}) of (\d{1})',
         "^For ICICI Bank Limited"]
    AMOUNT_LINE_NO_MATCH_REGEX = ['^(\d{10})$','^([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9] USD$']
    STATEMENT_AMOUNT_LINE_START_REGEX = ['^Total Amount due$']
    STATEMENT_AMOUNT_LINE_STOP_REGEX = ['^Minimum Amount due$']
    STATEMENT_AMOUNT_LINE_MATCH_REGEX = ['^`([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+).[0-9][0-9]']
    SERIAL_LINE_START_REGEX = ['^Amount \(in`\)$','^Transaction Details$']
    SERIAL_LINE_STOP_REGEX = ['Page (\d{1}) of (\d{1})']
    SERIAL_LINE_MATCH_REGEX = ['^(\d{10})$']
    DATE_DESCRIPTION_LINE_START_REGEX = [
        "^Amount \(in`\)$",
        "^www.icicibank.com/offers$",
        "^Transaction Details$",
        "^State Code: \d{2}$",
        "^CIN No. L65190GJ1994PLC021012$"
        ]
    DATE_DESCRIPTION_LINE_STOP_REGEX = [
        # "^# International Spends$",
        "^For exclusive$",
        "^EARNINGS$",
        "^Page \d of \d$",
        "^EMI / PERSONAL LOAN ON CREDIT CARDS$",
        "^Transaction/$",
        "^For ICICI Bank Limited",
        "^For any query",
        ]
    DESCRIPTION_LINE_NOT_MATCH_REGEX = [
        "^# International Spends$",
        "^[A-Z]{3}[1-2]\d$",#Avoid over flow of month/year to next row in cashback

        "^Apparel/Grocery-\d\d?%", #Avoid non description where are part of statement 
        "^Fuel-\d\d?%$",#Avoid non description where are part of statement fuel can be part or seperate
        "^Others-\d\d?%$", #Avoid non description where are part of statement 
        "^Dining-\d\d?%$", #Avoid non description where are part of statement 
        "^Travel-\d\d?%$",#Avoid non description where are part of statement 

        # "^\w+[-]\d\d?%$",#Trying to see if htis blanked rules works for above

       
        "^T&C apply$", # Might overflow
        "^\d{4}X{8}\d{4}$", # Removing account number/card number
        "^Intl.#", #side affect of adding Transaction Details in start regex
        "^Amount \(in`\)$",#side affect of adding Transaction Details in start regex
        "^amount$", #side affect of adding Transaction Details in start regex (it can be "Intl.# amount" or
                    # amount getting overflown to the next line   )
        "60 MYR", #That extra unwanted line in Startpoints hotel KUA,Malasya
        "^Reward$", #Rewards 
        "^Points$", #Points
        "^Reward Points$", #And finally!!

    ]

    ACCOUNT_NUMBER_LINE_MATCH_REGEX = ["^\d{4}X{8}\d{4}$"]

    def process_card_number(line):
        return CardNumberValue().cardNumber(line)
    
    statement_amount_pre_process = lambda x: x.replace('`','')
    serial_number_fetch = lambda x:x




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


