# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HrFieldRescission(models.Model):
    _name = 'hr.field.rescission'
    _order = 'codigo ASC'

    codigo = fields.Integer(
        string=u'Código',
        required=True,
    )
    descricao = fields.Char(
        string=u'descrição',
        required=True,
    )
    variaveis = fields.Char(
        string=u'Variáveis disponíveis',
        readonly=True,
        default='${DIAS_BASE} - ${DIAS_UTEIS} - ${FERIAS} - ${'
                'ABONO_PECUNIARIO} - ${DIAS_TRABALHADOS} - '
                '${PERIODO_FERIAS_VENCIDAS} - ${AVOS}'
    )
    rule = fields.One2many(
        string=u'Regras de Salário',
        comodel_name='hr.salary.rule',
        inverse_name='campo_rescisao',
        readonly=True,
    )
    name = fields.Char(
        string=u'Nome',
        compute="name_get",
        store=True,
    )

    @api.one
    def name_get(self):
        name = ''
        if self.codigo:
            name += str(self.codigo)
        if self.descricao:
            if self.codigo:
                name += '-'
            name += self.descricao
        return self.id, name
