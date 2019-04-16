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
from datetime import datetime
from wsgiref import headers



class Pypedido(object):
    """
    Esta classe comunica-se com a API dos MeusPedidos de acordo
    com o Manual versão 0.3
     
    """

    def __init__(self, apptoken, comptoken, url):
        self.end_url = str(url)
        self.headers = {'Content-Type' : 'application/json',
                        'ApplicationToken' : apptoken,
                        'CompanyToken' : comptoken
                        }
    
    def addObjeto(self, tipo, objeto):
        
        url = "%sapi/v1/%s/" % (self.end_url, tipo)
        
        o = requests.post(url, data=json.dumps(objeto), headers= self.headers)
         
        if o.status_code in [200, 201]:
            
            tempo = str(datetime.now())[0:19]

            res = {
                'meuspedidosid': o.headers['meuspedidosid'],
                'ultima_alteracao': tempo,
                'status': o.status_code,
                'controle': True,
            }
            return res
        elif o.content:
            res = {
                'resposta': json.loads(o.content),
                'controle': False,
            }
            
            return res
        
 
    def getObjetos(self, tipo, alterado_apos = False):
        """
        A definir
        """
        objeto = []

        if not alterado_apos:
            url = "%sapi/v1/%s/" % (self.end_url, tipo)
            
            o = requests.get(url, headers= self.headers)
            res = o.json()

            for item in res:
                if not item['excluido'] == True:
                    objeto.append(item)
            return objeto
        else:
            url = '%sapi/v1/%s?alterado_apos="%s"' % (self.end_url, tipo, alterado_apos)
    
            o = requests.get(url, headers= self.headers)
            res = o.json()

            for item in res:
                if not item['excluido'] == True:
                    objeto.append(item)
            return objeto

    def getObjeto(self, tipo, obj_id):

        
        url = "%sapi/v1/%s/%s/" % (self.end_url, tipo, obj_id)

        objeto = requests.get(url, headers= self.headers).json()

        if not objeto.get('excluido') == None:
            if objeto['excluido'] == True:
                return {}
    
            else:
                return objeto
        else:
            return False

        

    def setObjeto(self, tipo, obj_id, objeto):

        
        url = "%sapi/v1/%s/%s/" % (self.end_url, tipo, obj_id)

        o = requests.put(url, data= json.dumps(objeto), headers= self.headers)
        
        if o.headers.get('meuspedidosid') == None:
            res = {
                'resposta': json.loads(o.content),
                'controle': False,
            }
            return res
        else:
            res = {              
                'status': o.status_code,
                'controle': True,
            }
            return res
        

    def checkAtivo(self, tipo, obj_id):
        """
        Identifica se um objeto está ativo nos meus pedidos
        """

        objeto = self.getObjeto(tipo, obj_id)
        
        if not objeto:
            objeto = {}
        
        if not objeto.get('excluido') == None:
            if objeto['excluido'] == False:
                return True
            else:
                return False
        else:
            return False