#This file is part of the account_fiscalprinter_ar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
import xmlrpclib
from trytond.model import ModelSQL, ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button

__all__ = ['PosFiscalConfig', 'AccountFiscalPrinterCancelOpenStart',
    'AccountFiscalPrinterCancelOpen', 'AccountFiscalPrinterDailyCloseStart',
    'AccountFiscalPrinterDailyClose']


class PosFiscalConfig(ModelSQL, ModelView):
    'Fiscal Printer Configuration'
    __name__ = 'pos.fiscal.config'

    pos = fields.Integer('POS')
    pos_ip = fields.Char('POS IP Address')
    pos_code = fields.Boolean('Print Product Codes')
    is_fiscal = fields.Boolean('Fiscal ?')


class AccountFiscalPrinterCancelOpenStart(ModelView):
    'Cancel Open Document'
    __name__ = 'account.fiscalprinter.cancel_open.start'

    pos = fields.Many2One('pos.fiscal.config', 'POS', required=True)


class AccountFiscalPrinterCancelOpen(Wizard):
    'Cancel Open Document'
    __name__ = 'account.fiscalprinter.cancel_open'

    start = StateView('account.fiscalprinter.cancel_open.start',
        'account_fiscalprinter_ar.cancel_open_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Ok', 'send', 'tryton-ok', default=True),
            ])
    send = StateTransition()

    def get_printer(self, pos_ip):
        return xmlrpclib.Server(('http://%s:8069/') % (str(pos_ip),))

    def transition_send(self):
        server = self.get_printer(self.start.pos.pos_ip)
        printer_response = server.cancelAnyDocument()
        if printer_response != 1:
            raise Exception(printer_response)
        return 'end'


class AccountFiscalPrinterDailyCloseStart(ModelView):
    'Daily Close Start'
    __name__ = 'account.fiscalprinter.daily_close.start'

    pos = fields.Many2One('pos.fiscal.config', 'POS', required=True)
    type = fields.Selection([
        ('x', 'X'),
        ('z', 'Z'),
        ], 'Type', required=True)


class AccountFiscalPrinterDailyClose(Wizard):
    'Daily Close'
    __name__ = 'account.fiscalprinter.daily_close'

    start = StateView('account.fiscalprinter.daily_close.start',
        'account_fiscalprinter_ar.daily_close_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Ok', 'send', 'tryton-ok', default=True),
            ])
    send = StateTransition()

    def get_printer(self, pos_ip):
        return xmlrpclib.Server(('http://%s:8069/') % (str(pos_ip),))

    def transition_send(self):
        server = self.get_printer(self.start.pos.pos_ip)
        printer_response = server.dailyClose(self.start.type)
        if printer_response != 1:
            raise Exception(printer_response)
        return 'end'
