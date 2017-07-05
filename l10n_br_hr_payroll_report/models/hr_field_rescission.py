# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HrFieldRescission(models.Model):
    _name = 'hr.field.rescission'

    codigo = fields.Integer(
        string='codigo',
        required=True,
    )
    descricao = fields.Char(
        string='descrição',
        required=True,
    )
    variaveis = fields.Char(
        string='Variáveis disponíveis',
        readonly=True,
        default='${DIAS_BASE} - ${DIAS_UTEIS} - ${FERIAS} - ${'
                'ABONO_PECUNIARIO} - ${DIAS_TRABALHADOS} - '
                '${PERIODO_AQUISITIVO}'
    )
    rule = fields.Many2one(
        readonly=True,
    )

    @api.one
    def name_get(self):
        name = 'Campos da rescisão/'+str(self.id)
        return self.id, name
