# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.addons.alq_sale_quotation_management.models.constants import SELECTION_HEADER_OPTIONS
from odoo.addons.alq_sale_quotation_management.models.constants import SELECTION_HEADER_SPECIAL_OPTIONS
from odoo.addons.alq_sale_quotation_management.models.constants import SELECTION_LINE_OPTIONS
from odoo.addons.alq_sale_quotation_management.models.constants import SELECTION_MEASURE
from odoo.addons.alq_sale_quotation_management.models.constants import SELECTION_THICKNESS_MEASURE

import ast
import json


class SaleQuotationTemplate(models.Model):
    _name = "sale.quotation.template"
    _description = "Sale Quotation Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_default_sale_product_id(self):
        product = self.env.ref("alq_sale_quotation_management.alq_sale_quotation_product")
        return product.id if product else False

    business_line_ids = fields.Many2many(string="Business lines",
                                         comodel_name="sale.quotation.template.business",
                                         relation="sale_quotation_template_business_sale_quotation_template_rel",
                                         column1="business_id",
                                         column2="template_id")
    code = fields.Char(string="Code",
                       copy=False)
    days_default_value = fields.Float(string="Days default value",
                                      digits="Product Unit of Measure",
                                      tracking=True)
    days_options = fields.Selection(string="Days options",
                                    selection=SELECTION_HEADER_OPTIONS,
                                    tracking=True)
    days_show_field = fields.Boolean(string="Days show field",
                                     compute="_compute_days_show_field")
    efficiency_default_value = fields.Float(string="Efficiency default value",
                                            digits="Product Unit of Measure",
                                            tracking=True)
    efficiency_options = fields.Selection(string="Efficiency options",
                                          selection=SELECTION_HEADER_OPTIONS,
                                          tracking=True)
    efficiency_show_field = fields.Boolean(string="Efficiency show field",
                                           compute="_compute_efficiency_show_field")
    expiration_days = fields.Integer(string="Expiration days",
                                     tracking=True)
    length_default_value = fields.Float(string="Length default value",
                                        digits="Product Unit of Measure",
                                        tracking=True)
    length_options = fields.Selection(string="Length options",
                                      selection=SELECTION_HEADER_SPECIAL_OPTIONS,
                                      tracking=True)
    length_show_field = fields.Boolean(string="Length show field",
                                       compute="_compute_length_show_field")
    line_ids = fields.One2many(string="Lines",
                               comodel_name="sale.quotation.template.line",
                               inverse_name="template_id",
                               copy=True)
    measure = fields.Selection(string="Measure",
                               related="type_id.measure",
                               readonly=True)
    name = fields.Char(string="Name",
                       required=True,
                       tracking=True)
    note = fields.Text(string="Note",
                       tracking=True)
    perimeter_default_value = fields.Float(string="Perimeter default value",
                                           digits="Product Unit of Measure",
                                           tracking=True)
    perimeter_options = fields.Selection(string="Perimeter options",
                                         selection=SELECTION_HEADER_OPTIONS,
                                         tracking=True)
    perimeter_show_field = fields.Boolean(string="Perimeter show field",
                                          compute="_compute_perimeter_show_field")
    sale_by_sections = fields.Boolean(string="Separate sale order lines by sections",
                                      tracking=True)
    sale_distributed_product_id = fields.Many2one(string="Product distributed for sale order lines",
                                                  comodel_name="product.product",
                                                  tracking=True)
    sale_product_id = fields.Many2one(string="Product for sale order lines",
                                      comodel_name="product.product",
                                      default=_get_default_sale_product_id,
                                      tracking=True)
    surface_default_value = fields.Float(string="Surface default value",
                                         digits="Product Unit of Measure",
                                         tracking=True)
    surface_options = fields.Selection(string="Surface options",
                                       selection=SELECTION_HEADER_SPECIAL_OPTIONS,
                                       tracking=True)
    surface_show_field = fields.Boolean(string="Surface show field",
                                        compute="_compute_surface_show_field")
    thickness_default_value = fields.Float(string="Thickness default value",
                                           digits="Product Unit of Measure",
                                           tracking=True)
    thickness_measure = fields.Selection(string="Thickness measure",
                                         related="type_id.thickness_measure",
                                         readonly=True)
    thickness_options = fields.Selection(string="Thickness options",
                                         selection=SELECTION_HEADER_SPECIAL_OPTIONS,
                                         tracking=True)
    thickness_show_field = fields.Boolean(string="Thickness show field",
                                          compute="_compute_thickness_show_field")
    type_id = fields.Many2one(string="Template type",
                              comodel_name="sale.quotation.template.type",
                              tracking=True)
    width_default_value = fields.Float(string="Width default value",
                                       digits="Product Unit of Measure",
                                       tracking=True)
    width_options = fields.Selection(string="Width options",
                                     selection=SELECTION_HEADER_OPTIONS,
                                     tracking=True)
    width_show_field = fields.Boolean(string="Width show field",
                                      compute="_compute_width_show_field")
    workers_default_value = fields.Float(string="Workers default value",
                                         digits="Product Unit of Measure",
                                         tracking=True)
    workers_options = fields.Selection(string="Workers options",
                                       selection=SELECTION_HEADER_OPTIONS,
                                       tracking=True)
    workers_show_field = fields.Boolean(string="Workers show field",
                                        compute="_compute_workers_show_field")

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_days_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_days" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.days_show_field = res

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_efficiency_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_efficiency" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.efficiency_show_field = res

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_length_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_length" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.length_show_field = res

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_perimeter_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_perimeter" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.perimeter_show_field = res

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_surface_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_surface" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.surface_show_field = res

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_thickness_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_thickness" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.thickness_show_field = res

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_width_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_width" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.width_show_field = res

    @api.depends("type_id", "type_id.field_ids", "type_id.field_ids.code")
    def _compute_workers_show_field(self):
        for rec in self:
            res = False
            if rec.type_id and rec.type_id.field_ids:
                if "header_workers" in rec.type_id.field_ids.mapped("code"):
                    res = True
            rec.workers_show_field = res

    def _prepare_sale_quotation_vals(self):
        self.ensure_one()
        return {"commercial_id": self.env.user.id,
                "date": fields.Date.today(),
                "days": self.days_default_value,
                "days_default_value": self.days_default_value,
                "days_options": self.days_options,
                "efficiency": self.efficiency_default_value,
                "efficiency_default_value": self.efficiency_default_value,
                "efficiency_options": self.efficiency_options,
                "expiration_days": self.expiration_days,
                "expiration_date": fields.Date.today(),
                "field_ids": [(6, 0, self.type_id.field_ids.ids)],
                "length": self.length_default_value,
                "length_default_value": self.length_default_value,
                "length_options": self.length_options,
                "measure": self.type_id.measure,
                "name": _("New"),
                "note": self.note,
                "perimeter": self.perimeter_default_value,
                "perimeter_default_value": self.perimeter_default_value,
                "perimeter_options": self.perimeter_options,
                "quotation_template_id": self.id,
                "sale_distributed_product_id": self.sale_distributed_product_id.id if self.sale_distributed_product_id else False,
                "sale_product_id": self.sale_product_id.id if self.sale_product_id else False,
                "sale_by_sections": self.sale_by_sections,
                "surface": self.surface_default_value,
                "surface_default_value": self.surface_default_value,
                "surface_options": self.surface_options,
                "thickness": self.thickness_default_value,
                "thickness_measure": self.type_id.thickness_measure,
                "thickness_default_value": self.thickness_default_value,
                "thickness_options": self.thickness_options,
                "type_id": self.type_id.id if self.type_id else False,
                "user_id": self.env.user.id,
                "width": self.width_default_value,
                "width_default_value": self.width_default_value,
                "width_options": self.width_options,
                "workers": self.workers_default_value,
                "workers_default_value": self.workers_default_value,
                "workers_options": self.workers_options}

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if self._name and self._name == "sale.quotation.template":
            copy_text = _("(copy)")
            default["name"] = "%s %s" % (self.name, copy_text)
        return super(SaleQuotationTemplate, self).copy(default=default)

    def unlink(self):
        for rec in self:
            rec.line_ids.unlink()
        return super(SaleQuotationTemplate, self).unlink()


class SaleQuotationTemplateBusiness(models.Model):
    _name = "sale.quotation.template.business"
    _description = "Sale Quotation Template Business"

    code = fields.Char(string="Code",
                       required=True)
    name = fields.Char(string="Name",
                       required=True)
    root_analytic_account_id = fields.Many2one(string="Root analytic account",
                                               comodel_name="account.analytic.account")


class SaleQuotationTemplateDiscount(models.Model):
    _name = "sale.quotation.template.discount"
    _description = "Sale Quotation Template Discount"

    code = fields.Char(string="Code",
                       required=True)
    default_discount = fields.Boolean(string="Default discount")
    discount = fields.Float(string="Discount",
                            digits="Discount")
    name = fields.Char(string="Name",
                       required=True)


class SaleQuotationTemplateField(models.Model):
    _name = "sale.quotation.template.field"
    _description = "Sale Quotation Template Field"

    code = fields.Char(string="Code",
                       required=True)
    name = fields.Char(string="Name",
                       required=True)


class SaleQuotationTemplateLine(models.Model):
    _name = "sale.quotation.template.line"
    _description = "Sale Quotation Template Line"
    _order = "sequence, id"

    def _get_default_discount_ids(self):
        res = False
        sqtd_domain = [("default_discount", "=", True)]
        sqtd = self.env["sale.quotation.template.discount"].search(sqtd_domain)
        if sqtd:
            res = sqtd.ids
        return res

    def _get_default_formula_price_distributed(self):
        res = "result = 0.0"
        if self.env.context.get("default_measure", "NULL") == "linear":
            res = "result = line.price_total / (header.length or 1.0)"
        if self.env.context.get("default_measure", "NULL") == "square":
            res = "result = line.price_total / (header.surface or 1.0)"
        if self.env.context.get("default_display_type", "NULL") == "line_section":
            res = "result = line.get_price_distributed_section()"
        return res

    def _get_default_formula_price_total(self):
        res = "result = (line.price_unit * (1.0 - line.discount / 100.0)) * line.quantity"
        if self.env.context.get("default_display_type", False):
            if self.env.context.get("default_display_type") == "line_section":
                res = "result = line.get_price_total_section()"
        return res

    def _get_default_formula_quantity_editable(self):
        res = True
        if self.env.context.get("default_display_type", False):
            if self.env.context.get("default_display_type") == "line_section":
                res = False
        return res

    business_line_ids = fields.Many2many(string="Business lines",
                                         comodel_name="sale.quotation.template.business",
                                         relation="sqt_business_sqt_line_rel",
                                         column1="business_id",
                                         column2="line_id",
                                         compute="_compute_business_line_ids",
                                         store=True)
    coefficient_default_value = fields.Float(string="Coefficient default value",
                                             digits="Product Unit of Measure",
                                             default=1.0)
    coefficient_options = fields.Selection(string="Coefficient options",
                                           selection=SELECTION_LINE_OPTIONS,
                                           default="invisible")
    coefficient_show_field = fields.Boolean(string="Coefficient show field",
                                            compute="_compute_coefficient_show_field")
    default_product_id = fields.Many2one(string="Default product",
                                         comodel_name="product.product")
    discount_ids = fields.Many2many(string="Discounts",
                                    comodel_name="sale.quotation.template.discount",
                                    relation="sqt_discount_sqt_line_rel",
                                    column1="discount_id",
                                    column2="line_id",
                                    default=_get_default_discount_ids)
    display_type = fields.Selection(string="Display type",
                                    selection=[("line_section", "Section")],
                                    default=False,
                                    help="Technical field for UX purpose.")
    dosage_default_value = fields.Float(string="Dosage default value",
                                        digits="Product Unit of Measure")
    dosage_options = fields.Selection(string="Dosage options",
                                      selection=SELECTION_LINE_OPTIONS,
                                      default="invisible")
    dosage_show_field = fields.Boolean(string="Dosage show field",
                                       compute="_compute_dosage_show_field")
    editable_name = fields.Boolean(string="Editable name")
    efficiency_default_value = fields.Float(string="Efficiency default value",
                                            digits="Product Unit of Measure")
    efficiency_options = fields.Selection(string="Efficiency options",
                                          selection=SELECTION_LINE_OPTIONS,
                                          default="invisible")
    efficiency_show_field = fields.Boolean(string="Efficiency show field",
                                           compute="_compute_efficiency_show_field")
    formula_price_distributed = fields.Text(string="Formula: Price distributed",
                                            default=_get_default_formula_price_distributed)
    formula_price_distributed_editable = fields.Boolean(string="Formula editable: Price distributed")
    formula_price_total = fields.Text(string="Formula: Price total",
                                      default=_get_default_formula_price_total)
    formula_price_total_editable = fields.Boolean(string="Formula editable: Price total")
    formula_quantity = fields.Text(string="Formula: Quantity",
                                   default="result = 0.0")
    formula_quantity_editable = fields.Boolean(string="Formula editable: Quantity",
                                               default=_get_default_formula_quantity_editable)
    group_id = fields.Many2one(string="Line group",
                               comodel_name="sale.quotation.template.line.group")
    header_days_show_field = fields.Boolean(string="Header days show field",
                                            compute="_compute_header_days_show_field")
    header_efficiency_show_field = fields.Boolean(string="Header efficiency show field",
                                                  compute="_compute_header_efficiency_show_field")
    header_length_show_field = fields.Boolean(string="Header length show field",
                                              compute="_compute_header_length_show_field")
    header_perimeter_show_field = fields.Boolean(string="Header perimeter show field",
                                                 compute="_compute_header_perimeter_show_field")
    header_surface_show_field = fields.Boolean(string="Header surface show field",
                                               compute="_compute_header_surface_show_field")
    header_thickness_show_field = fields.Boolean(string="Header thickness show field",
                                                 compute="_compute_header_thickness_show_field")
    header_width_show_field = fields.Boolean(string="Header width show field",
                                             compute="_compute_header_width_show_field")
    header_workers_show_field = fields.Boolean(string="Header workers show field",
                                               compute="_compute_header_workers_show_field")
    height_default_value = fields.Float(string="Height default value",
                                        digits="Product Unit of Measure")
    height_options = fields.Selection(string="Height options",
                                      selection=SELECTION_LINE_OPTIONS,
                                      default="invisible")
    height_show_field = fields.Boolean(string="Height show field",
                                       compute="_compute_height_show_field")
    is_reference_line = fields.Boolean(string="Is reference line")
    length_default_value = fields.Float(string="Length default value",
                                        digits="Product Unit of Measure")
    length_options = fields.Selection(string="Length options",
                                      selection=SELECTION_LINE_OPTIONS,
                                      default="invisible")
    length_show_field = fields.Boolean(string="Length show field",
                                       compute="_compute_length_show_field")
    max_discount = fields.Float(string="Maximum discount",
                                digits="Discount")
    measure = fields.Selection(string="Measure",
                               related="template_id.type_id.measure",
                               readonly=True)
    min_price_unit = fields.Float(string="Minimum price unit",
                                  digits="Product Price")
    name = fields.Char(string="Name",
                       required=True)
    price_unit_default_value = fields.Float(string="Price unit default value",
                                            digits="Product Price")
    price_unit_options = fields.Selection(string="Price unit options",
                                          selection=SELECTION_LINE_OPTIONS,
                                          default=False)
    priority_price = fields.Selection(string="Priority price",
                                      selection=[("product", "Product"),
                                                 ("Line", "Line")],
                                      default="product",
                                      required=True)
    product_domain = fields.Char(string="Product domain")
    required_line = fields.Boolean(string="Required line")
    sequence = fields.Integer(string="Sequence",
                              default=100)
    surface_default_value = fields.Float(string="Surface default value",
                                         digits="Product Unit of Measure")
    surface_options = fields.Selection(string="Surface options",
                                       selection=SELECTION_LINE_OPTIONS,
                                       default="invisible")
    surface_show_field = fields.Boolean(string="Surface show field",
                                        compute="_compute_surface_show_field")
    template_id = fields.Many2one(string="Template",
                                  comodel_name="sale.quotation.template")
    thickness_default_value = fields.Float(string="Thickness default value",
                                           digits="Product Unit of Measure")
    thickness_measure = fields.Selection(string="Thickness measure",
                                         related="template_id.type_id.thickness_measure",
                                         readonly=True)
    thickness_options = fields.Selection(string="Thickness options",
                                         selection=SELECTION_LINE_OPTIONS,
                                         default="invisible")
    thickness_show_field = fields.Boolean(string="Thickness show field",
                                          compute="_compute_thickness_show_field")
    units_default_value = fields.Float(string="Units default value",
                                       digits="Product Unit of Measure")
    units_options = fields.Selection(string="Units options",
                                     selection=SELECTION_LINE_OPTIONS,
                                     default="invisible")
    units_show_field = fields.Boolean(string="Units show field",
                                      compute="_compute_units_show_field")
    usage_default_value = fields.Float(string="Usage default value",
                                       digits="Product Unit of Measure")
    usage_options = fields.Selection(string="Usage options",
                                     selection=SELECTION_LINE_OPTIONS,
                                     default="invisible")
    usage_show_field = fields.Boolean(string="Usage show field",
                                      compute="_compute_usage_show_field")
    weight_delivery = fields.Boolean(string="Weight counts for delivery")
    weight_waste = fields.Boolean(string="Weight counts for waste management")
    width_default_value = fields.Float(string="Width default value",
                                       digits="Product Unit of Measure")
    width_options = fields.Selection(string="Width options",
                                     selection=SELECTION_LINE_OPTIONS,
                                     default="invisible")
    width_show_field = fields.Boolean(string="Width show field",
                                      compute="_compute_width_show_field")

    @api.depends("template_id", "template_id.business_line_ids")
    def _compute_business_line_ids(self):
        for rec in self:
            if rec.template_id and rec.template_id.business_line_ids:
                rec.business_line_ids = [(6, 0, rec.template_id.business_line_ids.ids)]
            else:
                rec.business_line_ids = [(5, 0, 0)]

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_coefficient_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_coefficient" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.coefficient_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_dosage_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_dosage" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.dosage_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_efficiency_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_efficiency" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.efficiency_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_days_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_days" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_days_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_efficiency_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_efficiency" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_efficiency_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_length_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_length" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_length_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_perimeter_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_perimeter" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_perimeter_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_surface_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_surface" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_surface_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_thickness_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_thickness" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_thickness_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_width_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_width" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_width_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_header_workers_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "header_workers" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.header_workers_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_height_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_height" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.height_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_length_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_length" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.length_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_surface_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_surface" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.surface_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_thickness_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_thickness" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.thickness_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_units_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_units" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.units_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_usage_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_usage" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.usage_show_field = res

    @api.depends("template_id", "template_id.type_id", "template_id.type_id.field_ids", "template_id.type_id.field_ids.code")
    def _compute_width_show_field(self):
        for rec in self:
            res = False
            if rec.template_id and rec.template_id.type_id and rec.template_id.type_id.field_ids:
                if "line_width" in rec.template_id.type_id.field_ids.mapped("code"):
                    res = True
            rec.width_show_field = res

    @api.onchange("group_id")
    def _onchange_group_id(self):
        if self.group_id:
            self.required_line = False

    @api.onchange("required_line")
    def _onchange_required_line(self):
        if self.required_line:
            self.group_id = False

    def _prepare_sale_quotation_line_vals(self):
        self.ensure_one()
        product_domain = ast.literal_eval(self.product_domain) if self.product_domain else []
        min_discount = False
        for discount in self.discount_ids:
            if not min_discount:
                min_discount = discount
            if discount.discount < min_discount.discount:
                min_discount = discount
        return {"coefficient": self.coefficient_default_value,
                "coefficient_default_value": self.coefficient_default_value,
                "coefficient_options": self.coefficient_options,
                "default_product_id": self.default_product_id.id if self.default_product_id else False,
                "discount": min_discount.discount if min_discount else 0.0,
                "discount_id": min_discount.id if min_discount else False,
                "discount_ids": [(6, 0, self.discount_ids.ids)],
                "display_type": self.display_type,
                "dosage": self.dosage_default_value,
                "dosage_default_value": self.dosage_default_value,
                "dosage_options": self.dosage_options,
                "editable_name": self.editable_name,
                "efficiency": self.efficiency_default_value,
                "efficiency_default_value": self.efficiency_default_value,
                "efficiency_options": self.efficiency_options,
                "formula_price_distributed": self.formula_price_distributed,
                "formula_price_distributed_editable": self.formula_price_distributed_editable,
                "formula_price_total": self.formula_price_total,
                "formula_price_total_editable": self.formula_price_total_editable,
                "formula_quantity": self.formula_quantity,
                "formula_quantity_editable": self.formula_quantity_editable,
                "group_id": self.group_id.id if self.group_id else False,
                "height": self.height_default_value,
                "height_default_value": self.height_default_value,
                "height_options": self.height_options,
                "is_reference_line": self.is_reference_line,
                "length": self.length_default_value,
                "length_default_value": self.length_default_value,
                "length_options": self.length_options,
                "max_discount": self.max_discount,
                "min_price_unit": self.min_price_unit,
                "name": self.name,
                "price_unit": self.price_unit_default_value,
                "price_unit_default_value": self.price_unit_default_value,
                "price_unit_options": self.price_unit_options,
                "priority_price": self.priority_price,
                "product_domain": json.dumps(product_domain),
                "product_id": self.default_product_id.id if self.default_product_id else False,
                "quotation_template_line_id": self.id,
                "required_line": self.required_line,
                "sequence": self.sequence,
                "surface": self.surface_default_value,
                "surface_default_value": self.surface_default_value,
                "surface_options": self.surface_options,
                "template_discount_ids": [(6, 0, self.discount_ids.ids)],
                "template_id": self.template_id.id,
                "thickness": self.thickness_default_value,
                "thickness_default_value": self.thickness_default_value,
                "thickness_options": self.thickness_options,
                "units": self.units_default_value,
                "units_default_value": self.units_default_value,
                "units_options": self.units_options,
                "usage": self.usage_default_value,
                "usage_default_value": self.usage_default_value,
                "usage_options": self.usage_options,
                "weight_delivery": self.weight_delivery,
                "weight_waste": self.weight_waste,
                "width": self.width_default_value,
                "width_default_value": self.width_default_value,
                "width_options": self.width_options}

    def copy_line(self):
        self.ensure_one()
        self.copy(default={})
        return True


class SaleQuotationTemplateLineGroup(models.Model):
    _name = "sale.quotation.template.line.group"
    _description = "Sale Quotation Template Line Group"

    name = fields.Char(string="Name",
                       required=True)


class SaleQuotationTemplateType(models.Model):
    _name = "sale.quotation.template.type"
    _description = "Sale Quotation Template Type"

    field_ids = fields.Many2many(string="Fields",
                                 comodel_name="sale.quotation.template.field",
                                 relation="sale_quotation_template_field_sale_quotation_template_type_rel",
                                 column1="field_id",
                                 column2="type_id")
    measure = fields.Selection(string="Measure",
                               selection=SELECTION_MEASURE)
    name = fields.Char(string="Name",
                       required=True)
    thickness_measure = fields.Selection(string="Thickness measure",
                                         selection=SELECTION_THICKNESS_MEASURE)
