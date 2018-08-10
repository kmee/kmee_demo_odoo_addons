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
    'depends': ['base', 'webhook'],
    'data': [
         'views/totalvoice_base_view.xml',
         'views/totalvoice_webhook.xml',
         'views/totalvoice_config_view.xml'
    ],
}
