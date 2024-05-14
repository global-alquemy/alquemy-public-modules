# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    inv_by_cert = fields.Boolean(string="Invoicing by certifications")

    def create_invoices(self):
        return super(SaleAdvancePaymentInv, self.with_context(inv_by_cert=self.inv_by_cert)).create_invoices()
