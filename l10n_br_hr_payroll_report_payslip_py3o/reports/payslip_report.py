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


class DummyClass():
    def __init__(self):
        self.campo = 'asdf'

    def metodo(self):
        return 'asdf'


#"py3o_template_example"
@py3o_report_extender("l10n_br_hr_payroll_report_payslip_py3o.report_payslip_py3o_report")
def payslip_report(pool, cr, uid, local_context, context):
    print(context)
    print(local_context)
    print(pool)
    print(cr)
    print(uid)
    dc = DummyClass()
    #data_formatada = formata_data(payslip.date_from, u'%A/%Y')
    #pybrasil.data.formata_data
#    import pdb; pdb.set_trace() # BREAKPOINT
    #local_context.update({})
    #local_context.update(dc)
    values = {
        'base_inss': 0.0,
        'base_fgts': 0.0,
        'fgts': 0.0,
        'base_irrf': 0.0,
    }
    local_context.update(values)
