    # -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - KMEE- Luis Felipe Miléo (<http://www.kmee.com.br>)
#                               Rafael da Silva Lima (<rafael.lima@kmee.com.br>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#   123
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
from .meuspedidos.pypedido import Pypedido
from unicodedata import normalize
import re
import string
from datetime import datetime
import time




class sale_mobile_object(osv.osv):
    _name = "sale_mobile.object"
    _description = "Meus Pedidos - Vendas"
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

    def _config_data(self, cr, uid):

        pool = pooler.get_pool(cr.dbname)
        config_obj = pool.get('ir.config_parameter')

        data = {
            'apptoken': config_obj.get_param(cr, uid, 'meus_pedidos.apptoken'),
            'comptoken': config_obj.get_param(cr, uid, 'meus_pedidos.comptoken'),
            'url': config_obj.get_param(cr, uid, 'meus_pedidos.url'),
        }
        return data

    def mapping_objects(self, cr, uid, id, meuspedidosid, model, context=None):
        """
        Esta função irá mapear as ids entre objetos contidos
        nos Meus Pedidos, e poderam ser obtidos através da
        classe ir.model.data.
        """
        data = self._config_data(cr, uid)
        tipo = self.model_api(model)
        
        mobile_obj = Pypedido(
                                data['apptoken'], 
                                data['comptoken'], 
                                data['url']
                            )
        obj = self.search_objetcs(cr, uid, id, model, 1)
        active = mobile_obj.checkAtivo(tipo, meuspedidosid)

        if (not obj) and active:
            map_obj = self.pool.get('ir.model.data')

            values = {
        
                'name': str(meuspedidosid),
                'model': model,
                'module': 'kmee_sale_meuspedidos.' + model,
                'res_id': id,
                'noupdate': True,  # True para produção
            }

            
            ids = map_obj.create(cr, uid, values, context)
            print "Criou novo mapeamento id_meuspedidos_%d e id_openerp_%d" % (int(meuspedidosid), id)
            return ids
        else:
            print "Objeto já mapeado"
            return False
    
    def unmapping_objects(self, cr, uid, ids, context=None):

        map_obj = self.pool.get('ir.model.data')

        return map_obj.unlink(cr, uid, ids)


    def model_api(self, model):
        
        if isinstance(model, str):

            mod_api = {
            'res.partner': 'clientes',
            'product.product': 'produtos',
            'product.pricelist': 'tabelas_preco',
            'product.pricelist.product': 'produtos_tabela_preco',
            'delivery.carrier': 'transportadoras',
            'account.payment.term': 'condicoes_pagamento',
            'payment.type': 'formas_pagamento'
            }    

            return mod_api[model]
        else:
            return False
    
    def search_objetcs(self, cr, uid, id, model, origin, context=None):
        """
        origin: 1 para id do openerp e recebe a id dos meuspedidos
                2 para id dos meuspedidos e recebe a id do openerp
        """
        data = self._config_data(cr, uid)
        tipo = self.model_api(model)
        
        mobile_obj = Pypedido(
                                data['apptoken'], 
                                data['comptoken'], 
                                data['url']
                            )
        
        map_obj = self.pool.get('ir.model.data')
 
        modulo = 'kmee_sale_meuspedidos.' + model 
        
        if origin == 1:
            domain = [('module', '=', modulo),
                        ('model', '=', model),
                        ('res_id', '=', id)]

        if origin == 2:
            domain = [('module', '=', modulo),
                        ('model', '=', model),
                        ('name', '=', str(id))]
        
        obj_ids = map_obj.search(cr, uid, domain)
        
        
        #TODO: Obj com mais de 1 mapeamento, verificar quais ativos no meuspedidos e remover os duplicados
        obj = map_obj.read(cr, uid, obj_ids, ['name', 'res_id'])

        active = []
        inactive = []
        for objeto in obj:
            mp_id = str(objeto['name'])
            check = mobile_obj.checkAtivo(tipo, mp_id)
            if check:
                active.append(objeto)
            else:
                inactive.append(objeto['id'])

        # Cleaning inactive objects from ir.model.data
        self.unmapping_objects(cr, uid, inactive)

        
        if active:
            if origin == 1:    
                return int(active[0]['name'])
            elif origin == 2:
                return active[0]['res_id']
        else:
            return False

    def set_update(self, cr, uid, meuspedidosid, objeto, model, obj_date):
        
        data = self._config_data(cr, uid)

        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])

        tipo = self.model_api(model)

        objeto_mp = mobile_obj.getObjeto(tipo, meuspedidosid)
        
        if not objeto_mp:
            objeto_mp = {}
        
        # Formatação tempo OpenERP -> Meus Pedidos
        time_oerp = str(datetime.strptime(obj_date, '%Y-%m-%d %H:%M:%S' ))   
        
        if objeto_mp.get('ultima_alteracao') != None:
            time_mp =  normalize('NFKD', objeto_mp['ultima_alteracao']).encode('ascii','ignore')
        
            if time_oerp > time_mp:
                res = mobile_obj.setObjeto( tipo, meuspedidosid, objeto)
                if res.get('status') != None:
                    return True
            else:
                return False
        
    def translate_strings(self, tipo, valor):
        """
        tipo: cnpj, cpf , cep
        Esta função remove a pontuação contida nos dados  
        """
        valor = str(valor)
        dado = valor.translate(string.maketrans("", ""), string.punctuation)

        if tipo == "cnpj":
    
            if len(dado) < 14:
                dado = "0" + dado
                return dado
            else:
                return dado
        elif tipo == "cpf":
     
            if len(dado) < 11:
                dado = "0" + dado
                return dado
            else:
                return dado
        elif tipo == "cep":

            if len(dado) < 8:
                dado = "0" + dado
                return dado
            else:
                return dado
        else:
            return False

    
    def salesman_update(self, cr, uid, ids, context=None):
        """
        Insere Vendedores do Meus Pedidos no OpenERP
        Transferência unidirecional 
        OpenERP <- Meus Pedidos
        """

   
        data = self._config_data(cr, uid)
        
        mobile_obj = Pypedido(
                                data['apptoken'], 
                                data['comptoken'], 
                                data['url']
                            )

        obj_users = self.pool.get('res.users')
        domain = [('active', '=', True)]
        users_ids = obj_users.search(cr, uid, domain)
      
        for user in mobile_obj.getObjetos('usuarios'): 
            user_id = self.search_objetcs(cr, uid, user['id'], 'res.users', 2)

            if not user_id:
                if not user_id in users_ids and not user['excluido']:
                    vendedor_id = obj_users.create(cr, uid, {
                        'name': user['nome'],
                        'email': user['email'],
                        'phone': user['telefone'],
                        'in_group_51': user['administrador'],
                        'mobile': True,
                        'login': user['nome'].lower().replace(" ", "") + "_" + str(user['id']),
                    }, context=context)

                    if vendedor_id:
                        self.mapping_objects(cr, uid, vendedor_id, user['id'], 'res.users', context)
            else:
                print "Vendedor já mapeado"
                continue

        return True

    def product_update(self, cr, uid, ids, context=None):

        obj_product = self.pool.get('product.product')
   
        data = self._config_data(cr, uid)

        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])
        
        domain = [('active', '=', True)]
        produtos_ids = obj_product.search(cr, uid, domain)
        produtos_sync = [0, len(produtos_ids)]

        

        for id in produtos_ids:
                  
            prod_id = self.search_objetcs(cr, uid, id, 'product.product', 1)
            product = obj_product.browse(cr, uid, id, context)
                
            produto = {
                'codigo': product.default_code,
                'nome': product.name,
                'comissao': None,
                'preco_tabela': product.list_price,
                'ipi': None,
                'tipo': "P",
                'st': None,
                'grade_cores': None,
                'grade_tamanhos': None,
                'moeda': '0',
                'unidade': (product.uos_id.name or product.uom_id.name),
                'saldo_estoque': None,
                'observacoes': product.description,
                'excluido': False,
                
            }
            
            if not prod_id:    
            
                res = mobile_obj.addObjeto('produtos', produto)
                
                if res.get('resposta') != None:
                    print res['resposta']['mensagem']
                    for erro in res['resposta']['erros']:
                        print "Campo: ", erro['campo']
                        print "Mensagem: ", erro['mensagem']
                        print "Produto id: ", id
                else:
                    if res['status'] in [200, 201]:
                        obj_product.write(cr, uid, product.id, 
                            {
                                'write_date': res['ultima_alteracao']
                            })
                    
                    produtos_sync[0] += 1
                    self.mapping_objects(cr, uid, product.id, res['meuspedidosid'], 'product.product', context)
                              
            else:
                self.set_update(cr, uid, prod_id, produto,'product.product', product.write_date)
                
        print "Produtos Sincronizados - %d/%d produtos" % (produtos_sync[0], produtos_sync[1])
        return True

    


    def price_update(self, cr, uid, ids, context=None):
         
        if not context:
            context = {}

    
        
        data = self._config_data(cr, uid)
        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])
        obj_price_list = self.pool.get('product.pricelist')
#         domain = [('active', '=', True), ('type', '=', 'sale')]
        obj_product = self.pool.get('product.product')
        
        domain = [('active', '=', True),
                 ('type', 'in',
                 ['product', 'consu'])]                  
              
        id_tabela = None
        
            
        for price_list_id in obj_price_list.search(cr, uid, [('type', '=', 'sale')]):
            
            
            price_list_map = self.search_objetcs(cr, uid, price_list_id, 'product.pricelist', 1)
                
                
            if not price_list_map:
                
                
                price_list = obj_price_list.browse(cr, uid, price_list_id, context)
                                                     
                if not price_list_map: 
                                   
                    tabela_preco = {
                        'nome': price_list.name,
                        'tipo': 'P',
                        'excluido': False,
                    }
                    
                    res = mobile_obj.addObjeto('tabelas_preco', tabela_preco)          
                               
                    if res:
                        id_tabela = int(res['meuspedidosid'])
                        self.mapping_objects(cr, uid, price_list_id,
                               res['meuspedidosid'], 'product.pricelist', context)         
                else:
                    id_tabela = price_list_map  
                            
                for prod_id in obj_product.search(cr, uid, domain):

                    price_dict = obj_price_list.price_get(cr, uid, [price_list_id], prod_id, qty=0)

                    product_map = self.search_objetcs(cr, uid, prod_id, 'product.product', 1)
                              
                    price_list_prod_id = int(str(price_list_id) + str(prod_id))
                      
                    product_pricelist_product_map = self.search_objetcs(cr, uid, price_list_prod_id, 'product.pricelist.product',1)

                    if (not product_pricelist_product_map) and id_tabela: 
                        
                        if price_dict[price_list_id]:
                            price = price_dict[price_list_id]
        
                            tabela_preco_produto = {
                                 'preco': ('%.2f' % (price)).replace('.', ','),
                                 'tabela_id': id_tabela ,
                                 'produto_id': product_map,
                                 'excluido': False,
                                 
                                 }
    
                            res = mobile_obj.addObjeto('produtos_tabela_preco', tabela_preco_produto)
                                          
                            if res.get('meuspedidosid') != None:
                                self.mapping_objects(cr, uid, price_list_prod_id,
                                                    res['meuspedidosid'], 'product.pricelist.product', context)
            else:
                print "Lista de preço já mapeada"
                continue

        return True


    def partner_update(self, cr, uid, ids, context=None):

        novo_cliente_id = 0
        obj_partner = self.pool.get('res.partner')

        domain = [('customer', '=', True)]
        
        data = self._config_data(cr, uid)

        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])

   
        clientes_ids = obj_partner.search(cr, uid, domain)
        
        clientes_sync = [0, len(clientes_ids)]
        
        
        for id in clientes_ids:
            
            cliente_map = self.search_objetcs(cr, uid, id, 'res.partner', 1)
            partner = obj_partner.browse(cr, uid, id, context)

            if partner.is_company:
                tipo_cliente = "J"
                cnpj_novo = self.translate_strings("cnpj", partner.cnpj_cpf)
            else:
                tipo_cliente = "F"
                cnpj_novo = self.translate_strings("cpf", partner.cnpj_cpf)

            cep_novo = self.translate_strings("cep", partner.zip)

            rua_end = partner.street or " "
            rua_end += " " + str(partner.number)

            cliente = {

                'razao_social': partner.legal_name,
                'nome_fantasia': partner.name,
                'tipo': tipo_cliente,
                'cnpj': cnpj_novo,
                'inscricao_estadual': partner.inscr_est,
                'suframa': partner.suframa,
                'rua': rua_end,
                'complemento': partner.street2,
                'cep': cep_novo,
                'bairro': partner.district,
                'cidade': partner.city,
                'estado': partner.state_id.code,
                'observacao': partner.comment,
                'emails': [{'email': partner.email }],
                'telefones': [{'numero': partner.phone}],
                'contatos':[],
                'excluido': False,
                
            }

            if not cliente_map:

                res = mobile_obj.addObjeto('clientes', cliente)
                
                if res.get('resposta'):
                    print res['resposta']['mensagem']
                    for erro in res['resposta']['erros']:
                        print "Campo: ", erro['campo']
                        print "Mensagem: ", erro['mensagem']
                        print "Cliente id: ", partner.id
                else:
                    if res['status'] in [200, 201]:
                        obj_partner.write(cr, uid, partner.id, 
                            {
                                'write_date': res['ultima_alteracao']
                            })
                    clientes_sync[0] += 1 
                    self.mapping_objects(cr, uid, partner.id, res['meuspedidosid'],
                    'res.partner', context)
            else:
                self.set_update(cr, uid, cliente_map, cliente, 'res.partner', partner.write_date)
                

        print "Clientes Enviados - %d/%d clientes" % (clientes_sync[0], clientes_sync[1])
        clientes_sync = [0, len(clientes_ids)]
        
        users = mobile_obj.getObjetos('clientes')

        for user in users:
            
            if (not user['id'] in clientes_ids) and (not user['excluido']):
               
                email = ""
                numero = ""
                for item in user['emails']:
                    if 'email' in item.keys():
                        email += item['email'] + ', '

                for item in user['telefones']:
                    if 'numero' in item.keys():
                        numero += item['numero'] + ', '

                novo_cliente_id = obj_partner.create(cr, uid, {
                    'legal_name': user['razao_social'],
                    'name': user['nome_fantasia'],
                    'is_company': user['tipo'],
                    'cnpj_cpf': user['cnpj'],
                    'inscr_est': user['inscricao_estadual'],
                    'suframa': user['suframa'],
                    'street': user['rua'].rsplit(' ', 1)[0],
                    'number': user['rua'].rsplit(' ', 1)[1],
                    'street2': user['complemento'],
                    'zip': user['cep'],
                    'district': user['bairro'],
                    'city': user['cidade'],
                    'state_id.code': user['estado'],
                    'comment': user['observacao'],
                    'email': email,
                    'phone': numero,
                    'date': user['ultima_alteracao'],
                }, context= context)


                if novo_cliente_id:
                    clientes_sync[0] += 1 
                    self.mapping_objects(cr, uid, novo_cliente_id, user['id'],
                                        'res.partner', context)
                
        print "Clientes Recebidos - %d/%d clientes" % (clientes_sync[0], clientes_sync[1])
                         
        return True

    def delivery_update(self, cr, uid, ids, context=None):

        obj_delivery_carrier = self.pool.get('delivery.carrier')

        data = self._config_data(cr, uid)

        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])

        transp_ids = obj_delivery_carrier.search(cr, uid, [])

        

        for id in transp_ids:

            delivery_carrier = obj_delivery_carrier.browse(cr, uid, id, context)

            carrier = delivery_carrier.partner_id

            transp_map = self.search_objetcs(cr, uid, carrier.id, 'delivery.carrier', 1)
            
            transportadora = {
                
                'nome': str(carrier.name),
                'cidade': str(carrier.city),
                'estado': str(carrier.state_id.code),
                'informacoes_adicionais': str(carrier.comment),  # BUG: Restornando FALSE
                'telefones': str(carrier.phone),
                'excluido': False,
               
                }    

            if (not transp_map) and (transportadora['estado'] != "None"):
  
                res = mobile_obj.addObjeto('transportadoras', transportadora)

                if res.get('resposta'):
                #Debug 
                    print res['resposta']['mensagem']
                    for erro in res['resposta']['erros']:
                        print "Campo: ", erro['campo']
                        print "Mensagem: ", erro['mensagem']
                        print "Transportadora id: ", carrier.id
                else:
                    if res['status'] in [200, 201]:
                        delivery_carrier.write(cr, uid, carrier.id, 
                            {
                                'write_date': res['ultima_alteracao']
                            })
                    self.mapping_objects(cr, uid, carrier.id, res['meuspedidosid'],
                    'delivery.carrier', context)
            else:
                self.set_update(cr, uid, transp_map, transportadora, 'delivery.carrier', carrier.write_date)

        transp_meuspedidos = mobile_obj.getObjetos('transportadoras')

        for transp in transp_meuspedidos:

            id_transp = self.search_objetcs(cr, uid, transp['id'], 'delivery.carrier', 2)

            if (not id_transp in transp_ids) and (not transp['excluido']):
                    nova_transp_id = obj_delivery_carrier.create(cr, uid, {
                        'name': transp['nome'],
                        'city': transp['cidade'],
                        'state_id.code': transp['estado'],
                        'comment': transp['informacoes_adicionais'],
                        'phone': transp['telefones'],
                        }, context=context)

            if nova_transp_id:
                self.mapping_objects(cr, uid, carrier.id, transp['id'], 'delivery.carrier', context)
                
        return True

    def payment_type_update(self, cr, uid, ids, context=None):

        global novo_paytype_id

        obj_payment_type = self.pool.get('payment.type')

        data = self._config_data(cr, uid)

        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])

        payment_ids = obj_payment_type.search(cr, uid, [])

        
        for id in payment_ids:

            payment_type = obj_payment_type.browse(cr, uid, id, context)

            obj_price_list = self.pool.get('product.pricelist')
            domain = [('active', '=', True), ('type', '=', 'sale')]
            price_ids = obj_price_list.search(cr, uid, domain)

            for ids in  price_ids:

                obj_mapeado = self.search_objetcs(cr, uid, payment_type.id, 'payment.type', 1)
                    
                if not obj_mapeado:

                    cobranca = {
                    'id': payment_type.id,
                    'nome': payment_type.name,
                    'excluido': False,
                  
                    }

                    res = mobile_obj.addObjeto('formas_pagamento', cobranca)
                    if res:
                        self.mapping_objects(cr, uid, payment_type.id,
                                 res['meuspedidosid'], 'payment.type', context)
                else:
                    print "Forma de pagamento já mapeada"
                    continue
                
            paytype_meuspedidos = mobile_obj.getObjetos('formas_pagamento')
            
            for paytype in paytype_meuspedidos:
                pay_map = self.search_objetcs(cr, uid, paytype['id'], 'payment.type', 2)

                if (not pay_map == payment_type.id) and (not paytype['excluido']):
                        novo_paytype_id = obj_payment_type.create(cr, uid, {
                            'name': paytype['nome'],
                            }, context=context)

                        if novo_paytype_id:
                            self.mapping_objects(cr, uid, payment_type.id, paytype['id'], 'payment.type', context)
                else:
                    print "Condição de pagamento dos meus pedidos já mapeada"
                    continue
        return True

    def payment_terms_update(self, cr, uid, ids, context=None):
        

        novo_payterm_id = 0
        data = self._config_data(cr, uid)

        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])

        obj_payment_terms = self.pool.get('account.payment.term')

        domain = [('active', '=', True), ('mobile', '=', True)]
        payterms_ids = obj_payment_terms.search(cr, uid, domain)

        for id in payterms_ids:
            
            term = obj_payment_terms.browse(cr, uid, id, context)

            obj_mapeado = self.search_objetcs(cr, uid, term.id, 'account.payment.term', 1)
            
            vencimento = {
                'id': term.id,
                'nome': term.name,
                'excluido': False,
                
                }
               
            if not obj_mapeado:
   
                res = mobile_obj.addObjeto('condicoes_pagamento', vencimento)

                if res:
                    self.mapping_objects(cr, uid, term.id,
                             res['meuspedidosid'], 'account.payment.term', context)
            else:
                print "Condição de pagamento já mapeada"
                continue

        payterm_meuspedidos = mobile_obj.getObjetos('condicoes_pagamento')
        

        for payterm in payterm_meuspedidos:
            pay_id = self.search_objetcs(cr, uid, payterm['id'], 'account.payment.term', 2)
            if not pay_id:
               
                novo_payterm_id = obj_payment_terms.create(cr, uid, {
                    'name': payterm['nome'],
                    }, context=context)
                
                if novo_payterm_id:
                    print "Criou mapeamento de recebido"
                    self.mapping_objects(cr, uid, term.id,
                                 payterm['id'], 'account.payment.term', context)
            else:
                print "Condição de pagamento dos meus pedidos já mapeada"
                continue

        return True

    def _add_sale(self, cr, uid, ids, context, pedidos):
       
        if not context:
            context = {}

        obj_users = self.pool.get('res.users')
        obj_partner = self.pool.get('res.partner')
        obj_sale = self.pool.get('sale.order')

        data = self._config_data(cr, uid)

        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])

        obj_mapeado = self.pool.get('ir.model.data')

        for pedido in pedidos:
            itens = pedido['items']
            
            company_id = 1 
            partner_id = self.search_objetcs(cr, uid, pedido['cliente_id'], 'res.partner', 2)
            partner_invoice_id = partner_id
            partner_shipping_id = partner_id
            pricelist_id = 1
            shop_id = 1 

            res_partner = obj_partner.browse(cr, uid, partner_id , context=context)

            sale_id = obj_sale.create(cr, uid, {
                'partner_id' :partner_id,
                'partner_invoice_id' : partner_id,
                'partner_shipping_id': partner_id,
                'shop_id': shop_id,
                'pricelist_id': pricelist_id,
                'note': pedido['observacoes'],
                'payment_term' : 3,  # TODO: São codigos não dias int(pedido['condicao_pagamento'][:-4])
                'origin':'sale_mobile',
                'client_order_ref': pedido['numero'],

                }, context=context)

            self.mapping_objects(cr, uid, sale_id, pedido['id'], 'sale.order')

            fiscal_category_id = obj_sale._default_fiscal_category(cr, uid, context=context)

            
            fiscal_position = obj_sale.onchange_address_id(cr, uid, ids,
                 partner_invoice_id, partner_shipping_id, partner_id, shop_id,
                 context, fiscal_category_id=fiscal_category_id)['value']['fiscal_position']
                 
            obj_sale.write(cr, uid, sale_id, {
                'fiscal_category_id': fiscal_category_id,
                'fiscal_position': fiscal_position,
                }, context=context)

            sale_order = obj_sale.browse(cr, uid, sale_id, context=context)

            
            for item in itens:
                
                
                sale_order_line = self.pool.get('sale.order.line')
                product_obj = self.pool.get('product.product')
                product = product_id = 0
                
                mapeado = self.search_objetcs(cr, uid, item['produto_id'], 'product.product', 2)
                
                if mapeado:
                    product = product_id = mapeado['res_id']
                else:
                    print "Item produto não mapeado"
                    continue
                
            
                product_uom_qty = qnt = qty = float(item['quantidade'])
                price_unit = item['preco_liquido']
                date_order = fields.date.context_today(self, cr, uid)
                pricelist = 1
                
                context['parent_fiscal_category_id'] = fiscal_category_id
                context['shop_id'] = shop_id
                context['partner_invoice_id'] = partner_invoice_id
                
                line_tax = sale_order_line.product_id_change(cr, uid, [], pricelist,
                    product, qty=0, uom=False, qty_uos=0, uos=False, name='',
                    partner_id=partner_id, lang=False, update_tax=True,
                    date_order=date_order, packaging=False,
                    fiscal_position=fiscal_position, flag=False, context=context            
                    )
                
                
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
                
                sale_order_line.create(cr, uid, order_line)
                
        return True

    def import_moviments(self, cr, uid, ids, context=None):

        data = self._config_data(cr, uid)
        
        mobile_obj = Pypedido(data['apptoken'], data['comptoken'], data['url'])
        
        pedidos = mobile_obj.getObjetos("pedidos")
        pedidos_ok = []

        if not pedidos:
            return False

        else:
            for pedido in pedidos:
                
                mapeado = self.search_objetcs(cr, uid, pedido['cliente_id'], 'res.partner', 2)
                
                if not mapeado:
                    print "Pedido com cliente não encontrado"
                    continue
                else:
                    pedidos_ok.append(pedido)
                
            if pedidos_ok: 
                self._add_sale(cr, uid, ids, context, pedidos_ok)

        return True