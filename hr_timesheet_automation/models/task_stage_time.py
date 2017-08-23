# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class TaskStageTime(models.Model):
    _name = 'task.stage.time'

    @api.multi
    @api.depends('date_end')
    def _compute_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                duration = fields.Datetime.from_string(record.date_end) - \
                           fields.Datetime.from_string(record.date_start)
                duration_hours = (duration.total_seconds() / 3600)
                record.duration = duration_hours
            else:
                record.duration = False

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task'
    )
    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Stage'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User'
    )
    date_start = fields.Datetime(string='Date start')
    date_end = fields.Datetime(string='Date end')
    duration = fields.Float(string='Duration', compute='_compute_duration')
