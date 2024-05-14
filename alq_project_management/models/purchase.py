# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    collection_id = fields.Many2one(string="Collection order",
                                    comodel_name="collection.order")
    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction")
    construction_location_id = fields.Many2one(string="Construction location",
                                               comodel_name="stock.location")

    def _prepare_picking(self):
        self.ensure_one()
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.collection_id:
            res["collection_id"] = self.collection_id.id
        if self.construction_id:
            res["construction_id"] = self.construction_id.id
        if self.construction_location_id:
            res["location_dest_id"] = self.construction_location_id.id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    collection_notes = fields.Text(string="Collection notes")

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking=picking, price_unit=price_unit, product_uom_qty=product_uom_qty, product_uom=product_uom)
        if self.order_id and self.order_id.construction_location_id:
            res["location_dest_id"] = self.order_id.construction_location_id.id
        return res

    def _create_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._create_stock_moves(picking=picking)
        for move in res:
            if move.purchase_line_id and move.purchase_line_id.order_id and move.purchase_line_id.order_id.construction_location_id:
                move.location_dest_id = move.purchase_line_id.order_id.construction_location_id.id
                if move.picking_id:
                    move.picking_id.location_dest_id = move.purchase_line_id.order_id.construction_location_id.id
        return res
