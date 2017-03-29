# -*- coding: utf-8 -*-

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    cnae = fields.Integer(
        string=u'CNAE',
        size=7,
        default=3400100,
    )

    cnpj_cei = fields.Char(
        string=u'CNPJ/CEI Tomadora/Obra',
        default='12345678901',
    )
