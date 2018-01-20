#!/usr/bin/env python

"""ynab_csv.py: Converts Revolut csv file to an acceptable format for input to YNAB."""

__author__      = "Jon Lidgard"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Jon Lidgard"
__email__ = "jonlidgard@gmail.com"
__status__ = "Development"

import sys
import csv
import argparse
import datetime
#import locale
#from decimal import Decimal


YNAB_HEADER_DATE = 'Date'
YNAB_HEADER_PAYEE = 'Payee'
YNAB_HEADER_CATEGORY = 'Category'
YNAB_HEADER_MEMO = 'Memo'
YNAB_HEADER_OUTFLOW = 'Outflow'
YNAB_HEADER_INFLOW = 'Inflow'

REVOLUT_HEADER_DATE = 'Completed Date'
REVOLUT_HEADER_PAYEE = 'Reference'
REVOLUT_HEADER_CATEGORY = 'Category'
REVOLUT_HEADER_OUTFLOW = 'Paid Out (GBP)'
REVOLUT_HEADER_INFLOW = 'Paid In (GBP)'
REVOLUT_IDENTIFIER_KEY = REVOLUT_HEADER_DATE

PAYPAL_HEADER_DATE = 'Date'
PAYPAL_HEADER_PAYEE = ' Name'
PAYPAL_HEADER_TYPE = ' Type'
PAYPAL_HEADER_MEMO = ' Item Title'
PAYPAL_HEADER_INFLOW = ' Net'
PAYPAL_IDENTIFIER_KEY = ' Counterparty Status'


parser = argparse.ArgumentParser(description='Process Revolut csv statement files for import into YNAB.')
parser.add_argument('csvfile', help='the .csv file to process')
parser.add_argument('-c', '--category', action='count', help='Fill in the category field')
parser.add_argument('-m', '--memo', action='count', help='Fill in the Memo field with Exchange info')
parser.add_argument('-t', '--topup', action='count', help='Skip Top-Up & Auto Top-Up entries')
parser.add_argument('-o', '--output', help=' File to write csv to, else output to stdout')

args = parser.parse_args()

results = []
YNAB_FIELDNAMES = [YNAB_HEADER_DATE, YNAB_HEADER_PAYEE, YNAB_HEADER_CATEGORY, YNAB_HEADER_MEMO, YNAB_HEADER_OUTFLOW, YNAB_HEADER_INFLOW]


class baseCSV:

    def __init__(self, args, reader, writer):
        self.args = args
        self.reader = reader
        self.writer = writer

    def isBankTopUp(self, row):
        return False

    def printRow(self, y_row):
        y_line = y_row[YNAB_HEADER_DATE] + ',"' + y_row[YNAB_HEADER_PAYEE] + '","' + y_row[YNAB_HEADER_CATEGORY] + \
            '","' + y_row[YNAB_HEADER_MEMO] + '",' + y_row[YNAB_HEADER_OUTFLOW] + ',' + y_row[YNAB_HEADER_INFLOW]

        #            if not self.args.output:
        print(y_line)

    def writeHeader(self):
        if self.args.output:
            writer.writeheader()
        else:
            print(YNAB_HEADER_DATE + "," + YNAB_HEADER_PAYEE + "," + YNAB_HEADER_CATEGORY + "," +
                  YNAB_HEADER_MEMO + "," + YNAB_HEADER_OUTFLOW + "," + YNAB_HEADER_INFLOW)


    def writeRow(self, y_row):
        if self.args.output:
            writer.writerow(y_row)
        else:
            self.printRow(y_row)


    def Convert(self):
        print("")



class RevolutCSV(baseCSV):

    def __init__(self, args, reader, write):
        baseCSV.__init__(self, args, reader, writer)

    def isBankTopUp(self, row):
        payee = row[REVOLUT_HEADER_PAYEE]
        return payee[:6] == 'Top-Up' or payee[:11] == 'Auto Top-Up'

    def ProcessCurrency(self, amount):
        """ Remove the comma in n,nnn.nn"""
        return amount.replace(',','')

#        if amount == '':
#            return ''
#        return Decimal(amount)

    def Convert(self):
        self.writeHeader()

        for r_row in self.reader:

            if self.args.topup and self.isBankTopUp(r_row):
                continue

            y_row = {}
            # Do Date
            r_date = r_row[REVOLUT_HEADER_DATE]
            y_date = datetime.datetime.strptime(r_date, '%d %B %Y')
            y_date = (datetime.date.strftime(y_date, "%d/%m/%Y"))
            y_row[YNAB_HEADER_DATE] = y_date

            # Payee
            y_row[YNAB_HEADER_PAYEE] = r_row[REVOLUT_HEADER_PAYEE]

            # Category

            if self.args.category:
                y_row[YNAB_HEADER_CATEGORY] = r_row[REVOLUT_HEADER_CATEGORY]
            else:
                y_row[YNAB_HEADER_CATEGORY] = ''

            # Memo
            if self.args.memo:
                y_row[YNAB_HEADER_MEMO] = r_row['Exchange Out'] + r_row['Exchange In']
            else:
                y_row[YNAB_HEADER_MEMO] = ''

            # Inflow, Outflow

            y_row[YNAB_HEADER_INFLOW] = self.ProcessCurrency(r_row[REVOLUT_HEADER_INFLOW])
            y_row[YNAB_HEADER_OUTFLOW] = self.ProcessCurrency(r_row[REVOLUT_HEADER_OUTFLOW])


            self.writeRow(y_row)



class PaypalCSV(baseCSV):
    def __init__(self, args, reader, writer):
        baseCSV.__init__(self, args, reader, writer)

    def isBankTopUp(self, row):
        return row[PAYPAL_HEADER_PAYEE] == 'Bank Account' and row[PAYPAL_HEADER_TYPE] == 'Add Money from a Bank Account'

    def isTemporaryHold(self, row):
        return row[PAYPAL_HEADER_PAYEE] == 'PayPal' and row[PAYPAL_HEADER_TYPE] == "Temporary Hold"

    def isCurrencyConversion(self, row):
        return row[PAYPAL_HEADER_TYPE] == 'Currency Conversion'

    def Convert(self):
        self.writeHeader()

        for p_row in self.reader:

            if self.args.topup and self.isBankTopUp(p_row):
                continue

            if self.isTemporaryHold(p_row):
                continue

            if self.isCurrencyConversion(p_row):
                continue


            y_row = {}
            # Do Date
            y_row[YNAB_HEADER_DATE] = p_row[PAYPAL_HEADER_DATE]

            y_row[YNAB_HEADER_PAYEE] = p_row[PAYPAL_HEADER_PAYEE]
            y_row[YNAB_HEADER_CATEGORY] = ''

            if self.args.memo:
                y_row[YNAB_HEADER_MEMO] = p_row[PAYPAL_HEADER_MEMO]
            else:
                y_row[YNAB_HEADER_MEMO] = ''

            y_row[YNAB_HEADER_OUTFLOW] = ''
            y_row[YNAB_HEADER_INFLOW] = p_row[PAYPAL_HEADER_INFLOW]

            self.writeRow(y_row)

with open(args.csvfile, newline='') as csvfile:
    # Check we've got a header line
    if not csv.Sniffer().has_header(csvfile.read(1024)):
        print ("ERROR: s does not appear to have a header line.", file=sys.stderr)
        exit(1)
    csvfile.seek(0)

    # Get some basic csv file info
    dialect = csv.Sniffer().sniff(csvfile.read(1024))

    csvfile.seek(0)

    # Start reading the file
    reader = csv.DictReader(csvfile, delimiter=dialect.delimiter)
    if args.output:
        outfile = open(args.output, 'w')
        writer = csv.DictWriter(outfile, YNAB_FIELDNAMES)
    else:
        writer = None

    #    print (reader.fieldnames)
    if REVOLUT_IDENTIFIER_KEY in reader.fieldnames:
        csv_processor = RevolutCSV(args, reader, writer)
    elif PAYPAL_IDENTIFIER_KEY in reader.fieldnames:
        csv_processor = PaypalCSV(args, reader, writer)
    else:
        print("ERROR: Unrecognised file format.", file=sys.stderr)
        exit(1)

    csv_processor.Convert()

