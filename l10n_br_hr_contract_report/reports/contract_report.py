# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - Hendrix Costa <hendrix.costa@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.report_py3o.py3o_parser import py3o_report_extender
from openerp import api


@api.model
@py3o_report_extender('l10n_br_hr_contract_report.reports.contract_report')
def contract_report(pool, cr, uid, local_context, context):
    companylogo = \
        pool['hr.contract'] \
        .browse(cr, uid, context['active_id']).company_id.logo
    d = {'companylogo': companylogo}
    local_context.update(d)
