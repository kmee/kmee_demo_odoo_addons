    # -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - KMEE- Rafael da Silva Lima (<rafael.lima@kmee.com.br>)
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


import json, requests
#from pypedido import Pypedido
from wsgiref import headers


class Zerapedido(object):
    """
    Abaixo segue o esquemático para obter o id dos meus pedidos e a classe
    pool = pooler.get_pool(cr.dbname)
    obj_mapeado = pool.get('ir.model.data')
    obj_mapeado.get_object_reference(cr, uid, 'res.partner', partner.id)
    """

    def __init__(self, apptoken, comptoken, url):
        self.end_url = str(url)
        self.headers = {'Content-Type' : 'application/json',
                        'ApplicationToken' : apptoken,
                        'CompanyToken' : comptoken
                        }

    def getAtivo(self, tipo):
        url = "%sapi/v1/%s/" % (self.end_url, tipo)
        o = requests.get(url, headers= self.headers)
        if o.headers.get('meuspedidos_requisicoes_extras') != None:
            n_requests = int(o.headers['meuspedidos_requisicoes_extras'])
        else:
            n_requests = 0
        #itens = o.headers['meuspedidos_qtde_total_registros']
        objetos = o.json()
        ativos = []

        if objetos:
            ultimo = sorted(objetos, key=lambda k: k['ultima_alteracao'])[-1:][0]['ultima_alteracao']
            
            
            for item in objetos:
                if item['excluido'] == False:
                    ativos.append(item)
         
            for i in range(n_requests):
                objs = self.getObjetos(tipo, ultimo)
                if objs:
                    for item in objs:
                        if item['excluido'] == False:
                            ativos.append(item)
                ultimo = sorted(objetos, key=lambda k: k['ultima_alteracao'])[-1:][0]['ultima_alteracao']
            

            #print "Existem %s objetos e %s não estão excluidos" % (int(itens), len(ativos))
            if ativos:
                return ativos
            else:
                return False
        else:
            return False

    def getObjetos(self, tipo, alterado_apos = False):
        """
        A definir
        """
        objeto = []
        

        if not alterado_apos:
            url = "%sapi/v1/%s/" % (self.end_url, tipo)
            
            o = requests.get(url, headers= self.headers)
            res = o.json()

            return res
        else:

            url = '%sapi/v1/%s?alterado_apos=%s' % (self.end_url, tipo, alterado_apos)  
        
            o = requests.get(url, headers= self.headers)
            res = o.json()
 
            return res
            
    def delObjetos(self, tipo):

        ativos = self.getAtivo(tipo)

        if ativos:
            for item in ativos:
                url = "%sapi/v1/%s/%s/" % (self.end_url, tipo, item['id'])
                
                o = requests.put(url, data= json.dumps(item), headers= self.headers)
                print str(tipo) + " id: %s foi deletado" % item['id']
                print "Resp. servidor: ", o.status_code
        else:
            print "Não existem dados do tipo[%s] para serem removidos" % tipo
   
class Zera():
    zera = Zerapedido("c2e6b6b5-3128-4771-9c14-b8caf125f735",
                        "98a0f506-e201-4a66-9589-a79b223b180f",
                           "http://69.164.203.63:8080/")
  
    tipo = {
        '1': 'clientes',
        '2': 'produtos',
        '3': 'tabelas_preco',
        '4': 'produtos_tabela_preco',
        '5': 'transportadoras',
        '6': 'condicoes_pagamento',
        '7': 'formas_pagamento'
    }


    
    for item in tipo.keys():
        zera.delObjetos(tipo[item])