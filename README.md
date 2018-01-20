## usage: ynab_csv.py [-h] [-c] [-m] [-t] [-o OUTPUT] csvfile

```
Process Revolut csv statement files for import into YNAB.

positional arguments:
  csvfile               the .csv file to process

optional arguments:
  -h, --help            show this help message and exit
  -c, --category        Fill in the category field
  -m, --memo            Fill in the Memo field with Exchange info
  -t, --topup           Skip Top-Up, Auto Top-Up (Revolut) & Add money from a Bank Account (PayPal) entries
  -o OUTPUT, --output OUTPUT
                        File to write csv to, else output to stdout
```

Revolut files are processed to remove the ',' from the Inflow & Outflow fields

PayPal files are processed to remove the 'Temporary Hold' and 'Currency Conversion' entries

IMPORTANT:  This program is set to work in the UK with GBP & will need modifying to work in other countries.
            MINIMAL testing carried out, check the output carefully!
            Revolut, PayPal & YNAB file specs valid as of 20th Jan 2018.
