# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - Hendrix Costa <hendrix.costa@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.report_py3o.py3o_parser import py3o_report_extender
from openerp import api
import logging

_logger = logging.getLogger(__name__)
try:
    from pybrasil import valor

except ImportError:
    _logger.info('Cannot import pybrasil')


class linha(object):
    def __init__(self, one, two, three):
        self.one = one
        self.two = two
        self.three = three


class provento_obj(object):
    def __init__(self, line_ids):
        self.campo = line_ids['campo']
        self.valor_provento_fmt = line_ids['valor_provento_fmt']
        self.amount = line_ids['amount']
        self.round_total = line_ids['round_total']
        self.display_name = line_ids['display_name']


class deducao_obj(object):
    def __init__(self, line_ids):
        self.campo = line_ids['campo']
        self.amount = line_ids['amount']
        self.valor_deducao_fmt = line_ids['valor_deducao_fmt']
        self.round_total = line_ids['round_total']
        self.display_name = line_ids['display_name']


def buscar_ultimo_salario(
        pool, cr, uid, mes_da_rescisao, contract_id, context):
    ultimo_holerite_id = pool['hr.payslip'].search(
        cr, uid, [
            ('contract_id', '=', contract_id),
            ('mes_do_ano', '=', mes_da_rescisao - 1),
            ('tipo_de_folha', '=', 'normal'),
        ], context=context
    )
    ultimo_holerite = pool['hr.payslip'].browse(cr, uid, ultimo_holerite_id)
    for line in ultimo_holerite.line_ids:
        if line.code == "SALARIO":
            return line.total


@api.model
@py3o_report_extender(
    'l10n_br_hr_payroll_report.report_payslip_py3o_rescisao')
def payslip_rescisao(pool, cr, uid, local_context, context):
    companylogo = \
        pool['hr.payslip'].browse(cr, uid, context[
            'active_id']).company_id.logo
    data = {
        'companylogo': companylogo,
        'ultimo_salario':
            buscar_ultimo_salario(
                pool, cr, uid, local_context['objects'].mes_do_ano,
                local_context['objects'].contract_id.id, context
            ),
        'provento_line': valor_provento(pool, cr, uid, local_context[
            'objects'].line_ids, context),
        'deducao_line': valor_deducao(pool, cr, uid, local_context[
            'objects'].line_ids, context),
    }
    local_context.update(data)


def valor_provento(pool, cr, uid, line_ids, context):
    fields = pool['hr.field.rescission'].search(
        cr, uid, [], context=context
    )
    lines = []
    campos = []
    descricao = {}
    # impede registros repetidos
    for field in fields:
        record = pool['hr.field.rescission'].browse(cr, uid, field)
        if record.codigo not in campos:
            campos.append(record.codigo)
            descricao.update({record.codigo: {
                'descricao': record.descricao}})
    # para cada campo
    for record in campos:
        line = {'valor_provento': 0.0, 'amount': 0.0}

        # procura linhas que possuem o campo e faz a soma dos seus proventos
        for rec in line_ids:
            # cada regra da linha
            for rule in rec['salary_rule_id']['campo_rescisao']:
                if rule.codigo == record and rec.category_id.code == \
                        'PROVENTO':
                    line['valor_provento'] += rec.valor_provento
                    line['amount'] += rec.amount
                    line['round_total'] = rec.round_total

        line['display_name'] = str(record) + " " + descricao[record][
            'descricao']
        line['campo'] = record
        if line.get('valor_provento'):
            line['valor_provento_fmt'] = valor.formata_valor(
                line['valor_provento'])
            obj = provento_obj(line)
            lines.append(obj)
    if len(lines) != 0:
        lines = sorted(lines, key=lambda t: t.campo)

    table_lines = []
    for it in range(0, len(lines), 3):
        if it + 2 > len(lines):
            line1 = {}
            line1['campo'] = ''
            line1['valor_provento_fmt'] = ''
            line1['amount'] = ''
            line1['round_total'] = ''
            line1['display_name'] = ''
            obj1 = provento_obj(line1)
            line2 = {}
            line2['campo'] = ''
            line2['valor_provento_fmt'] = ''
            line2['amount'] = ''
            line2['round_total'] = ''
            line2['display_name'] = ''
            obj2 = provento_obj(line2)
            line_obj = linha(lines[it], obj1, obj2)
        elif it + 3 > len(lines):
            line1 = {}
            line1['campo'] = ''
            line1['valor_provento_fmt'] = ''
            line1['amount'] = ''
            line1['round_total'] = ''
            line1['display_name'] = ''
            obj1 = provento_obj(line1)
            line_obj = linha(lines[it], lines[it + 1], obj1)
        else:
            line_obj = linha(lines[it], lines[it + 1], lines[it + 2])
        table_lines.append(line_obj)
    return table_lines


def valor_deducao(pool, cr, uid, line_ids, context):
    fields = pool['hr.field.rescission'].search(
        cr, uid, [], context=context
    )
    lines = []
    campos = []
    descricao = {}
    # impede registros repetidos
    for field in fields:
        record = pool['hr.field.rescission'].browse(cr, uid, field)
        if record.codigo not in campos:
            campos.append(record.codigo)
            descricao.update({record.codigo: {
                'descricao': record.descricao}})
    # para cada campo
    for record in campos:
        line = {'valor_deducao': 0.0, 'amount': 0.0, 'valor_deducao_fmt': ''}

        # procura linhas que possuem o campo e faz a soma de suas deduções
        for rec in line_ids:
            # cada regra da linha
            for rule in rec['salary_rule_id']['campo_rescisao']:
                if rule.codigo == record and rec.category_id.\
                        code not in ['PROVENTO', 'BRUTO', 'REFERENCIA',
                                     'LIQUIDO', 'FGTS']:
                    line['amount'] += rec.amount
                    line['valor_deducao'] += rec.valor_deducao
                    line['round_total'] = rec.round_total
        line['display_name'] = str(record) + " " + descricao[record][
            'descricao']
        line['campo'] = record
        if line.get('valor_deducao', False):
            line['valor_deducao_fmt'] = valor.formata_valor(
                line['valor_deducao'])
            obj = deducao_obj(line)
            lines.append(obj)
    if len(lines) != 0:
        lines = sorted(lines, key=lambda t: t.campo)

    table_lines = []
    for it in range(0, len(lines), 3):
        if it + 2 > len(lines):
            line1 = {}
            line1['campo'] = ''
            line1['valor_deducao_fmt'] = ''
            line1['amount'] = ''
            line1['round_total'] = ''
            line1['display_name'] = ''
            obj1 = deducao_obj(line1)
            line2 = {}
            line2['campo'] = ''
            line2['valor_deducao_fmt'] = ''
            line2['amount'] = ''
            line2['round_total'] = ''
            line2['display_name'] = ''
            obj2 = deducao_obj(line2)
            line_obj = linha(lines[it], obj1, obj2)
        elif it + 3 > len(lines):
            line1 = {}
            line1['campo'] = ''
            line1['valor_deducao_fmt'] = ''
            line1['amount'] = ''
            line1['round_total'] = ''
            line1['display_name'] = ''
            obj1 = deducao_obj(line1)
            line_obj = linha(lines[it], lines[it + 1], obj1)
        else:
            line_obj = linha(lines[it], lines[it + 1], lines[it + 2])
        table_lines.append(line_obj)
    return table_lines
