# Copyright 2019 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sac',
    'summary': """
        Serviço de Atendimento ao Consumidor""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'www.kmee.com.br',
    'depends': [
        'mail',
        'base_kanban_stage',
    ],
    'data': [
        'security/sac_assunto.xml',
        'security/sac_ticket.xml',

        'data/sac_sequence.xml',

        'views/sac_menu.xml',

        'views/sac_assunto.xml',
        'views/sac_ticket.xml',
    ],
    'demo': [
        'demo/sac_assunto.xml',
        'demo/sac_ticket.xml',
    ],
}
