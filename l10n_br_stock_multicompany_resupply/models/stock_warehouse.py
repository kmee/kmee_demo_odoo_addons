# -*- coding: utf-8 -*-
# Copyright 2016 KMEE - www.kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class StockWarehouse(models.Model):
    """Adaptação do warehouse para transferências de mercadorias entre filiais

        Simplificando o faturamento entre filais através de regras de
        push/pull. Permitindo que as operações sejam faturadas e utlizáveis
        por usuários de cada filial

        Note:
            Automatizar a criação das regras de resuprimento conforme
            configurações brasileiras;
            TODO: Alterar as permissões de acesso dos modelos
            TODO: Remover a necessidade de se forçar a disponibilidade de
                materiais transferidos entre filais
    """

    _inherit = 'stock.warehouse'

    def _prepare_inter_company_to_stock(
            self, item, warehouse, partner_address_id=False, context=False):
        item['fiscal_category_id'] = (
            warehouse.company_id.stock_in_resupply_fiscal_category_id and
            warehouse.company_id.stock_in_resupply_fiscal_category_id.id)
        item['invoice_state'] = (
            warehouse.company_id.stock_in_resupply_invoice_state)
        item['partner_address_id'] = partner_address_id

    def _prepare_stock_to_inter_company(
            self, item, warehouse, partner_address_id=False, context=False):
        item['fiscal_category_id'] = (
            warehouse.company_id.stock_out_resupply_fiscal_category_id and
            warehouse.company_id.stock_out_resupply_fiscal_category_id.id)
        item['invoice_state'] = (
            warehouse.company_id.stock_out_resupply_invoice_state)
        item['partner_address_id'] = partner_address_id

    def _get_mto_pull_rule(self, cr, uid, warehouse, values, context=None):
        """Altera a criação das regras Estoque -> Inter Company Transit MTO
        adicionando os campos Categoria Fiscal e Tipo de Faturamento definidos
        no cadastro da empresa.
        """
        result = super(StockWarehouse, self)._get_mto_pull_rule(
            cr, uid, warehouse, values, context)

        for item in result:
            self._prepare_stock_to_inter_company(
                item=item, warehouse=warehouse, context=context)
        return result

    def _get_supply_pull_rules(self, cr, uid, supply_warehouse, values,
                               new_route_id, context=None):
        """Altera a criação das regras Estoque -> Inter Company Transit e
        Inter Company Transit -> Estoque
        adicionando os campos Categoria Fiscal e Tipo de Faturamento definidos
        no cadastro da empresa.
        """
        result = super(StockWarehouse, self)._get_supply_pull_rules(
            cr, uid, supply_warehouse, values, new_route_id, context)

        source_item = dest_item = None
        for item in result:
            warehouse = self.browse(cr, uid, item.get('warehouse_id'))
            if not warehouse:
                return result
            external_transit_location = self._get_external_transit_location(
                cr, uid, warehouse, context=context)
            if item['location_id'] == external_transit_location.id:
                source_item = item
                source_warehouse = warehouse
            elif item['location_src_id'] == external_transit_location.id:
                dest_item = item
                dest_warehouse = warehouse

        if source_item is not None:
            partner_address_id = (
                self.browse(cr, uid, dest_item['warehouse_id']).partner_id.id
                if dest_item is not None
                else None
            )

            self._prepare_stock_to_inter_company(
                item=source_item,
                warehouse=source_warehouse,
                partner_address_id=partner_address_id,
                context=context,
            )

        if dest_item is not None:
            partner_address_id = self.browse(
                cr, uid, dest_item['propagate_warehouse_id']).partner_id.id
            self._prepare_inter_company_to_stock(
                item=dest_item,
                warehouse=dest_warehouse,
                partner_address_id=partner_address_id,
                context=context,
            )
        return result
