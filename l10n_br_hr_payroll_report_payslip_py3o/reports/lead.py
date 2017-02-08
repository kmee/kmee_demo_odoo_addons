# -*- encoding: utf-8 -*-
from openerp.addons.report_py3o.py3o_parser import py3o_report_extender


@py3o_report_extender("hr.payslip")
def payslip_report(pool, cr, uid, local_context, context):
    import ipdb; ipdb.set_trace() # BREAKPOINT
    local_context.update({})
