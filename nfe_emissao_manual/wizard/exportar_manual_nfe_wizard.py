# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import time
import base64
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

from openerp.addons.nfe.sped.nfe.processing.certificado import Certificado
from openerp.addons.nfe.sped.nfe.processing.processor import ProcessadorNFe


class L10nBrAccountNfeExportInvoice(models.TransientModel):
    """ Export fiscal eletronic file from invoice"""
    _inherit = 'l10n_br_account_product.nfe_export_invoice'

    @api.multi
    def nfe_export(self):
        for data in self:
            active_ids = self._context.get('active_ids', [])

            if not active_ids:
                err_msg = (u'Não existe nenhum documento fiscal para ser'
                           u' exportado!')
            export_inv_ids = []
            export_inv_numbers = []
            company_ids = []
            err_msg = ''

            for inv in self.env['account.invoice'].browse(active_ids):
                if inv.state not in ('sefaz_export'):
                    err_msg += (u"O Documento Fiscal %s não esta definida para"
                                u" ser exportação "
                                u"para a SEFAZ.\n") % inv.internal_number
                elif not inv.issuer == '0':
                    err_msg += (u"O Documento Fiscal %s é do tipo externa e "
                                u"não pode ser exportada para a "
                                u"receita.\n") % inv.internal_number
                else:
                    inv.write({
                        'nfe_export_date': False,
                        'nfe_access_key': False,
                        'nfe_status': False,
                        'nfe_date': False
                    })

                    message = "O Documento Fiscal %s foi \
                        exportado." % inv.internal_number
                    inv.log(message)
                    export_inv_ids.append(inv.id)
                    company_ids.append(inv.company_id.id)

                export_inv_numbers.append(inv.internal_number)

            if len(set(company_ids)) > 1:
                err_msg += (u'Não é permitido exportar Documentos Fiscais de '
                            u'mais de uma empresa, por favor selecione '
                            u'Documentos Fiscais da mesma empresa.')

            if export_inv_ids:
                if len(export_inv_numbers) > 1:
                    name = 'nfes%s-%s.%s' % (
                        time.strftime('%d-%m-%Y'),
                        self.env['ir.sequence'].get('nfe.export'),
                        data.file_type)
                else:
                    name = 'nfe%s.%s' % (export_inv_numbers[0],
                                         data.file_type)

                mod_serializer = __import__(
                    ('openerp.addons.l10n_br_account_product'
                     '.sped.nfe.serializer.') +
                    data.file_type, globals(), locals(), data.file_type)

                func = getattr(mod_serializer, 'nfe_export')

                str_nfe_version = inv.nfe_version

                nfes = func(self._cr, self._uid, export_inv_ids,
                            data.nfe_environment, str_nfe_version,
                            self._context)

                for nfe in nfes:

                    company = inv.company_id

                    p = ProcessadorNFe(company)
                    p.ambiente = int(company.nfe_environment)
                    p.estado = company.partner_id.l10n_br_city_id.state_id.code
                    p.certificado = Certificado(company)
                    p.salvar_arquivos = True
                    p.contingencia_SCAN = False

                    nfe_obj = inv._get_nfe_factory(inv.nfe_version)
                    nfe = nfe_obj.set_xml(nfe['nfe'])

                    p.certificado.assina_xmlnfe(nfe)

                    nfe_file = nfe.xml.encode('utf8')

                data.write({
                    'file': base64.b64encode(nfe_file),
                    'state': 'done',
                    'name': name,
                })

            if err_msg:
                raise UserError(_('Error!'), _("'%s'") % _(err_msg, ))

            view_rec = self.env['ir.model.data'].get_object_reference(
                'l10n_br_account_product',
                'l10n_br_account_product_nfe_export_invoice_form')
            view_id = view_rec and view_rec[1] or False

            return {
                'view_type': 'form',
                'view_id': [view_id],
                'view_mode': 'form',
                'res_model': 'l10n_br_account_product.nfe_export_invoice',
                'res_id': data.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': data.env.context,
            }
