# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    quotation_commission_ids = fields.One2many(string="Quotation commissions",
                                               comodel_name="res.partner.quotation.commission",
                                               inverse_name="partner_id")


class ResPartnerQuotationCommission(models.Model):
    _name = "res.partner.quotation.commission"
    _description = "Res Partner Quotation Commission"

    commission = fields.Float(string="Commission")
    operating_unit_id = fields.Many2one(string="Operating unit",
                                        comodel_name="operating.unit")
    partner_id = fields.Many2one(string="Partner",
                                 comodel_name="res.partner")


class ResUsers(models.Model):
    _inherit = "res.users"

    code = fields.Char(string="Code")
