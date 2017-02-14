# -*- encoding: utf-8 -*-
#############################################################################
#   Copyright 2017 Haevas Informatica (http://www.haevas.com)
#   info Haevas <info@haevas.com>
#############################################################################
#   Developed by: Albert De La Fuente <albert@haevas.com>
#############################################################################
#   License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#############################################################################
from openerp.addons.report_py3o.py3o_parser import py3o_report_extender


# l10n_br_hr_payslip_py3o_report.report
@py3o_report_extender("l10n_br_hr_payroll_report_payslip_py3o.report_payslip_py3o_report")
def payslip_report(pool, cr, uid, local_context, context):
    #import pdb; pdb.set_trace() # BREAKPOINT
    #employee_id = self.env['employee_id']
    #employee = pool.get('hr.employee')
    #slip_line = pool.get('hr.payslip.line')
    #m = model('hr.payslip.line')
    #id = m.search([('code', '=', 'BASE_INSS'), ('slip_id', '=', xxx)])
    #m.browse(id).read()
    # data_formatada = formata_data(payslip.date_from, u'%A/%Y')
    # pybrasil.data.formata_data
#    import pdb; pdb.set_trace() # BREAKPOINT
    #values = {
    #    #'logo': context['logo'],
    #    'base_inss': 0.0,
    #    'base_fgts': 0.0,
    #    'fgts': 0.0,
    #    'base_irrf': 0.0,
    #}
    #local_context.update(values)
    #import pdb; pdb.set_trace() # BREAKPOINT
    #meu_legal_name = formatar(payslip.partner.legal_name)
    companylogo = pool['hr.payslip'].browse(cr, uid, context['active_id']).company_id.logo
    d = {'companylogo': companylogo}
    local_context.update(d)

