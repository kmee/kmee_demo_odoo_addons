# coding: utf-8
from openerp.osv import fields, osv
from openerp.tools.translate import _

class ProductPricelistProduct(osv.osv):
	_name = "product.pricelist.product"
	_description = "Classe abstrata para salvar sincronização de listas de preço"
