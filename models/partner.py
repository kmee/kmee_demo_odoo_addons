# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    totalvoice_number = fields.Char(
        string="TotalVoice Number",
        store=True,
    )
