#This file is part of the account_fiscalprinter_ar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

__all__ = ['AccountFiscalPosition', 'Party']
__metaclass__ = PoolMeta

STATES = {
    'readonly': ~Eval('active', True),
}
DEPENDS = ['active']


class AccountFiscalPosition(ModelSQL, ModelView):
    "Fiscal Position"
    __name__ = 'account.fiscal.position'

    name = fields.Char('Name', required=True, select=True,
        states=STATES, depends=DEPENDS)
    code = fields.Char('Code', required=True, select=True,
        states=STATES, depends=DEPENDS)
    notes = fields.Text('Notes', translate=True,
        states=STATES, depends=DEPENDS)
    active = fields.Boolean('Active', select=True)

    @classmethod
    def __setup__(cls):
        super(AccountFiscalPosition, cls).__setup__()
        cls._sql_constraints = [
            ('code_uniq', 'UNIQUE(code)',
             'The code of the fiscal position must be unique!')
        ]
        cls._order.insert(0, ('name', 'ASC'))

    @staticmethod
    def default_active():
        return True


class Party:
    __name__ = 'party.party'

    fiscal_position = fields.Many2One('account.fiscal.position',
        'Fiscal Position', states=STATES, depends=DEPENDS)


