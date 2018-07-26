# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'NFe Emissão Manual',
    'description': """
        Acessar o wizard 
        Localização Barsil -> Processamento periodico -> Importar NFes

        Quando a tela aparecer pode ser importados arquivos .xml ou .zip quem contenham .xml

        Serão alteradas as inforções da aba documento fiscal na fatura correspondente a nota processada. as informações alteradas são chave de acesso nfe, protocolo, status na sefaz, data do status nfe. 

        Para verificar ir em contabilidade->procurar pela fatura processada->aba do documento fiscal
        """,
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE INFORMATICA',
    'website': 'www.kmee.com.br',
    'depends': [
        'l10n_br_account_product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/importar_nfe_wizard.xml',
    ],
    'demo': [
    ],
}
