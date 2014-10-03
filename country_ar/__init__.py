#This file is part of the country_ar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.


from trytond.pool import Pool
from .country import *


def register():
    Pool.register(
        Subdivision,
        module='country_ar', type_='model')


