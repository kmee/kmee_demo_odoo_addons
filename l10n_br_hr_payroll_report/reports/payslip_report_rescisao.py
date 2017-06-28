# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - Hendrix Costa <hendrix.costa@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.report_py3o.py3o_parser import py3o_report_extender
from openerp import api


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
    }
    local_context.update(data)
