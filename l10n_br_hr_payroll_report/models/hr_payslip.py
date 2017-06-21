# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    line_ids_fmt = fields.One2many(
        comodel_name='line.ids.fmt',
        inverse_name='payslip_id',
    )

    @api.multi
    def compute_sheet(self):
        compute = super(HrPayslip, self).compute_sheet()
        self._compute_line_ids_fmt()
        return compute

    def _compute_line_ids_fmt(self):
        proventos = []
        deducoes = []
        line_ids_fmt = []
        for line in self.line_ids_fmt:
            line.unlink()
        for line in self.line_ids:
            if line.category_id.code == 'PROVENTO':
                proventos.append(line)
            elif line.category_id.code not in [
                'PROVENTO', 'BRUTO', 'REFERENCIA',
                'LIQUIDO', 'FGTS'
            ]:
                deducoes.append(line)
        while len(proventos):
            if len(proventos) > 2:
                line_ids_fmt.append(self.env['line.ids.fmt'].create({
                    'code': 'PROVENTO',
                    'display_name': proventos[0].display_name,
                    'value': str(proventos.pop(0).valor_provento),
                    'display_name_1': proventos[0].display_name,
                    'value_1': str(proventos.pop(0).valor_provento),
                    'display_name_2': proventos[0].display_name,
                    'value_2': str(proventos.pop(0).valor_provento),
                }).id)
            elif len(proventos) == 2:
                line_ids_fmt.append(self.env['line.ids.fmt'].create({
                    'code': 'PROVENTO',
                    'display_name': proventos[0].display_name,
                    'value': str(proventos.pop(0).valor_provento),
                    'display_name_1': proventos[0].display_name,
                    'value_1': str(proventos.pop(0).valor_provento),
                    'display_name_2': '',
                    'value_2': '',
                }).id)
            elif len(proventos) == 1:
                line_ids_fmt.append(self.env['line.ids.fmt'].create({
                    'code': 'PROVENTO',
                    'display_name': proventos[0].display_name,
                    'value': str(proventos.pop(0).valor_provento),
                    'display_name_1': '',
                    'value_1': '',
                    'display_name_2': '',
                    'value_2': '',
                }).id)

        while len(deducoes):
            if len(deducoes) > 2:
                line_ids_fmt.append(self.env['line.ids.fmt'].create({
                    'code': 'DEDUCAO',
                    'display_name': deducoes[0].display_name,
                    'value': str(deducoes.pop(0).valor_deducao),
                    'display_name_1': deducoes[0].display_name,
                    'value_1': str(deducoes.pop(0).valor_deducao),
                    'display_name_2': deducoes[0].display_name,
                    'value_2': str(deducoes.pop(0).valor_deducao),
                }).id)
            if len(deducoes) == 2:
                line_ids_fmt.append(self.env['line.ids.fmt'].create({
                    'code': 'DEDUCAO',
                    'display_name': deducoes[0].display_name,
                    'value': str(deducoes.pop(0).valor_deducao),
                    'display_name_1': deducoes[0].display_name,
                    'value_1': str(deducoes.pop(0).valor_deducao),
                    'display_name_2': '',
                    'value_2': '',
                }).id)
            if len(deducoes) == 1:
                line_ids_fmt.append(self.env['line.ids.fmt'].create({
                    'code': 'DEDUCAO',
                    'display_name': deducoes[0].display_name,
                    'value': str(deducoes.pop(0).valor_deducao),
                    'display_name_1': '',
                    'value_1': '',
                    'display_name_2': '',
                    'value_2': '',
                }).id)
        self.line_ids_fmt = line_ids_fmt


class LineIdsFmt(models.Model):
    _name = 'line.ids.fmt'

    payslip_id = fields.Many2one(
        comodel_name='hr.payslip'
    )

    code = fields.Char(
        string=u'CODE'
    )

    display_name = fields.Char(
        string=u'First Display Name'
    )

    display_name_1 = fields.Char(
        string=u'Second Display Name'
    )

    display_name_2 = fields.Char(
        string=u'Third Display Name'
    )

    value = fields.Char(
        string=u'First Value'
    )

    value_1 = fields.Char(
        string=u'Second Value'
    )

    value_2 = fields.Char(
        string=u'Third Value'
    )
