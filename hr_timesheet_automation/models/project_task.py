# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProjectTaskTimesheetAutomation(models.Model):
    _inherit = 'project.task'

    task_stage_time_ids = fields.One2many(
        comodel_name='task.stage.time',
        inverse_name='task_id',
        string='Time per stage',
    )

    datetime_start = fields.Datetime('Start time')
    datetime_end = fields.Datetime('Stop time')
    stop_label = fields.Boolean()

    def open_timesheet_creation_wizard(self):
        ctx = self.env.context.copy()
        ctx.update(dict(task_id=self.id))
        return {
            'name': _('Timesheet Line Creation'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'timesheet.creation.wizard',
            'context': ctx,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def action_log_time(self):
        actual_time = fields.Datetime.now()

        if not self.datetime_start and not self.datetime_end:
            self.datetime_start = actual_time
            self.stop_label = True

        elif self.datetime_start and not self.datetime_end:
            self.datetime_end = actual_time
            self.stop_label = False
            return self.open_timesheet_creation_wizard()

        elif self.datetime_start and self.datetime_end:
            self.datetime_start = actual_time
            self.datetime_end = False
            self.stop_label = True

    def create_new_stage_time(self, stage_id):
        actual_time = fields.Datetime.now()
        return {
            'task_id': self.id,
            'stage_id': stage_id,
            'user_id': self.env.user.id,
            'date_start': actual_time,
        }

    def conclude_last_stage_time(self):
        last_stage_time = self.env['task.stage.time'].search(
            [
                ('task_id', '=', self.id),
            ], order='id desc', limit=1)

        if last_stage_time and not last_stage_time.date_end:
            actual_time = fields.Datetime.now()
            dt_at = fields.Datetime.from_string(actual_time)
            last_stage_time.date_end = dt_at
        return last_stage_time

    @api.model
    def create(self, vals):
        stage_id = self._get_default_stage_id()
        stage_time = self.create_new_stage_time(stage_id)
        vals['task_stage_time_ids'] = [(0, 0, stage_time)]
        res = super(ProjectTaskTimesheetAutomation, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            self.conclude_last_stage_time()
            vals['task_stage_time_ids'] = [
                (0, 0, self.create_new_stage_time(vals.get('stage_id')))]
        res = super(ProjectTaskTimesheetAutomation, self).write(vals)
        return res
