# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HrFieldRescission(models.Model):
    _name = 'hr.field.rescission'

    codigo = fields.Integer()
    descricao = fields.Char()
