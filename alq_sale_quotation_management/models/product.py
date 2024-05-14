# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplateQuotationCommission(models.Model):
    _name = "product.template.quotation.commission"
    _description = "Product Template Quotation Commission"

    commission = fields.Float(string="Commission")
    discount_id = fields.Many2one(string="Discount",
                                  comodel_name="sale.quotation.template.discount")
    template_id = fields.Many2one(string="Product template",
                                  comodel_name="product.template")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    coefficient = fields.Float(string="Coefficient",
                               digits="Product Unit of Measure")
    coefficient_delivery_weight = fields.Float(string="Coefficient delivery weight",
                                               digits="Product Unit of Measure")
    dosage = fields.Float(string="Dosage",
                          digits="Product Unit of Measure")
    efficiency = fields.Float(string="Efficiency",
                              digits="Product Unit of Measure")
    efficiency_umbral = fields.Float(string="Efficiency umbral",
                                     digits="Product Unit of Measure")
    length = fields.Float(string="Length",
                          digits="Product Unit of Measure")
    major_dividend = fields.Float(string="Major dividend",
                                  digits="Product Unit of Measure")
    minimum_workers = fields.Float(string="Minimum workers",
                                   digits="Product Unit of Measure")
    minor_dividend = fields.Float(string="Minor dividend",
                                  digits="Product Unit of Measure")
    quotation_commission_ids = fields.One2many(string="Quotation commissions",
                                               comodel_name="product.template.quotation.commission",
                                               inverse_name="template_id")
    surface = fields.Float(string="Surface",
                           digits="Product Unit of Measure")
    thickness = fields.Float(string="Thickness",
                             digits="Product Unit of Measure")
    units = fields.Float(string="Units",
                         digits="Product Unit of Measure")
    usage = fields.Float(string="Usage",
                         digits="Product Unit of Measure")
    work_price = fields.Float(string="Work price",
                              digits="Product Price")
    work_price_minimum = fields.Float(string="Work price minimum",
                                      digits="Product Price")
