# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SacTicketWizard(models.TransientModel):

    _name = 'sac.ticket.wizard'

    name = fields.Char()
    project_id = fields.Many2one(
        comodel_name='project.project',
    )

    @api.multi
    def doit(self):
        for wizard in self:
            result_ids = self.env['project.task'].create(
                {
                    'project_id': wizard.project_id.id,
                    'name':  wizard.name,
                }
            )
            active_id = wizard.env.context.get('active_id')
            if active_id:
                ticket = self.env['sac.ticket'].browse(
                    active_id
                )
                ticket.task_id = result_ids

        #action = {
        #    'type': 'ir.actions.act_window',
        #    'name': 'Action Name',  # TODO
        #    'res_model': 'project.task',
        #    'domain': [('id', 'in', result_ids.ids)],
        #    'view_mode': 'form,tree',
        #}
        #return action
        return True
