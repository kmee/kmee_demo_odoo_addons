# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - Hendrix Costa <hendrix.costa@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.report_py3o.py3o_parser import py3o_report_extender
from openerp import api
from collections import OrderedDict


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
        pool['hr.payslip'] \
        .browse(cr, uid, context['active_id']).company_id.logo
    data = {
        'companylogo': companylogo,
        'ultimo_salario':
            buscar_ultimo_salario(
                pool, cr, uid, local_context['objects'].mes_do_ano,
                local_context['objects'].contract_id.id, context
            ),
        'correct_line_ids': valor_provento(pool, cr, uid, local_context[
            'objects'].line_ids, context)
    }
    local_context.update(data)
    pass


def valor_provento(pool, cr, uid, line_ids, context):
    fields = pool['hr.field.rescission'].search(
        cr, uid, [], context=context
    )
    lines = {}
    campos = []
    for field in fields:
        record = pool['hr.field.rescission'].browse(cr, uid, field)
        if record.codigo not in campos:
            campos.append(record)
    col = 0
    # para cada campo
    for record in campos:
        line = {'valor_provento': 0.0, 'amount': 0.0}

        # procura linhas que possuem o campo e faz a soma dos seus proventos
        for rec in line_ids:
            for rule in rec['salary_rule_id']['campo_rescisao']:
                if rule.codigo == record.codigo:
                    line['valor_provento'] += rec.valor_provento
                    line['amount'] += rec.amount
                    line['code'] = rec.category_id.code
                    line['valor_deducao_fmt'] = rec.valor_deducao_fmt

        line['display_name'] = str(record.codigo) + record.descricao
        line['column'] = col
        col += 1
        lines.update({record.codigo: line})

    OrderedDict(sorted(lines.items(), key=lambda t: t[0]))
    return lines
