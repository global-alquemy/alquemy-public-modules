# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    account_analytic_id = fields.Many2one(copy=False)

    @api.onchange("analytic_account_id")
    def _onchange_analytic_account_id(self):
        if self.analytic_account_id:
            self.order_line.update({"account_analytic_id": self.analytic_account_id.id})


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    account_analytic_id = fields.Many2one(string="Analytic account",
                                          comodel_name="account.analytic.account",
                                          copy=False)

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals["analytic_account_id"] = self.account_analytic_id.id if self.account_analytic_id else False
        return vals

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id and self.product_id.income_analytic_account_id:
            self.update({"account_analytic_id": self.product_id.income_analytic_account_id.id})
        elif self.order_id and self.order_id.analytic_account_id:
            self.update({"account_analytic_id": self.order_id.analytic_account_id.id})
        return res
