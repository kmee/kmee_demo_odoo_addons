# -*- encoding: utf-8 -*-
from openerp.addons.report_py3o.py3o_parser import py3o_report_extender


@py3o_report_extender("crm.lead")
def lead_report(pool, cr, uid, local_context, context):
    local_context.update({})
