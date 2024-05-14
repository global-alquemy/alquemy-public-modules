# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GenerateSaleQuotationWizard(models.TransientModel):
    _name = "generate.sale.quotation.wizard"
    _description = "Generate Sale Quotation Wizard"

    business_line_id = fields.Many2one(string="Business line",
                                       comodel_name="sale.quotation.template.business")
    date = fields.Date(string="Quotation date",
                       default=fields.Date.today)
    operating_unit_id = fields.Many2one(string="Operating unit",
                                        comodel_name="operating.unit")
    partner_id = fields.Many2one(string="Customer",
                                 comodel_name="res.partner")
    partner_shipping_id = fields.Many2one(string="Delivery address",
                                          comodel_name="res.partner")
    quotation_name = fields.Char(string="Quotation name")
    template_id = fields.Many2one(string="Template",
                                  comodel_name="sale.quotation.template")

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.partner_shipping_id = False

    def generate_sale_quotation(self):
        self.ensure_one()
        if not self.template_id:
            raise UserError(_("You must select a sale quotation template."))
        quotation_vals = self.template_id._prepare_sale_quotation_vals()
        quotation_vals["business_line_id"] = self.business_line_id.id if self.business_line_id else False
        quotation_vals["date"] = self.date
        quotation_vals["expiration_date"] = self.date
        quotation_vals["operating_unit_id"] = self.operating_unit_id.id if self.operating_unit_id else False
        quotation_vals["partner_id"] = self.partner_id.id if self.partner_id else False
        quotation_vals["partner_shipping_id"] = self.partner_shipping_id.id if self.partner_shipping_id else False
        if self.partner_id and self.partner_id.user_id:
            quotation_vals["commercial_id"] = self.partner_id.user_id.id
        if quotation_vals.get("expiration_days", False):
            quotation_vals["expiration_date"] = self.date + relativedelta(days=quotation_vals["expiration_days"])
        if quotation_vals.get("name", _("New")) == _("New") and self.quotation_name:
            quotation_vals["name"] = self.quotation_name
        quotation = self.env["sale.quotation"].create(quotation_vals)
        if quotation:
            for line in self.template_id.line_ids:
                line_vals = line._prepare_sale_quotation_line_vals()
                line_vals["quotation_id"] = quotation.id
                line = self.env["sale.quotation.line"].create(line_vals)
                line._onchange_product_id()
                if line.display_type == "line_section":
                    line.description = line.name
        quotation.recalculate_lines_sequence()
        quotation._onchange_line_ids()
        quotation.get_quotation_commissions()
        form_view = self.env.ref("alq_sale_quotation_management.sale_quotation_form")
        return {"context": {},
                "name": _("Quotation"),
                "res_model": "sale.quotation",
                "res_id": quotation.id,
                "src_model": "generate.sale.quotation.wizard",
                "src_id": self.id,
                "target": "current",
                "type": "ir.actions.act_window",
                "view_id": form_view.id if form_view else False,
                "view_mode": "form"}
