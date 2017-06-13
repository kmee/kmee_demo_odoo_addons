# -*- encoding: utf-8 -*-
# Copyright (C) 2017 - TODAY Albert De La Fuente - KMEE
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api
from openerp.addons.report_py3o.py3o_parser import py3o_report_extender


@api.model
@py3o_report_extender(
    "l10n_br_hr_payroll_report.report_analytic_py3o_report")
def analytic_report(pool, cr, uid, local_context, context):
    active_model = context['active_model']
    if active_model == 'wizard.l10n_br_hr_payroll.analytic_report':
        proxy = pool['wizard.l10n_br_hr_payroll.analytic_report']
        wizard = proxy.browse(cr, uid, context['active_id'])
        payslip_ids = \
            pool['hr.payslip'].search(cr, uid, [
                ('company_id', '=', wizard.company_id.id),
                ('tipo_de_folha', '=', wizard.tipo_de_folha),
                ('mes_do_ano', '=', wizard.mes_do_ano),
                ('ano', '=', wizard.ano)]
            )

        payslips = []
        for payslip_id in payslip_ids:
            payslips += \
                pool['hr.payslip']\
                .browse(cr, uid, payslip_id)
    else:
        payslips = \
            pool['hr.payslip.run']\
            .browse(cr, uid, context['active_id']).slip_ids
    SQL_BUSCA_RUBRICAS = '''
    SELECT 
        salary_rule.code,
        salary_rule.name,
        sum(payslip_line.quantity) as quantity,
        payslip_line.rate,
        sum(payslip_line.total),
        rule_category.code as category
    FROM 
        hr_payslip payslip
        join hr_payslip_line payslip_line on payslip_line.slip_id = payslip.id
        join hr_salary_rule salary_rule on salary_rule.id = payslip_line.salary_rule_id
        join hr_salary_rule_category rule_category on rule_category.id = salary_rule.category_id
    WHERE
        payslip.mes_do_ano = {}
    GROUP BY
        salary_rule.code,
        salary_rule.name,
        payslip_line.rate,
        category
    ORDER BY
        salary_rule.name;
    '''
    SQL_BUSCA_SEFIP = '''
    SELECT 
        salary_rule.code,
        salary_rule.name,
        sum(payslip_line.quantity) as quantity,
        payslip_line.rate,
        sum(payslip_line.total),
        rule_category.code as category
    FROM 
        hr_payslip payslip
        join hr_payslip_line payslip_line on payslip_line.slip_id = payslip.id
        join hr_salary_rule salary_rule on salary_rule.id = payslip_line.salary_rule_id
        join hr_salary_rule_category rule_category on rule_category.id = salary_rule.category_id
    WHERE
        rule_category.code = 'SEFIP'
    GROUP BY
        salary_rule.code,
        salary_rule.name,
        payslip_line.rate,
        category
    ORDER BY
        salary_rule.name;
    '''
    SQL_BUSCA_RUBRICAS = SQL_BUSCA_RUBRICAS.format(wizard.mes_do_ano)
    cr.execute(SQL_BUSCA_RUBRICAS)
    payslip_lines = cr.dictfetchall()
    cr.execute(SQL_BUSCA_SEFIP)
    payslip_lines_sefip = cr.dictfetchall()
    proventos = []
    descontos = []
    total_proventos = 0.0
    total_descontos = 0.0
    taxa_inss_empresa = 0.0
    taxa_rat_fap = 0.0
    taxa_terceiros = 0.0

    for rubrica in payslip_lines_sefip:
        if rubrica['code'] == 'INSS_EMPRESA':
            taxa_inss_empresa = rubrica['rate']/100
        elif rubrica['code'] == 'INSS_RAT_FAP':
            taxa_rat_fap = rubrica['rate']/100
        elif rubrica['code'] == 'INSS_OUTRAS_ENTIDADES':
            taxa_terceiros = rubrica['rate']/100

    class inss_empresa_obj(object):
        def __init__(self, valores_inss_empresa):
            self.base = valores_inss_empresa['base']
            self.inss_empresa = valores_inss_empresa['inss_empresa']
            self.rat_fap = valores_inss_empresa['rat_fap']
            self.terceiros = valores_inss_empresa['terceiros']
            self.total = valores_inss_empresa['total']

    class rubrica_obj(object):
        def __init__(self, rubrica):
            self.code = rubrica['code']
            self.name = rubrica['name']
            self.quantity = rubrica['quantity']
            self.sum = rubrica['sum']

    valores_inss_empresa = {
            'base': 0.0,
            'inss_empresa': 0.0,
            'rat_fap': 0.0,
            'terceiros': 0.0,
            'total': 0.0,
        }
    inss_empresa_funcionario = inss_empresa_obj(valores_inss_empresa)
    inss_empresa_pro_labore = inss_empresa_obj(valores_inss_empresa)
    inss_empresa_autonomo = inss_empresa_obj(valores_inss_empresa)
    inss_empresa_cooperativa = inss_empresa_obj(valores_inss_empresa)
    for rubrica in payslip_lines:
        if rubrica['code'] == 'INSS_EMPRESA':
            inss_empresa_funcionario.base = rubrica['sum']
            inss_empresa_funcionario.inss_empresa = \
                rubrica['sum'] * taxa_inss_empresa
            inss_empresa_funcionario.rat_fap = rubrica['sum'] * taxa_rat_fap
            inss_empresa_funcionario.terceiros = rubrica['sum'] * taxa_terceiros
            inss_empresa_funcionario.total = \
                inss_empresa_funcionario.inss_empresa + \
                inss_empresa_funcionario.rat_fap + \
                inss_empresa_funcionario.terceiros
        if rubrica['category'] == 'PROVENTO':
            proventos.append(rubrica_obj(rubrica))
            total_proventos += rubrica['sum']
        elif rubrica['category'] in ['DEDUCAO', 'INSS', 'IRPF']:
            descontos.append(rubrica_obj(rubrica))
            total_descontos += rubrica['sum']

    legal_name = payslips[0].company_id.legal_name
    cnpj_cpf = payslips[0].company_id.cnpj_cpf
    mes_do_ano = payslips[0].mes_do_ano
    ano = payslips[0].ano

    data = {
        'legal_name': legal_name,
        'cnpj_cpf': cnpj_cpf,
        'mes_do_ano': mes_do_ano,
        'ano': ano,
        'objects': payslips,
        'proventos': proventos,
        'descontos': descontos,
        'total_proventos': total_proventos,
        'total_descontos': total_descontos,
        'total_liquido': total_proventos - total_descontos,
        'inss_empresa_funcionario': inss_empresa_funcionario,
        'inss_empresa_pro_labore': inss_empresa_pro_labore,
        'inss_empresa_autonomo': inss_empresa_autonomo,
        'inss_empresa_cooperativa': inss_empresa_cooperativa,
    }
    local_context.update(data)
