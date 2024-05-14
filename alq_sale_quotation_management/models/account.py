# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction")
    is_construction = fields.Boolean(string="It's construction account")


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction",
                                      related="account_id.construction_id",
                                      readonly=True,
                                      store=True)


class AccountMove(models.Model):
    _inherit = "account.move"

    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction")

    def _prepare_cert_section_line_vals(self, new_seq=False):
        self.ensure_one()
        if not new_seq:
            new_seq = self.sequence
        return {"account_id": False,
                "discount": 0.0,
                "display_type": "line_section",
                "is_cert_line": True,
                "name": "%s %s" % (_("Certification discount:"), self.name or "n/a"),
                "price_unit": 0.0,
                "product_id": False,
                "product_uom_id": False,
                "quantity": 0.0,
                "sequence": new_seq}


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_cert_line = fields.Boolean(string="It's certification line")

    def _prepare_invoice_line_copy(self, new_qty=0.0, new_seq=False):
        self.ensure_one()
        if not new_qty:
            new_qty = self.quantity
        if not new_qty:
            new_seq = self.sequence
        return {"account_id": self.account_id.id if self.account_id else False,
                "analytic_account_id": self.analytic_account_id.id if self.analytic_account_id else False,
                "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
                "discount": self.discount,
                "display_type": self.display_type,
                "is_cert_line": True,
                "name": self.name,
                "price_unit": self.price_unit,
                "product_id": self.product_id.id if self.product_id else False,
                "product_uom_id": self.product_uom_id.id if self.product_uom_id else False,
                "quantity": new_qty * -1,
                "sequence": new_seq,
                "sale_line_ids": [(6, 0, self.sale_line_ids.ids)],
                "tax_ids": [(6, 0, self.tax_ids.ids)]}
