# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SacTicket(models.Model):

    _inherit = 'sac.ticket'

    task_id = fields.Many2one(
        'project.task',
    )
    project_id = fields.Many2one(
        'project.project',
        related='task_id.project_id'
    )
