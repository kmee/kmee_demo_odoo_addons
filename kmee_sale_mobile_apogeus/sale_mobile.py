    # -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - KMEE- Luis Felipe Miléo (<http://www.kmee.com.br>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _

from unicodedata import normalize
import re
from string import punctuation
from datetime import datetime
import time
try:
    from pyapogeus.apogeus import Apogeus
except ImportError:
    import logging
    _logger = logging.getLogger(__name__)
    _logger.info('Cannot import pyapogeus')


class sale_mobile_object(osv.osv):
    _name = "sale_mobile.object"
    _description = "Apogeus Sales Mobile"
    _columns = {
            'state': fields.selection([
            ('done', 'OK'),
            ('error', 'Error'),
            ('warning', 'Warning')
            ], 'Status', select=True, readonly=True,
            help='Status dos processamentos'),
        'table_name': fields.char("Tabela", size=64, required=True, select=1),
        'description': fields.char("Descrição", size=64, required=True,
        select=1),
        'file_name': fields.char("Name", size=64, required=True, select=1)
        }


class sale_mobile_export(osv.osv):

    _name = "sale_mobile.process"
    _description = "Sales Process"

    def salesman_update(self, cr, uid, ids, context=None): #tbven.txt

        if not context:
            context = {}

        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id

        try:
            group_id = self.pool.get('ir.model.data').get_object_reference(cr,
                uid, 'sale_mobile', 'group_sale_mobile')[1]
        except:
            return False

        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')
        save_dir = config_obj.get_param(cr, uid, 'sale_mobile.dir.save').format(cr.dbname)
        mobile_obj = Apogeus(company_id, 1, False, save_dir)


        obj_users = self.pool.get('res.users')

        for id in obj_users.search(cr, uid, [('groups_id.id', '=', group_id)]):
            user = obj_users.browse(cr, uid, id, context)

            vendedor = {
                'codigo_filial': company_id,
                'codigo_vendedor': user.id,
                'nome_vendedor': user.name,
                'transmite_flex_negativo': "N",
            }

            mobile_obj.addVendedor(vendedor)
        return mobile_obj.save_tbven

    def product_update(self, cr, uid, ids, context=None):
        #tbpro.txt

        if not context:
            context = {}

        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id

        obj_product = self.pool.get('product.product')

        domain = [('sale_ok', '=', True), ('active', '=', True),
            ('fiscal_type', '=', 'product'), ('type', 'in',
            ['product', 'consu'])]

        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')
        save_dir = config_obj.get_param(cr, uid, 'sale_mobile.dir.save').format(cr.dbname)
        mobile_obj = Apogeus(company_id, 1, False, save_dir)

        for id in obj_product.search(cr, uid, domain):
            product = obj_product.browse(cr, uid, id, context)

            produto = {
                'codigo_filial': company_id,
                'codigo_produto': product.id,
                'descricao_produto':  normalize('NFKD',unicode(product.name)).encode('ASCII','ignore'),
                'unidade': (product.uos_id.name or product.uom_id.name),
                'codigo_grupo': product.categ_id.id,
                'descricao_grupo': normalize('NFKD',unicode(product.categ_id.name)).encode('ASCII','ignore'),
                'peso_kg': (int(('%.3f' % (product.weight_net)).replace('.', ''))) ,
                'multiplo': 100,
                'data_alteracao': datetime.strptime(product.write_date, '%Y-%m-%d %H:%M:%S' ),
                'situacao_resigistro': 'N',
                'observacao_produto': normalize('NFKD',unicode( product.description_sale or '')).encode('ASCII','ignore'),
                'quantidade_varejo': 1,
            }

            mobile_obj.addProduto(produto)
        return mobile_obj.save_tbpro

    def partner_update(self, cr, uid, ids, context=None):
        #tbcli.txt

        if not context:
            context = {}
        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id

        obj_partner = self.pool.get('res.partner')

        domain = [('customer', '=', True), ('active', '=', True), ('user_id','!=', False)]

        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')
        save_dir = config_obj.get_param(cr, uid, 'sale_mobile.dir.save').format(cr.dbname)
        mobile_obj = Apogeus(company_id, 1, False, save_dir)

        for id in obj_partner.search(cr, uid, domain):

            partner = obj_partner.browse(cr, uid, id, context)

            cliente = {
                'codigo_filial': company_id,
                'codigo_cliente': partner.id,
                'razao_social': normalize('NFKD',unicode(partner.legal_name or '')).encode('ASCII','ignore'),
                'nome_fantasia': normalize('NFKD',unicode(partner.name or '')).encode('ASCII','ignore'),
                'endereco': normalize('NFKD',unicode(partner.street or '')).encode('ASCII','ignore'),
                'bairro': normalize('NFKD',unicode(partner.district or '')).encode('ASCII','ignore'),
                'cidade': normalize('NFKD',unicode(partner.city or '')).encode('ASCII','ignore'),
                'numero_endereco': normalize('NFKD',unicode(partner.number or '' )).encode('ASCII','ignore'),
                'uf': partner.state_id.code or '',
                'bloqueado': "N",
                'altera_pauta': "S",
                'vendedor1': partner.user_id.id,
                'altera_pauta': 'S',
                'altera_cobranca': 'I',
                'altera_coluna': 'S',
                'altera_vencimento': 'I',
                'consumidor_final': 'N',
                'fisico_juridico':'J',
                'cnpj_cpf': normalize('NFKD',unicode((re.sub('[%s]' % re.escape(punctuation), '', partner.cnpj_cpf or '')))).encode('ASCII','ignore'),
            }
            mobile_obj.addCliente(cliente)

        return mobile_obj.save_tbcli

    def payment_type_update(self, cr, uid, ids, context=None):
        #tbcob
        if not context:
            context = {}
        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id
        obj_payment_type = self.pool.get('payment.type')

        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')
        save_dir = config_obj.get_param(cr, uid, 'sale_mobile.dir.save').format(cr.dbname)
        mobile_obj = Apogeus(company_id, 1, False, save_dir)

        for id in obj_payment_type.search(cr, uid, []):
            payment_type = obj_payment_type.browse(cr, uid, id, context)

            obj_price_list = self.pool.get('product.pricelist')
            domain = [('active', '=', True), ('type', '=', 'sale')]
            for ids in  obj_price_list.search(cr, uid, domain):
                cobranca = {
                    'codigo_tipo_cobranca': payment_type.id,
                    'descricao_cobranca': payment_type.name,
                    'codigo_filial': company_id,
                    'coluna_precos_pauta': '01',
                    'codigo_pauta_precos': '1',
                }
                mobile_obj.addCobranca(cobranca)
        return mobile_obj.save_tbcob

    def payment_terms_update(self, cr, uid, ids, context=None):
        #tbven.txt
        if not context:
            context = {}
        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id

        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')
        save_dir = config_obj.get_param(cr, uid, 'sale_mobile.dir.save').format(cr.dbname)
        mobile_obj = Apogeus(company_id, 1, False, save_dir)

        obj_payment_terms = self.pool.get('account.payment.term')

        domain = [('active', '=', True), ('mobile', '=', True)]

        for id in obj_payment_terms.search(cr, uid,domain):
            term = obj_payment_terms.browse(cr, uid, id, context)

            vencimento = {
                'codigo_filial': company_id,
                'codigo_pauta_precos': '1',
                'codigo_vencimento': term.id,
                'coluna_precos_pauta': '01',
                'descricao_vencimento': normalize('NFKD',unicode( term.name)).encode('ASCII','ignore'),
                'codigo_cobranca': '001',
                'nomero_parcelas': len(term.line_ids),
            }
            #TODO arrumar codigo cobranca
            mobile_obj.addVencimento(vencimento)
        return mobile_obj.save_tbvct

    def price_update(self, cr, uid, ids, context=None):

        if not context:
            context = {}

        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id
        try:
            group_id = self.pool.get('ir.model.data').get_object_reference(cr,
                uid, 'sale_mobile', 'group_sale_mobile')[1]
        except:
            return False

        obj_users = self.pool.get('res.users')
        user_ids = obj_users.search(cr, uid, [('groups_id.id', '=', group_id)])

        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')
        save_dir = config_obj.get_param(cr, uid, 'sale_mobile.dir.save').format(cr.dbname)
        mobile_obj = Apogeus(company_id, 1, False, save_dir)

        obj_product = self.pool.get('product.product')

        obj_price_list = self.pool.get('product.pricelist')
        domain = [('active', '=', True), ('type', '=', 'sale')]


        for ids in  obj_price_list.search(cr, uid, domain):

            ids = [ids]
            domain = [('sale_ok', '=', True), ('active', '=', True),
                ('fiscal_type', '=', 'product'), ('type', 'in',
                ['product', 'consu'])]

            for prod_id in obj_product.search(cr, uid, domain):
                price = obj_price_list.price_get(cr, uid, ids , prod_id, qty=0)

                product = obj_product.browse(cr, uid, prod_id, context)

                preco = {
                    'codigo_filial': company_id,
                    'codigo_produto': prod_id,
                    'preco_venda1': (int(('%.2f' % (price[ids[0]])).replace('.', ''))),
                    'saldo_estoque': (int(('%.3f' % (product.qty_available)).replace('.', ''))),
                    'codigo_pauta_precos': ids[0],
                    'tipo_produto': 'N',
                    'desconto_maximo':'01000',
                    }
                mobile_obj.addPreco(preco)
            mobile_obj.save_tbpre
            list_price = obj_price_list.browse(cr, uid, ids[0], context)

            for user in user_ids:
                pauta = {
                    'codigo_filial': company_id,
                    'codigo_vendedor': user,
                    'codigo_pauta_precos': ids[0],
                    'descricao_pauta': normalize('NFKD',unicode(list_price.name)).encode('ASCII','ignore'),
                    'data_inicial': "01011999",
                    'data_final': "01012999",
                    'controla_flex': "N",
                    'acumulador_limitador_flex_negativo': 'N',
                    'acumulador_limitador_flex_positivo': 'N',
                    'permitir_flex_negativo': 'N',
                    'adiciona_desconto_saldo_flex': 'N',
                    'subtrai_desconto_saldo_flex': 'N',
                    }
                mobile_obj.addPauta(pauta)

            mobile_obj.save_tbpta
            prazo_pauta = {
                'codigo_filial': company_id,
                'coluna_preco_pauta': '01',
                'descritivo_coluna_precos': 'Prazo Pauta',
                'codigo_pauta_precos': ids[0],
                }

            mobile_obj.addPrazoPauta(prazo_pauta)

        return mobile_obj.save_tbprp

    def _add_sale(self, cr, uid, ids, context, data):

        if not context:
            context = {}

        obj_users = self.pool.get('res.users')
        obj_partner = self.pool.get('res.partner')
        obj_sale = self.pool.get('sale.order')

        for pedido in data.keys():
            sale =  data[pedido]['pedido']
            itens = data[pedido]['itens']
            payment = data[pedido]['prazo']

            company_id = int(sale['codigo_filial'])
            partner_id = int(sale['codigo_cliente'])
            partner_invoice_id = partner_id
            partner_shipping_id = partner_id
            pricelist_id = sale['codigo_pauta_precos']
            shop_id = 1
            user_id = int(sale['codigo_vendedor'])

            res_partner = obj_partner.browse(cr, uid, partner_id , context=context)

            sale_id = obj_sale.create(cr, uid, {
                'partner_id' :partner_id,
                'partner_invoice_id' : partner_id,
                'partner_shipping_id': partner_id,
                'shop_id' :shop_id,
                'pricelist_id': pricelist_id,
                'user_id' : user_id,
                'note': (sale['observacao_pedido'] or '').decode('UTF-8','ignore'),
                'payment_term' : int(sale['codigo_vencimento']),
                'origin':'sale_mobile',
                'client_order_ref': sale['numero_pedido'],
                #'fiscal_position'
                #'client_order_ref'
                #'picking_ids'
                #'state'
                #'currency_id'
                #'portal_payment_options'
                #'carrier_id'
                #'order_line'
                #'amount_untaxed'
                #'amount_tax'
                #'amount_total'
                #'invoiced'
                #'shipped'
                #'invoice_exists'
                #'invoice_exists'
                #'project_id'
                #'message_follower_ids'
                #'message_ids'
                }, context=context)

            fiscal_category_id = obj_sale._default_fiscal_category(cr, uid,
                context=context)

            fiscal_position = obj_sale.onchange_address_id(cr, uid, ids,
                 partner_invoice_id, partner_shipping_id, partner_id, shop_id,
                 context, fiscal_category_id)['value']['fiscal_position']
            obj_sale.write(cr, uid, sale_id, {
                'fiscal_category_id': fiscal_category_id,
                'fiscal_position': fiscal_position,
                }, context=context)

            sale_order = obj_sale.browse(cr, uid, sale_id, context=context)

            for item in itens:
                sale_order_line = self.pool.get('sale.order.line')
                product_obj = self.pool.get('product.product')
                product = product_id = int(item['codigo_produto'])
                product_uom_qty = qnt = qty =  float(item['quantidade'])
                price_unit = item['valor_venda']
                date_order = fields.date.context_today(self,cr,uid)
                pricelist = 1

                line_tax = sale_order_line.product_id_change(cr, uid,[],pricelist,
                     product, qty=0, uom=False, qty_uos=0, uos=False, name='',
                     partner_id=partner_id, lang=False, update_tax=True,
                     date_order=date_order, packaging=False,
                     fiscal_position=False, flag=False, context=context,
                     parent_fiscal_category_id=fiscal_category_id, shop_id=shop_id,
                     parent_fiscal_position=False,
                     partner_invoice_id=partner_invoice_id)

                onchange_fiscal_category_id = sale_order_line.onchange_fiscal_category_id(cr, uid,
                    [], partner_id, partner_invoice_id, shop_id, product_id,
                    fiscal_category_id=line_tax['value']['fiscal_category_id'],
                    context=context)

                onchange_fiscal_position = sale_order_line.onchange_fiscal_position(cr, uid, ids,
                     partner_id, partner_invoice_id, shop_id, product_id,
                     fiscal_position=onchange_fiscal_category_id['value']['fiscal_position'],
                     fiscal_category_id=line_tax['value']['fiscal_category_id'])

                order_line = {
                    'order_id': sale_id,
                    'price_unit': price_unit,
                    'product_uom_qty': product_uom_qty,
                    'name': line_tax['value']['name'],
                    'product_uom': line_tax['value']['product_uom'],
                    'product_id': product_id,
                    'fiscal_category_id': line_tax['value']['fiscal_category_id'],
                    'fiscal_position': onchange_fiscal_position['value']['fiscal_position'],
                     'tax_id': [(6, 0, onchange_fiscal_position['value']['tax_id'])]
                }
                line_id = sale_order_line.create(cr, uid, order_line)
        return True

    def _add_crm():
        if not context:
            context = {}

        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id

    def _add_partner():
        if not context:
            context = {}

        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id

    def _add_message():
        if not context:
            context = {}

        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id

    def import_moviments(self, cr, uid, ids, context=None):
        if not context:
            context = {}

        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id
        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')
        read_dir = config_obj.get_param(cr, uid, 'sale_mobile.dir.read').format(cr.dbname)
        mobile_obj = Apogeus(company_id, 2, read_dir, False)

        data = mobile_obj.getData()

        if not data:
            return False

        if data['pedidos']:
            self._add_sale(cr, uid, ids, context, data['pedidos'])
        #if data['nao_venda']:
            #add_crm(data['nao_venda'])
        #if data['clientes']:
            #add_partner(data['clientes'])
        #if data['mensagens']:
            #add_message(data['messagens'])
        return True