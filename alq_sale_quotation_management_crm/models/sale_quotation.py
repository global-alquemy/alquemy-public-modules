# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleQuotation(models.Model):
    _inherit = "sale.quotation"

    lead_id = fields.Many2one(string="CRM lead",
                              comodel_name="crm.lead",
                              tracking=True)

    def _prepare_sale_order_domain(self):
        self.ensure_one()
        res = super(SaleQuotation, self)._prepare_sale_order_domain()
        if self.lead_id:
            res = [("company_id", "=", self.env.company.id),
                   ("name", "=", self.lead_id.quotation_sequence)]
        return res

    def _prepare_sale_order_vals(self):
        self.ensure_one()
        res = super(SaleQuotation, self)._prepare_sale_order_vals()
        if self.lead_id:
            res["name"] = self.lead_id.quotation_sequence
            res["opportunity_id"] = self.lead_id.id
            res["team_id"] = self.lead_id.team_id.id if self.lead_id.team_id else False
        return res

    def create_analytic_account(self):
        res = super(SaleQuotation, self).create_analytic_account()
        for rec in self:
            if rec.analytic_account_id and rec.lead_id and rec.lead_id.quotation_sequence:
                aag_values = {"company_id": self.env.company.id,
                              "name": rec.lead_id.quotation_sequence}
                new_analytic_group = self.env["account.analytic.group"].create(aag_values)
                if new_analytic_group:
                    rec.analytic_account_id.group_id = new_analytic_group.id
        return res

    def get_or_create_sale_order(self):
        res = super(SaleQuotation, self).get_or_create_sale_order()
        for rec in self:
            if rec.lead_id and rec.sale_order_id:
                rec.sale_order_id.opportunity_id = self.lead_id.id
        return res
