#This file is part of the account_fiscalprinter_ar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
import xmlrpclib
from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Eval, In
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__all__ = ['Invoice']
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'

    pos = fields.Many2One('pos.fiscal.config', 'POS',
        states={
            'readonly': Eval('state') != 'draft',
            'invisible': In(Eval('type'), ['in_invoice', 'in_credit_note']),
            })

    def encode_ascii(self, string):
        encoded = ''
        for s in string:
            if isinstance(s, str):
                s = unicode(s.strip(), 'utf-8')
                encoded += s
        return encoded

    def get_printer(self, pos_ip):
        return xmlrpclib.Server(('http://%s:8069/') % (str(pos_ip),))

    def cancelAnyDocument(self, session, pos_ip):
        printer = self.get_printer(pos_ip)
        printer.cancelAnyDocument()
        return 'end'

    def get_line_tax(self, line):
        res = Decimal('0.00')
        if line.taxes:
            for tax in line.taxes:
                if tax.group.code == 'IVA':
                    res = tax.percentage
        return res

    def action_fiscal_printer(self):
        Company = Pool().get('company.company')

        if self.type in ['in_invoice', 'in_refund']:
            return True
        if not self.party.vat_number:
            raise Exception('You need to define a vat number for the customer')
        if not self.pos.is_fiscal:
            return True
        company = Company(Transaction().context.get('company'))
        printer = self.get_printer(self.pos.pos_ip)
        printer.cancelAnyDocument()

        name = str(self.party.name)
        try:
            fiscal_pos_code = str(self.party.fiscal_position.code)
        except:
            raise Exception('You need to define a fiscal position in the '
                    'party form')

        address = self.party.address_get(type='invoice')
        if not address:
            raise Exception('You need to define an invoice address for the '
                    'party')

        full_address = ''
        if address.street:
            full_address = str(full_address + ' ' + address.street)
        if address.streetbis:
            full_address = str(full_address + ' ' + address.streetbis)
        if address.city:
            full_address = str(full_address + ' ' + address.city)

        try:
            if fiscal_pos_code == '01' \
                    and company.party.fiscal_position.code == '01':
                _type = 'A'
            elif fiscal_pos_code != '01' \
                    and company.party.fiscal_position.code == '01':
                _type = 'B'
            else:
                _type = 'C'
        except:
            raise Exception('You need to define fiscal position for your '
                    'company')

        if fiscal_pos_code == '05':
            docType = '2'
        else:
            docType = 'C'

        if fiscal_pos_code == '01':
            ivaType = str('I')
        else:
            ivaType = str('C')
        try:
            doc = str(self.party.vat_number)
        except:
            raise Exception('You need to define a vat number in the party '
                    'form')

        if self.type == 'out_invoice':
            printed_invoice = printer.openBillTicket(_type, name, full_address,
                    doc, docType, ivaType)
            if printed_invoice != 1:
                raise Exception('An error has ocurred' + self.encode_ascii(str(
                        printed_invoice)))
        else:
            printer.openBillCreditTicket(_type, name, full_address, doc,
                    docType, ivaType)

        for line in self.lines:
            if line.type == 'line':
                tax = self.get_line_tax(line)
                unit_price = 0.00
                if line.unit_price:
                    unit_price = str(line.unit_price + ((line.unit_price *
                            tax) / 100))
                if line.product:
                    detail = ''
                    if self.pos and self.pos.pos_code:
                        detail = line.product.code
                        detail += ' '
                    if line.description:
                        detail += line.description
                    else:
                        detail += line.product.name
                else:
                    detail = line.description
                # TODO: Line discount
                printer.addItem(detail, line.quantity, unit_price,
                    str(tax), str('0'), '')
            if line.type == 'comment':
                printer.printFiscalText(line.description)

        # TODO: Add payment mode
        #if self.contado:
            #printer.addPayment('Contado. ', str(self.total_amount))
        #else:
            #printer.addPayment('Cta. Cte.', str(self.total_amount))
        printer.closeDocument()
        if self.type == 'out_invoice':
            last_invoice = printer.getLastNumber(_type)
        else:
            last_invoice = printer.getLastCreditNoteNumber(_type)

        self.write([self], {'reference': _type + '-' +
            str(self.pos.pos).zfill(4) + '-' + str(last_invoice).zfill(8)})

        return True

    @classmethod
    def post(cls, invoices):
        for invoice in invoices:
            invoice.action_fiscal_printer()
        super(Invoice, cls).post(invoices)
