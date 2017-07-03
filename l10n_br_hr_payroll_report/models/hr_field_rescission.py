# -*- coding: utf-8 -*-
from openerp import models, fields


class HrFieldRescission(models.Model):
    _name = 'hr.field.rescission'

    codigo = fields.Integer(
        required=True,
    )
    descricao = fields.Char(
        required=True,
    )
    rule = fields.Many2one()
