# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class SaleQuotation(models.Model):
    _inherit = "sale.quotation"

    collection_ids = fields.One2many(string="Collections",
                                     comodel_name="collection.order",
                                     inverse_name="quotation_id")
    collections_count = fields.Integer(string="Collections count",
                                       compute="_compute_collections_count")
    project_ids = fields.One2many(string="Projects",
                                  comodel_name="project.project",
                                  inverse_name="quotation_id")
    projects_count = fields.Integer(string="Projects count",
                                    compute="_compute_projects_count")

    @api.depends("collection_ids")
    def _compute_collections_count(self):
        for rec in self:
            rec.collections_count = len(rec.collection_ids) if rec.collection_ids else 0

    @api.depends("project_ids")
    def _compute_projects_count(self):
        for rec in self:
            rec.projects_count = len(rec.project_ids) if rec.project_ids else 0

    def _prepare_collection_vals(self):
        self.ensure_one()
        return {"analytic_account_id": self.analytic_account_id.id if self.analytic_account_id else False,
                "business_line_id": self.business_line_id.id if self.business_line_id else False,
                "construction_id": self.construction_id.id if self.construction_id else False,
                "internal_notes": self.internal_notes,
                "name": self.display_name,
                "operating_unit_id": self.operating_unit_id.id if self.operating_unit_id else False,
                "partner_id": self.partner_id.id if self.partner_id else False,
                "partner_shipping_id": self.partner_shipping_id.id if self.partner_shipping_id else False,
                "quotation_id": self.id}

    def _prepare_project_vals(self):
        self.ensure_one()
        return {"analytic_account_id": self.analytic_account_id.id if self.analytic_account_id else False,
                "business_line_id": self.business_line_id.id if self.business_line_id else False,
                "company_id": self.env.company.id,
                "construction_id": self.construction_id.id if self.construction_id else False,
                "date_start": fields.Date.today(),
                "is_construction": True,
                "is_template": False,
                "name": self.display_name,
                "operating_unit_id": self.operating_unit_id.id if self.operating_unit_id else False,
                "partner_id": self.partner_id.id if self.partner_id else False,
                "partner_shipping_id": self.partner_shipping_id.id if self.partner_shipping_id else False,
                "privacy_visibility": "portal",
                "quotation_id": self.id,
                "surface_id": self.business_line_id.surface_id.id if self.business_line_id and self.business_line_id.surface_id else False,
                "user_id": False}

    def action_done(self):
        res = super(SaleQuotation, self).action_done()
        for rec in self:
            rec.create_project()
        return res

    def button_view_collections(self):
        self.ensure_one()
        if self.collection_ids:
            return {"domain": [("id", "in", self.collection_ids.ids)],
                    "name": _("Collections"),
                    "res_model": "collection.order",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def button_view_projects(self):
        self.ensure_one()
        if self.project_ids:
            return {"domain": [("id", "in", self.project_ids.ids)],
                    "name": _("Projects"),
                    "res_model": "project.project",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def create_project(self):
        for rec in self:
            sw_domain = [("company_id", "=", self.env.company.id),
                         ("operating_unit_id", "=", rec.operating_unit_id.id)]
            warehouse = self.env["stock.warehouse"].search(sw_domain, limit=1)
            if not warehouse:
                sw_error_msg = _("Delegation warehouse not found.")
                raise ValidationError(sw_error_msg)
            sl_domain = [("is_construction", "=", True),
                         ("location_id", "=", warehouse.view_location_id.id)]
            root_location = self.env["stock.location"].search(sl_domain, limit=1)
            if not root_location:
                sl_error_msg = _("Construction root location not found.")
                raise ValidationError(sl_error_msg)
            sl_values = {"is_construction": True,
                         "location_id": root_location.id,
                         "name": rec.display_name,
                         "usage": "internal"}
            if rec.partner_shipping_id and rec.partner_shipping_id.name:
                sl_values["name"] = rec.partner_shipping_id.name
            location = self.env["stock.location"].create(sl_values)
            pp_values = rec._prepare_project_vals()
            pp_values["construction_warehouse_id"] = warehouse.id
            if location:
                pp_values["construction_location_id"] = location.id
            if rec.template_project_id:
                project = rec.template_project_id.copy(pp_values)
            else:
                project = self.env["project.project"].create(pp_values)
            co_values = rec._prepare_collection_vals()
            co_values["construction_warehouse_id"] = warehouse.id
            if location:
                co_values["construction_location_id"] = location.id
            if project:
                co_values["project_id"] = project.id
            collection = self.env["collection.order"].create(co_values)
            if collection:
                project.collection_id = collection.id
                for line in rec.line_ids.filtered(lambda f: not f.display_type and f.product_id and f.collection_quantity > 0.0):
                    col_values = line._prepare_collection_line_vals()
                    col_values["collection_id"] = collection.id
                    self.env["collection.order.line"].create(col_values)


class SaleQuotationLine(models.Model):
    _inherit = "sale.quotation.line"

    collection_quantity = fields.Float(string="Collection quantity",
                                       digits="Product Unit of Measure",
                                       compute="_compute_collection_quantity",
                                       store=True)

    @api.depends("coefficient", "display_type", "dosage", "efficiency", "height", "length", "product_id",
                 "quotation_id", "quotation_id.days", "quotation_id.efficiency", "quotation_id.length",
                 "quotation_id.surface", "quotation_id.thickness", "quotation_id.width",
                 "quotation_id.workers", "surface", "thickness", "units", "usage", "width")
    def _compute_collection_quantity(self):
        for rec in self:
            if not rec.display_type and not rec.product_id:
                rec.collection_quantity = 0
            else:
                formula = rec.formula_quantity
                results = rec._get_formula_fields()
                safe_eval(formula, results, mode="exec", nocopy=True)
                rec.collection_quantity = float(results.get("collection_qty", "0.0"))

    def _prepare_collection_line_vals(self):
        self.ensure_one()
        return {"material_control": self.material_control,
                "product_id": self.product_id.id if self.product_id else False,
                "product_uom_id": self.product_id.uom_id.id if self.product_id and self.product_id.uom_id else False,
                "product_uom_qty": 0,
                "quotation_price_unit": self.price_unit,
                "quotation_product_id": self.product_id.id if self.product_id else False,
                "quotation_qty": self.collection_quantity,
                "required_qty": self.collection_quantity}
