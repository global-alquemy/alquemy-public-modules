# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_construction = fields.Boolean(string="Is construction")

    def name_get(self):
        show_stock_product = self.env.context.get("show_stock_product_id", False)
        if show_stock_product:
            result = []
            for rec in self:
                sq_domain = [("company_id", "=", rec.company_id.id),
                             ("location_id", "=", rec.id),
                             ("product_id", "=", show_stock_product),
                             ("quantity", ">", 0.0)]
                quants = self.env["stock.quant"].search(sq_domain)
                qty = sum(quants.mapped("quantity"))
                name = "%s (%s)" % (rec.complete_name, qty)
                result.append((rec.id, name))
            return result
        return super(StockLocation, self).name_get()


class StockPicking(models.Model):
    _inherit = "stock.move"

    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction",
                                      related="picking_id.construction_id",
                                      readonly=True,
                                      store=True)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    collection_id = fields.Many2one(string="Collection order",
                                    comodel_name="collection.order")
    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction")
    worksheet_id = fields.Many2one(string="Construction worksheet",
                                   comodel_name="construction.worksheet")


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_construction = fields.Boolean(string="Is construction")
