# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class TimesheetCreationWizard(models.TransientModel):
    _name = 'timesheet.creation.wizard'

    @api.model
    def _get_default_time(self):
        task = self.env['project.task'].browse(self._context.get('task_id'))

        duration = fields.Datetime.from_string(task.datetime_end) - \
                   fields.Datetime.from_string(task.datetime_start)

        duration_hours = (duration.total_seconds() / 3600)
        return duration_hours

    duration = fields.Float(default=_get_default_time)
    activity_description = fields.Char()

    def _get_timesheet(self, task):
        return {
            'name': self.activity_description,
            'project_id': task.project_id.id,
            'task_id': task.id,
            'unit_amount': self.duration,
            'user_id': self.env.user.id,
        }

    def action_create_timesheet(self):
        task = self.env['project.task'].browse(self._context.get('task_id'))
        task.timesheet_ids = [(0, 0, self._get_timesheet(task))]
