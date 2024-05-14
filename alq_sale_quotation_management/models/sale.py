# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction")
    quotation_ids = fields.One2many(string="Quotations",
                                    comodel_name="sale.quotation",
                                    inverse_name="sale_order_id")
    quotations_count = fields.Integer(string="Quotations count",
                                      compute="_compute_quotations_count")

    @api.depends("quotation_ids")
    def _compute_quotations_count(self):
        for rec in self:
            rec.quotations_count = len(rec.quotation_ids) if rec.quotation_ids else 0

    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        res["construction_id"] = self.construction_id.id if self.construction_id else False
        if self.env.context.get("inv_by_cert", False):
            new_cert_lines = []
            new_cert_seq = 1000
            order_lines = self.order_line.filtered(lambda f: not f.is_downpayment)
            for invoice in self.invoice_ids.sorted(key=lambda s: s.name):
                cert_section_created = False
                invoice_lines = invoice.invoice_line_ids.filtered(lambda f: f.product_id in order_lines.mapped("product_id"))
                for product in invoice_lines.mapped("product_id"):
                    if not cert_section_created:
                        new_cert_lines.append((0, 0, invoice._prepare_cert_section_line_vals(new_seq=new_cert_seq)))
                        cert_section_created = True
                        new_cert_seq += 1
                    product_lines = invoice_lines.filtered(lambda f: product == f.product_id)
                    product_qty = sum(product_lines.mapped("quantity"))
                    new_cert_lines.append((0, 0, product_lines[:1]._prepare_invoice_line_copy(new_qty=product_qty, new_seq=new_cert_seq)))
                    new_cert_seq += 1
            res["invoice_line_ids"] += new_cert_lines
        return res

    def button_view_quotations(self):
        self.ensure_one()
        if self.quotation_ids:
            return {"domain": [("id", "in", self.quotation_ids.ids)],
                    "name": _("Quotations"),
                    "res_model": "sale.quotation",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def unlink(self):
        for rec in self:
            if rec.quotation_ids:
                error_msg = _("You can't delete a sale order with sale quotations linked.")
                raise ValidationError(error_msg)
        return super(SaleOrder, self).unlink()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.env.context.get("inv_by_cert", False):
            res["quantity"] = self.product_uom_qty
        return res
