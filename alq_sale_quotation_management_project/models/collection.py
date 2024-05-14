# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CollectionOrder(models.Model):
    _inherit = "collection.order"

    business_line_id = fields.Many2one(string="Business line",
                                       comodel_name="sale.quotation.template.business",
                                       tracking=True)
    quotation_id = fields.Many2one(string="Quotation",
                                   comodel_name="sale.quotation",
                                   tracking=True)
