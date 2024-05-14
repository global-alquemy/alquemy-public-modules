# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

import string


class GenerateSaleQuotationWizard(models.TransientModel):
    _inherit = "generate.sale.quotation.wizard"

    lead_id = fields.Many2one(string="CRM lead",
                              comodel_name="crm.lead")

    def generate_sale_quotation(self):
        res = super(GenerateSaleQuotationWizard, self).generate_sale_quotation()
        self.ensure_one()
        if self.lead_id and res.get("res_id", False) and res.get("res_model", False):
            quotation = self.env[res["res_model"]].browse(res["res_id"])
            if quotation:
                if self.lead_id.construction_id:
                    quotation.construction_id = self.lead_id.construction_id.id
                quotation.lead_id = self.lead_id.id
                quotation.origin = self.lead_id.name
                if not self.lead_id.quotation_sequence and quotation.name:
                    self.lead_id.quotation_sequence = quotation.name[:-4]
                self.lead_id.next_version += 1
                self.lead_id.next_subsequence = string.ascii_uppercase[self.lead_id.next_version - 1]
        return res
