#This file is part of the account_fiscalprinter_ar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool
from party import *
from fiscalprinter import *
from invoice import *


def register():
    Pool.register(
        AccountFiscalPosition,
        Party,
        PosFiscalConfig,
        AccountFiscalPrinterCancelOpenStart,
        AccountFiscalPrinterDailyCloseStart,
        Invoice,
        module='account_fiscalprinter_ar', type_='model')
    Pool.register(
        AccountFiscalPrinterCancelOpen,
        AccountFiscalPrinterDailyClose,
        module='account_fiscalprinter_ar', type_='wizard')