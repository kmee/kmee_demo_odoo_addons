{
    'name': "TotalVoice Odoo",
    'summary': """ This application is intended to receive SMS and perform automatic actions from these messages. """,
    'version': '10.0.1.0.0',
    'category': 'SMS app',
    'website': "https://www.kmee.com.br/",
    'author': "KMEE Informática LTDA",
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'depends': [
        'base',
        'mail',
        'webhook',
        'link_tracker',
    ],
    'data': [
        'security/totalvoice_security.xml',
        'security/ir.model.access.csv',

        'data/ir_config_parameter.xml',

         'views/totalvoice_base_view.xml',
         'views/totalvoice_webhook.xml',
         'views/totalvoice_config_view.xml',
         'views/totalvoice_cron.xml',
         'views/totalvoice_addnumber_view.xml',
         'views/res_users_views.xml',
         'views/res_partner_views.xml',
    ],
}
