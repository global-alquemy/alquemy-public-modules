# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleQuotationTemplate(models.Model):
    _inherit = "sale.quotation.template"

    template_project_id = fields.Many2one(string="Template project",
                                          comodel_name="project.project",
                                          tracking=True)

    def _prepare_sale_quotation_vals(self):
        self.ensure_one()
        res = super(SaleQuotationTemplate, self)._prepare_sale_quotation_vals()
        if self.template_project_id:
            res["template_project_id"] = self.template_project_id.id
        return res


class SaleQuotationTemplateBusiness(models.Model):
    _inherit = "sale.quotation.template.business"

    surface_id = fields.Many2one(string="Surface type",
                                 comodel_name="construction.surface")


class SaleQuotationTemplateLine(models.Model):
    _inherit = "sale.quotation.template.line"

    formula_quantity = fields.Text(default="result = 0.0\ncollection_qty = result")
    is_project_labor = fields.Boolean(string="Is project labor")
    material_control = fields.Boolean(string="Material control")

    def _prepare_sale_quotation_line_vals(self):
        self.ensure_one()
        res = super(SaleQuotationTemplateLine, self)._prepare_sale_quotation_line_vals()
        res["is_project_labor"] = self.is_project_labor
        res["material_control"] = self.material_control
        return res
