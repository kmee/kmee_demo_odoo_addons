# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HrFieldRescission(models.Model):
    _name = 'hr.field.rescission'

    codigo = fields.Integer(
        required=True,
    )
    descricao = fields.Char(
        required=True,
    )
    rule = fields.Many2one(
        readonly=True,
    )

    @api.one
    def name_get(self):
        name = 'Campos da rescisão/'+str(self.id)
        return self.id, name
