# Copyright 2019 kmee
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sac Project',
    'summary': """
        Integration with project""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'kmee,Odoo Community Association (OCA)',
    'depends': [
        'sac',
        'project',
    ],
    'data': [
        'wizards/sac_ticket_wizard.xml',
        'views/sac_ticket.xml',
    ],
    'demo': [
    ],
}
