# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR Timesheet Automation',
    'summary': """
        Implements start/pause/stop button in task model for 
        better time control""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'www.kmee.com.br',
    'depends': [
        'hr_timesheet'
    ],
    'data': [
        'views/project_task_view.xml',
        'wizards/timesheet_creation_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [

    ],
    'test': [
    ]
}
