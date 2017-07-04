# -*- coding: utf-8 -*-

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    cnpj_cei = fields.Char(
        string=u'CNPJ/CEI Tomadora/Obra',
        default='12345678901',
    )
