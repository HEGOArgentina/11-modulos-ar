#This file is part of the country_ar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['Subdivision']


class Subdivision(ModelSQL, ModelView):
    'Adding zip code'
    __name__ = 'country.subdivision'

    zip = fields.Char('Zip', required=False, select=1)

