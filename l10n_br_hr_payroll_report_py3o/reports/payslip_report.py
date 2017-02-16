# -*- encoding: utf-8 -*-
# Copyright (C) 2017 - TODAY Albert De La Fuente - KMEE
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.addons.report_py3o.py3o_parser import py3o_report_extender
from openerp import api
from openerp import fields


@py3o_report_extender(
    "l10n_br_hr_payroll_report_py3o.report_payslip_py3o_report")
def payslip_report(pool, cr, uid, local_context, context):
    companylogo = \
        pool['hr.payslip'] \
        .browse(cr, uid, context['active_id']).company_id.logo
    d = {'companylogo': companylogo}
    local_context.update(d)


@api.model
@py3o_report_extender(
    "l10n_br_hr_payroll_report_py3o.report_analytic_py3o_report")
def analytic_report(pool, cr, uid, local_context, context):
    active_model = context['active_model']
    if active_model == 'wizard.l10n_br_hr_payroll.analytic_report':
        print('Venho dos reports')
        import pdb; pdb.set_trace() # BREAKPOINT
        data = {}
    else:
        print('Venho do imprimir')
        payslips = \
            pool['hr.payslip.run']\
            .browse(cr, uid, context['active_id']).slip_ids

    legal_name = payslips[0].company_id.legal_name
    legal_name = 'Empresa bla bla'
    cnpj_cpf = payslips[0].company_id.cnpj_cpf
    cnpj_cpf = '125.252.15'
    mes_do_ano = payslips[0].mes_do_ano
    mes_do_ano = '3'
    ano = payslips[0].ano
    ano = '2017'
    #fields.convert_to_write(payslip_obj)

    data = {
        'legal_name': legal_name,
        'cnpj_cpf': cnpj_cpf,
        'mes_do_ano': mes_do_ano,
        'ano': ano,
        'objects': payslips,
        'totals': {
            ''
        },
    }
    local_context.update(data)
