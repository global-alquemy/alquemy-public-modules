# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.addons.alq_sale_quotation_management.models.constants import SELECTION_MEASURE
from odoo.addons.alq_sale_quotation_management.models.constants import SELECTION_THICKNESS_MEASURE
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

import math
import string


class SaleQuotation(models.Model):
    _name = "sale.quotation"
    _description = "Sale Quotation"
    _inherit = ["sale.quotation.template", "mail.thread", "mail.activity.mixin"]
    _order = "name"

    analytic_account_id = fields.Many2one(string="Analytic account",
                                          comodel_name="account.analytic.account",
                                          tracking=True)
    business_line_id = fields.Many2one(string="Business line",
                                       comodel_name="sale.quotation.template.business")
    business_line_ids = fields.Many2many(string="Business lines",
                                         comodel_name="sale.quotation.template.business",
                                         relation="sale_quotation_template_business_sale_quotation_rel",
                                         column1="business_id",
                                         column2="quotation_id")
    coefficient_show_column = fields.Boolean(string="Coefficient show column",
                                             compute="_compute_coefficient_show_column")
    commercial_commission = fields.Float(string="Commercial commission")
    commercial_id = fields.Many2one(string="Commercial",
                                    comodel_name="res.users",
                                    tracking=True)
    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction",
                                      tracking=True)
    currency_id = fields.Many2one(string="Currency",
                                  comodel_name="res.currency",
                                  related="partner_id.currency_id",
                                  readonly=True)
    date = fields.Date(string="Quotation date",
                       default=fields.Date.today,
                       tracking=True)
    date_status = fields.Date(string="Change status date",
                              tracking=True)
    days = fields.Float(string="Days",
                        digits="Product Unit of Measure",
                        tracking=True)
    days_show_field = fields.Boolean(compute="_compute_days_show_field")
    delivery_weight = fields.Float(string="Delivery weight",
                                   digits="Stock Weight",
                                   compute="_compute_delivery_weight",
                                   store=True)
    description = fields.Text(string="Description",
                              tracking=True)
    display_name = fields.Char(string="Display name",
                               compute="_compute_display_name",
                               store=True)
    dosage_show_column = fields.Boolean(string="Dosage show column",
                                        compute="_compute_dosage_show_column")
    efficiency = fields.Float(string="Efficiency",
                              digits="Product Unit of Measure",
                              tracking=True)
    efficiency_show_column = fields.Boolean(string="Efficiency show column",
                                            compute="_compute_efficiency_show_column")
    efficiency_show_field = fields.Boolean(compute="_compute_efficiency_show_field")
    expiration_date = fields.Date(string="Expiration date",
                                  tracking=True)
    field_ids = fields.Many2many(string="Fields",
                                 comodel_name="sale.quotation.template.field",
                                 relation="sale_quotation_template_field_sale_quotation_rel",
                                 column1="field_id",
                                 column2="quotation_id")
    group_done = fields.Boolean(string="Quotation group done",
                                compute="_compute_group_done")
    group_id = fields.Many2one(string="Quotation group",
                               comodel_name="sale.quotation.group",
                               copy=False,
                               tracking=True)
    height_show_column = fields.Boolean(string="Height show column",
                                        compute="_compute_height_show_column")
    hide_distributed_data = fields.Boolean(string="Hide distributed data",
                                           tracking=True)
    internal_notes = fields.Text(string="Internal notes",
                                 tracking=True)
    length = fields.Float(string="Length",
                          digits="Product Unit of Measure",
                          tracking=True)
    length_show_column = fields.Boolean(string="Length show column",
                                        compute="_compute_length_show_column")
    length_show_field = fields.Boolean(compute="_compute_length_show_field")
    line_ids = fields.One2many(string="Lines",
                               comodel_name="sale.quotation.line",
                               inverse_name="quotation_id",
                               copy=False)
    margin = fields.Float(string="Margin",
                          digits="Discount",
                          compute="_compute_margin",
                          store=True)
    margin_coefficient = fields.Float(string="Margin coefficient",
                                      digits="Discount",
                                      default=1.0,
                                      tracking=True)
    margin_price = fields.Monetary(string="Margin price",
                                   compute="_compute_margin_price",
                                   currency_field="currency_id",
                                   store=True)
    margin_price_distributed = fields.Monetary(string="Margin price distributed",
                                               compute="_compute_margin_price_distributed",
                                               currency_field="currency_id",
                                               store=True)
    measure = fields.Selection(string="Measure",
                               selection=SELECTION_MEASURE,
                               store=True,
                               related=False,
                               readonly=False,
                               tracking=True)
    name = fields.Char(copy=False,
                       tracking=True)
    operating_unit_id = fields.Many2one(string="Operating unit",
                                        comodel_name="operating.unit",
                                        tracking=True)
    origin = fields.Char(string="Origin",
                         copy=False,
                         tracking=True)
    partner_id = fields.Many2one(string="Customer",
                                 comodel_name="res.partner",
                                 tracking=True)
    partner_shipping_id = fields.Many2one(string="Delivery address",
                                          comodel_name="res.partner",
                                          tracking=True)
    perimeter = fields.Float(string="Perimeter",
                             digits="Product Unit of Measure",
                             tracking=True)
    perimeter_show_field = fields.Boolean(compute="_compute_perimeter_show_field")
    quotation_template_id = fields.Many2one(string="Quotation Template",
                                            comodel_name="sale.quotation.template",
                                            tracking=True)
    remaining_expiration_date = fields.Date(string="Remaining expiration date",
                                            compute="_compute_remaining_expiration_date",
                                            store=True)
    sale_by_sections = fields.Boolean(string="Separate sale order lines by sections",
                                      tracking=True)
    sale_order_id = fields.Many2one(string="Sale order",
                                    comodel_name="sale.order",
                                    tracking=True)
    sale_product_id = fields.Many2one(string="Product for sale order lines",
                                      comodel_name="product.product",
                                      tracking=True)
    show_user_commission = fields.Boolean(string="Show user commission",
                                          compute="_compute_show_user_commission")
    state = fields.Selection(string="State",
                             selection=[("draft", "Draft"),
                                        ("sent", "Sent"),
                                        ("quotation", "Quotation"),
                                        ("confirmed", "Confirmed"),
                                        ("done", "Done"),
                                        ("cancel", "Canceled")],
                             default="draft",
                             tracking=True)
    surface = fields.Float(string="Surface",
                           digits="Product Unit of Measure",
                           tracking=True)
    surface_show_column = fields.Boolean(string="Surface show column",
                                         compute="_compute_surface_show_column")
    surface_show_field = fields.Boolean(compute="_compute_surface_show_field")
    thickness = fields.Float(string="Thickness",
                             digits="Product Unit of Measure",
                             tracking=True)
    thickness_measure = fields.Selection(string="Thickness measure",
                                         selection=SELECTION_THICKNESS_MEASURE,
                                         store=True,
                                         related=False,
                                         readonly=False,
                                         tracking=True)
    thickness_show_column = fields.Boolean(string="Thickness show column",
                                           compute="_compute_thickness_show_column")
    thickness_show_field = fields.Boolean(compute="_compute_thickness_show_field")
    total_commercial_commissions = fields.Monetary(string="Total commercial commissions",
                                                   compute="_compute_total_commercial_commissions",
                                                   currency_field="currency_id",
                                                   store=True)
    total_commissions = fields.Monetary(string="Total commissions",
                                        compute="_compute_total_commissions",
                                        currency_field="currency_id",
                                        store=True)
    total_cost = fields.Monetary(string="Total cost",
                                 compute="_compute_total_cost",
                                 currency_field="currency_id",
                                 store=True)
    total_cost_distributed = fields.Monetary(string="Total cost distributed",
                                             compute="_compute_total_cost_distributed",
                                             currency_field="currency_id",
                                             store=True)
    total_price = fields.Monetary(string="Total price",
                                  compute="_compute_total_price",
                                  currency_field="currency_id",
                                  store=True)
    total_price_distributed = fields.Monetary(string="Total price distributed",
                                              compute="_compute_total_price_distributed",
                                              currency_field="currency_id",
                                              store=True)
    total_product_commissions = fields.Monetary(string="Total product commissions",
                                                compute="_compute_total_product_commissions",
                                                currency_field="currency_id",
                                                store=True)
    total_weight = fields.Float(string="Total weight",
                                digits="Stock Weight",
                                compute="_compute_total_weight",
                                store=True)
    units_show_column = fields.Boolean(string="Units show column",
                                       compute="_compute_units_show_column")
    usage_show_column = fields.Boolean(string="Usage show column",
                                       compute="_compute_usage_show_column")
    user_commission = fields.Float(string="User commission",
                                   tracking=True)
    user_id = fields.Many2one(string="User",
                              comodel_name="res.users",
                              tracking=True)
    waste_weight = fields.Float(string="Waste weight",
                                digits="Stock Weight",
                                compute="_compute_waste_weight",
                                store=True)
    width = fields.Float(string="Width",
                         digits="Product Unit of Measure",
                         tracking=True)
    width_show_column = fields.Boolean(string="Width show column",
                                       compute="_compute_width_show_column")
    width_show_field = fields.Boolean(compute="_compute_width_show_field")
    workers = fields.Float(string="Workers",
                           digits="Product Unit of Measure",
                           tracking=True)
    workers_show_field = fields.Boolean(compute="_compute_workers_show_field")

    @api.depends("field_ids", "field_ids.code")
    def _compute_coefficient_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_coefficient" in rec.field_ids.mapped("code"):
                res = True
            rec.coefficient_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_days_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_days" in rec.field_ids.mapped("code"):
                res = True
            rec.days_show_field = res

    @api.depends("line_ids", "line_ids.product_id", "line_ids.quantity",
                 "line_ids.weight", "line_ids.weight_delivery")
    def _compute_delivery_weight(self):
        for rec in self:
            res = 0.0
            for line in rec.line_ids.filtered(lambda f: f.weight_delivery):
                if line.product_id and line.quantity and line.weight:
                    res += line.quantity * line.weight
            rec.delivery_weight = res
            for line in rec.line_ids.filtered(lambda f: "header.delivery_weight" in f.formula_quantity):
                line._compute_quantity()

    @api.depends("name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name

    @api.depends("field_ids", "field_ids.code")
    def _compute_dosage_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_dosage" in rec.field_ids.mapped("code"):
                res = True
            rec.dosage_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_efficiency_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_efficiency" in rec.field_ids.mapped("code"):
                res = True
            rec.efficiency_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_efficiency_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_efficiency" in rec.field_ids.mapped("code"):
                res = True
            rec.efficiency_show_field = res

    @api.depends("group_id", "group_id.quotation_ids", "group_id.quotation_ids.state")
    def _compute_group_done(self):
        for rec in self:
            if rec.group_id and rec.group_id.quotation_ids:
                rec.group_done = any([x == "done" for x in rec.group_id.quotation_ids.mapped("state")])
            else:
                rec.group_done = False

    @api.depends("field_ids", "field_ids.code")
    def _compute_height_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_height" in rec.field_ids.mapped("code"):
                res = True
            rec.height_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_length_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_length" in rec.field_ids.mapped("code"):
                res = True
            rec.length_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_length_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_length" in rec.field_ids.mapped("code"):
                res = True
            rec.length_show_field = res

    @api.depends("total_cost", "total_price")
    def _compute_margin(self):
        for rec in self:
            rec.margin = ((rec.total_price - rec.total_cost) / (rec.total_price or 1.0)) * 100.0

    @api.depends("total_cost", "total_price")
    def _compute_margin_price(self):
        for rec in self:
            rec.margin_price = rec.total_price - rec.total_cost

    @api.depends("length", "measure", "surface", "margin_price")
    def _compute_margin_price_distributed(self):
        for rec in self:
            res = 0.0
            if rec.measure and rec.measure == "linear":
                res = rec.margin_price / (rec.length or 1.0)
            if rec.measure and rec.measure == "square":
                res = rec.margin_price / (rec.surface or 1.0)
            rec.margin_price_distributed = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_perimeter_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_perimeter" in rec.field_ids.mapped("code"):
                res = True
            rec.perimeter_show_field = res

    @api.depends("expiration_date")
    def _compute_remaining_expiration_date(self):
        for rec in self:
            rec.remaining_expiration_date = rec.expiration_date

    @api.depends("commercial_id", "user_id")
    def _compute_show_user_commission(self):
        for rec in self:
            rec.show_user_commission = True if rec.commercial_id != rec.user_id else False

    @api.depends("field_ids", "field_ids.code")
    def _compute_surface_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_surface" in rec.field_ids.mapped("code"):
                res = True
            rec.surface_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_surface_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_surface" in rec.field_ids.mapped("code"):
                res = True
            rec.surface_show_field = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_thickness_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_thickness" in rec.field_ids.mapped("code"):
                res = True
            rec.thickness_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_thickness_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_thickness" in rec.field_ids.mapped("code"):
                res = True
            rec.thickness_show_field = res

    @api.depends("commercial_commission", "margin_price")
    def _compute_total_commercial_commissions(self):
        for rec in self:
            rec.total_commercial_commissions = (rec.commercial_commission * rec.margin_price) / 100.0

    @api.depends("total_commercial_commissions", "total_product_commissions")
    def _compute_total_commissions(self):
        for rec in self:
            rec.total_commissions = rec.total_commercial_commissions + rec.total_product_commissions

    @api.depends("line_ids", "line_ids.display_type", "line_ids.price_total")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.line_ids.filtered(lambda x: not x.display_type).mapped("price_total")) or 0.0

    @api.depends("length", "measure", "surface", "total_cost")
    def _compute_total_cost_distributed(self):
        for rec in self:
            res = 0.0
            if rec.measure and rec.measure == "linear":
                res = rec.total_cost / (rec.length or 1.0)
            if rec.measure and rec.measure == "square":
                res = rec.total_cost / (rec.surface or 1.0)
            rec.total_cost_distributed = res

    @api.depends("length", "measure", "surface", "total_price_distributed")
    def _compute_total_price(self):
        for rec in self:
            res = 0.0
            if rec.measure and rec.measure == "linear":
                res = rec.total_price_distributed * (rec.length or 1.0)
            if rec.measure and rec.measure == "square":
                res = rec.total_price_distributed * (rec.surface or 1.0)
            rec.total_price = res

    @api.depends("length", "margin_coefficient", "measure", "surface", "total_cost")
    def _compute_total_price_distributed(self):
        for rec in self:
            res = 0.0
            if rec.measure and rec.measure == "linear":
                res = (rec.total_cost * rec.margin_coefficient) / (rec.length or 1.0)
            if rec.measure and rec.measure == "square":
                res = (rec.total_cost * rec.margin_coefficient) / (rec.surface or 1.0)
            rec.total_price_distributed = res

    @api.depends("line_ids", "line_ids.price_total", "line_ids.product_commission")
    def _compute_total_product_commissions(self):
        for rec in self:
            rec.total_product_commissions = sum([(x.product_commission * x.price_total) / 100.0 for x in rec.line_ids])

    @api.depends("line_ids", "line_ids.product_id", "line_ids.quantity", "line_ids.weight")
    def _compute_total_weight(self):
        for rec in self:
            res = 0.0
            for line in rec.line_ids:
                if line.product_id and line.quantity and line.weight:
                    res += line.quantity * line.weight
            rec.total_weight = res
            for line in rec.line_ids.filtered(lambda f: "header.total_weight" in f.formula_quantity):
                line._compute_quantity()

    @api.depends("field_ids", "field_ids.code")
    def _compute_units_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_units" in rec.field_ids.mapped("code"):
                res = True
            rec.units_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_usage_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_usage" in rec.field_ids.mapped("code"):
                res = True
            rec.usage_show_column = res

    @api.depends("line_ids", "line_ids.product_id", "line_ids.quantity",
                 "line_ids.weight", "line_ids.weight_waste")
    def _compute_waste_weight(self):
        for rec in self:
            res = 0.0
            for line in rec.line_ids.filtered(lambda f: f.weight_waste):
                if line.product_id and line.quantity and line.weight:
                    res += line.quantity * line.weight
            rec.waste_weight = res
            for line in rec.line_ids.filtered(lambda f: "header.waste_weight" in f.formula_quantity):
                line._compute_quantity()

    @api.depends("field_ids", "field_ids.code")
    def _compute_width_show_column(self):
        for rec in self:
            res = False
            if rec.field_ids and "line_width" in rec.field_ids.mapped("code"):
                res = True
            rec.width_show_column = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_width_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_width" in rec.field_ids.mapped("code"):
                res = True
            rec.width_show_field = res

    @api.depends("field_ids", "field_ids.code")
    def _compute_workers_show_field(self):
        for rec in self:
            res = False
            if rec.field_ids and "header_workers" in rec.field_ids.mapped("code"):
                res = True
            rec.workers_show_field = res

    @api.onchange("commercial_id")
    def _onchange_commercial_id(self):
        self.commercial_commission = 0.0
        if self.commercial_id and self.commercial_id.quotation_commission_ids:
            commercial_commissions = self.commercial_id.quotation_commission_ids.filtered(lambda f: f.operating_unit_id == self.operating_unit_id)
            if commercial_commissions:
                self.commercial_commission = commercial_commissions[:1].commission

    @api.onchange("line_ids")
    def _onchange_line_ids(self):
        for line in self.line_ids.filtered(lambda x: x.display_type == "line_section"):
            line._compute_quantity()
            line._compute_price_total()
            line._compute_price_distributed()
        if self.length_options and self.length_options == "compute":
            self.length = sum(self.line_ids.filtered(lambda x: x.is_reference_line).mapped("length"))
        if self.surface_options and self.surface_options == "compute":
            self.surface = sum(self.line_ids.filtered(lambda x: x.is_reference_line).mapped("surface"))
        if self.thickness_options and self.thickness_options == "compute":
            thickness_sum = sum([x.thickness * x.surface for x in self.line_ids.filtered(lambda x: x.is_reference_line)])
            self.thickness = thickness_sum / (self.surface or 1.0)
        dependant_lines = self.line_ids.filtered(lambda x: "get_line_by_name" in x.formula_quantity)
        if dependant_lines:
            dependant_lines._compute_quantity()

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.partner_shipping_id = False

    def _prepare_sale_order_domain(self):
        self.ensure_one()
        return [("company_id", "=", self.env.company.id),
                ("name", "=", self.display_name)]

    def _prepare_sale_order_vals(self):
        self.ensure_one()
        return {"construction_id": self.construction_id.id if self.construction_id else False,
                "name": self.display_name,
                "operating_unit_id": self.operating_unit_id.id if self.operating_unit_id else False,
                "origin": self.display_name,
                "partner_id": self.partner_id.id if self.partner_id else False}

    def _prepare_sale_order_line_vals(self):
        self.ensure_one()
        name = self.display_name
        if self.description:
            name = "%s - %s" % (self.display_name, self.description)
        result = {"account_analytic_id": self.analytic_account_id.id if self.analytic_account_id else False,
                  "name": name,
                  "price_unit": self.total_price_distributed,
                  "product_id": self.sale_distributed_product_id.id if self.sale_distributed_product_id else False}
        if self.measure and self.measure == "linear":
            result["product_uom_qty"] = self.length
        elif self.measure and self.measure == "square":
            result["product_uom_qty"] = self.surface
        else:
            result["product_uom_qty"] = 1.0
        if self.hide_distributed_data:
            result["price_unit"] = self.total_price
            result["product_id"] = self.sale_product_id.id if self.sale_product_id else False
            result["product_uom_qty"] = 1.0
        return result

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"
            rec.date_status = fields.Date.today()

    def action_confirmed(self):
        for rec in self:
            rec.sale_quotation_validation()
            if rec.group_id and rec.group_id.quotation_ids:
                quotations = rec.group_id.quotation_ids.filtered(lambda f: f.state in ["confirmed", "quotation"] and f.id != rec.id)
                if quotations:
                    quotations.action_sent()
            rec.get_quotation_commissions()
            rec.state = "confirmed"
            rec.date_status = fields.Date.today()

    def action_done(self):
        for rec in self:
            rec.sale_quotation_validation()
            if rec.group_id and rec.group_id.quotation_ids:
                if any([x == "done" for x in rec.group_id.quotation_ids.mapped("state")]):
                    done_error_msg = _("A validated version of this quotation already exists.")
                    raise ValidationError(done_error_msg)
                quotations = rec.group_id.quotation_ids.filtered(lambda f: f.id != rec.id)
                if quotations:
                    quotations.action_cancel()
            rec.get_quotation_commissions()
            rec.state = "done"
            rec.date_status = fields.Date.today()
            rec.create_analytic_account()
            rec.get_or_create_sale_order()

    def action_draft(self):
        for rec in self:
            rec.get_quotation_commissions()
            rec.state = "draft"
            rec.date_status = fields.Date.today()

    def action_quotation(self):
        for rec in self:
            rec.sale_quotation_validation()
            if rec.group_id and rec.group_id.quotation_ids:
                quotations = rec.group_id.quotation_ids.filtered(lambda f: f.state in ["confirmed", "quotation"] and f.id != rec.id)
                if quotations:
                    quotations.action_sent()
            rec.get_quotation_commissions()
            rec.state = "quotation"
            rec.date_status = fields.Date.today()

    def action_send_email(self):
        self.ensure_one()
        template_id = self.env["ir.model.data"]._xmlid_to_res_id("alq_sale_quotation_management.alq_sale_quotation_mail_template",
                                                                 raise_if_not_found=False)
        lang = self.env.context.get("lang")
        template = self.env["mail.template"].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {"custom_layout": "mail.mail_notification_paynow",
               "default_composition_mode": "comment",
               "default_model": "sale.quotation",
               "default_res_id": self.id,
               "default_template_id": template_id,
               "default_use_template": bool(template_id),
               "force_email": True,
               "mark_so_as_sent": True}
        return {"context": ctx,
                "res_model": "mail.compose.message",
                "target": "new",
                "type": "ir.actions.act_window",
                "view_id": False,
                "view_mode": "form",
                "views": [(False, "form")]}

    def action_sent(self):
        for rec in self:
            rec.sale_quotation_validation()
            rec.get_quotation_commissions()
            rec.state = "sent"
            rec.date_status = fields.Date.today()

    def button_view_sale_order(self):
        self.ensure_one()
        if self.sale_order_id:
            return {"name": _("Sale order"),
                    "res_id": self.sale_order_id.id,
                    "res_model": "sale.order",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "form"}

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            seq_name = False
            quotation_seq = self.env.ref("alq_sale_quotation_management.alq_sale_quotation_seq")
            if quotation_seq:
                seq_name = quotation_seq.next_by_id()
            if not seq_name:
                seq_name = self.env["ir.sequence"].next_by_code("sale.quotation")
            if not seq_name:
                error_msg = _("Sequence for sale quotations not found.")
                raise ValidationError(error_msg)
            name = "%s-A" % seq_name
            sqg_vals = {"name": name,
                        "next_subsequence": "b",
                        "next_version": 2}
            group = self.env["sale.quotation.group"].create(sqg_vals)
            if group:
                vals["group_id"] = group.id
            vals["name"] = "%s-a" % name
        elif vals.get("name", False) and not vals.get("group_id", False):
            name = vals["name"][:-2]
            sqg_vals = {"name": name,
                        "next_subsequence": "b",
                        "next_version": 2}
            group = self.env["sale.quotation.group"].create(sqg_vals)
            if group:
                vals["group_id"] = group.id
        return super(SaleQuotation, self).create(vals)

    def create_analytic_account(self):
        for rec in self:
            if rec.business_line_id and rec.business_line_id.root_analytic_account_id:
                if not rec.analytic_account_id:
                    aaa_values = {"company_id": self.env.company.id,
                                  "construction_id": rec.construction_id.id if rec.construction_id else False,
                                  "is_construction": True,
                                  "name": rec.display_name,
                                  "parent_id": rec.business_line_id.root_analytic_account_id.id}
                    if rec.operating_unit_id:
                        aaa_values["operating_unit_ids"] = [(6, 0, [rec.operating_unit_id.id])]
                    new_analytic_account = self.env["account.analytic.account"].create(aaa_values)
                    if new_analytic_account:
                        rec.analytic_account_id = new_analytic_account.id

    def create_new_version(self):
        self.ensure_one()
        default = {"origin": self.display_name}
        if self.group_id and self.group_id.name and self.group_id.next_subsequence:
            default["group_id"] = self.group_id.id
            default["name"] = "%s-%s" % (self.group_id.name, self.group_id.next_subsequence)
        else:
            name = self.name[:-1]
            index = string.ascii_lowercase.index(self.name[-1:]) + 1
            next_index = index + 1
            version = string.ascii_lowercase[next_index - 1]
            default["name"] = "%s%s" % (name, version)
        quotation = self.copy(default=default)
        if quotation:
            for line in self.line_ids:
                line.copy({"quotation_id": quotation.id})
            if self.group_id:
                self.group_id.next_version += 1
                self.group_id.next_subsequence = string.ascii_lowercase[self.group_id.next_version - 1]
            quotation.get_quotation_commissions()
            form_view = self.env.ref("alq_sale_quotation_management.sale_quotation_form")
            return {"context": {},
                    "name": _("Quotation"),
                    "res_model": "sale.quotation",
                    "res_id": quotation.id,
                    "src_model": "sale.quotation",
                    "src_id": self.id,
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_id": form_view.id if form_view else False,
                    "view_mode": "form"}
        return False

    def get_line_by_name(self, name="NULL"):
        if not isinstance(name, str):
            name = "NULL"
        return self.line_ids.filtered(lambda x: x.name == name)[:1]

    def get_or_create_sale_order(self):
        for rec in self:
            order_confirmation = False
            so_domain = rec._prepare_sale_order_domain()
            order = self.env["sale.order"].search(so_domain, limit=1)
            if not order:
                order_vals = rec._prepare_sale_order_vals()
                order = self.env["sale.order"].create(order_vals)
                order_confirmation = True
            if order:
                if rec.sale_by_sections:
                    line_count = 0
                    for line in rec.line_ids.filtered(lambda x: x.display_type == "line_section"):
                        line_vals = line._prepare_sale_order_line_vals()
                        line_vals["order_id"] = order.id
                        self.env["sale.order.line"].create(line_vals)
                        line_count += 1
                    if rec.margin_price and line_count:
                        margin = rec.margin_price / line_count
                        for line in order.order_line:
                            line.price_unit += margin
                        margin_diff = rec.total_price - sum(order.order_line.mapped("price_unit"))
                        if margin_diff != 0.0 and order.order_line:
                            order.order_line[:1].price_unit += margin_diff
                else:
                    line_vals = rec._prepare_sale_order_line_vals()
                    line_vals["order_id"] = order.id
                    self.env["sale.order.line"].create(line_vals)
                rec.sale_order_id = order.id
                if order_confirmation:
                    order.action_confirm()

    def get_quotation_commissions(self):
        for rec in self:
            rec.commercial_commission = 0.0
            if rec.commercial_id and rec.commercial_id.quotation_commission_ids:
                commercial_commissions = rec.commercial_id.quotation_commission_ids.filtered(lambda f: f.operating_unit_id == rec.operating_unit_id)
                if commercial_commissions:
                    rec.commercial_commission = commercial_commissions[:1].commission
            for line in rec.line_ids:
                line.product_commission = 0.0
                if line.product_id and line.product_id.quotation_commission_ids:
                    product_commissions = line.product_id.quotation_commission_ids.filtered(lambda f: f.discount_id == line.discount_id)
                    if product_commissions:
                        line.product_commission = product_commissions[:1].commission

    def get_special_delivery_weight(self):
        res = 0.0
        for line in self.line_ids.filtered(lambda f: f.weight_delivery):
            if line.product_id and line.quantity and line.weight:
                res += line.quantity * line.weight * line.product_id.coefficient_delivery_weight
        return res

    def get_quotation_commissions(self):
        for rec in self:
            rec.commercial_commission = 0.0
            if rec.commercial_id and rec.commercial_id.quotation_commission_ids:
                commercial_commissions = rec.commercial_id.quotation_commission_ids.filtered(lambda f: f.operating_unit_id == rec.operating_unit_id)
                if commercial_commissions:
                    rec.commercial_commission = commercial_commissions[:1].commission
            for line in rec.line_ids:
                line.product_commission = 0.0
                if line.product_id and line.product_id.quotation_commission_ids:
                    product_commissions = line.product_id.quotation_commission_ids.filtered(lambda f: f.discount_id == line.discount_id)
                    if product_commissions:
                        line.product_commission = product_commissions[:1].commission

    def recalculate_lines_sequence(self):
        for rec in self:
            index = 1
            for line in rec.line_ids:
                line.sequence = index
                index += 1

    def sale_quotation_validation(self):
        for rec in self:
            for group in rec.line_ids.mapped("group_id"):
                group_lines = rec.line_ids.filtered(lambda f: f.group_id and f.group_id == group)
                if group_lines and all([not x.product_id or x.quantity <= 0.0 for x in group_lines]):
                    group_error_msg = _("At least one of the following lines is required:")
                    raise ValidationError("%s\n%s" % (group_error_msg, ", ".join(group_lines.mapped("name"))))
            required_lines = rec.line_ids.filtered(lambda f: f.required_line and (not f.product_id or f.quantity <= 0.0))
            if required_lines:
                required_error_msg = _("The following lines are required:")
                raise ValidationError("%s\n%s" % (required_error_msg, ", ".join(required_lines.mapped("name"))))
            validation_error_list = []
            header_sqtf_domain = [("code", "ilike", "header_")]
            for header_field in self.env["sale.quotation.template.field"].search(header_sqtf_domain):
                if header_field.code in rec.field_ids.mapped("code"):
                    if getattr(rec, header_field.code.split("_")[1], 0.0) < 0.0:
                        validation_error_list += [header_field.name]
            for line in rec.line_ids:
                line_sqtf_domain = [("code", "ilike", "line_")]
                for line_field in self.env["sale.quotation.template.field"].search(line_sqtf_domain):
                    if line_field.code in rec.field_ids.mapped("code"):
                        if getattr(line, line_field.code.split("_")[1], 0.0) < 0.0:
                            validation_error_list += ["%s - %s" % (line.name, line_field.name)]
            if validation_error_list:
                validation_error_msg = _("The following fields have a negative value:")
                raise ValidationError("%s\n%s" % (validation_error_msg, "\n".join(validation_error_list)))

    def unlink(self):
        for rec in self:
            if rec.state != "cancel":
                error_msg = _("You can't delete a quotation without before canceling it.")
                raise ValidationError(error_msg)
            rec.line_ids.unlink()
        return super(SaleQuotation, self).unlink()


class SaleQuotationGroup(models.Model):
    _name = "sale.quotation.group"
    _description = "Sale Quotation Group"

    name = fields.Char(string="Name",
                       required=True)
    next_subsequence = fields.Char(string="Next subsequence",
                                   default="b")
    next_version = fields.Integer(string="Next version",
                                  default=2)
    quotation_ids = fields.One2many(string="Sale quotations",
                                    comodel_name="sale.quotation",
                                    inverse_name="group_id")


class SaleQuotationLine(models.Model):
    _name = "sale.quotation.line"
    _description = "Sale Quotation Line"
    _inherit = "sale.quotation.template.line"
    _order = "sequence, id"

    business_line_ids = fields.Many2many(string="Business lines",
                                         comodel_name="sale.quotation.template.business",
                                         relation="sale_quotation_template_business_sale_quotation_line_rel",
                                         column1="business_id",
                                         column2="line_id")
    coefficient = fields.Float(string="Coefficient",
                               digits="Product Unit of Measure")
    coefficient_show_field = fields.Boolean(compute="_compute_coefficient_show_field")
    currency_id = fields.Many2one(string="Currency",
                                  comodel_name="res.currency",
                                  related="quotation_id.partner_id.currency_id",
                                  readonly=True)
    description = fields.Text(string="Description")
    discount = fields.Float(string="Discount",
                            digits="Discount")
    discount_id = fields.Many2one(string="Discount selected",
                                  comodel_name="sale.quotation.template.discount")
    discount_ids = fields.Many2many(string="Discounts",
                                    comodel_name="sale.quotation.template.discount",
                                    relation="sale_quotation_template_discount_sale_quotation_line_rel",
                                    column1="discount_id",
                                    column2="line_id",
                                    default=False)
    dosage = fields.Float(string="Dosage",
                          digits="Product Unit of Measure")
    dosage_show_field = fields.Boolean(compute="_compute_dosage_show_field")
    duplicated_line = fields.Boolean(string="Duplicated line",
                                     default=False)
    efficiency = fields.Float(string="Efficiency",
                              digits="Product Unit of Measure")
    efficiency_show_field = fields.Boolean(compute="_compute_efficiency_show_field")
    header_days_show_field = fields.Boolean(compute="_compute_header_days_show_field")
    header_efficiency_show_field = fields.Boolean(compute="_compute_header_efficiency_show_field")
    header_length_show_field = fields.Boolean(compute="_compute_header_length_show_field")
    header_perimeter_show_field = fields.Boolean(compute="_compute_header_perimeter_show_field")
    header_surface_show_field = fields.Boolean(compute="_compute_header_surface_show_field")
    header_thickness_show_field = fields.Boolean(compute="_compute_header_thickness_show_field")
    header_width_show_field = fields.Boolean(compute="_compute_header_width_show_field")
    header_workers_show_field = fields.Boolean(compute="_compute_header_workers_show_field")
    height = fields.Float(string="Height",
                          digits="Product Unit of Measure")
    height_show_field = fields.Boolean(compute="_compute_height_show_field")
    length = fields.Float(string="Length",
                          digits="Product Unit of Measure")
    length_show_field = fields.Boolean(compute="_compute_length_show_field")
    measure = fields.Selection(string="Measure",
                               related="quotation_id.measure",
                               readonly=True)
    price_distributed = fields.Monetary(string="Price distributed",
                                        compute="_compute_price_distributed",
                                        currency_field="currency_id",
                                        store=True)
    price_total = fields.Monetary(string="Price total",
                                  compute="_compute_price_total",
                                  currency_field="currency_id",
                                  store=True)
    price_unit = fields.Float(string="Price unit",
                              digits="Product Price")
    product_commission = fields.Float(string="Product commission")
    product_id = fields.Many2one(string="Product",
                                 comodel_name="product.product")
    quantity = fields.Float(string="Quantity",
                            digits="Product Unit of Measure",
                            compute="_compute_quantity",
                            store=True)
    quotation_id = fields.Many2one(string="Quotation",
                                   comodel_name="sale.quotation")
    quotation_template_line_id = fields.Many2one(string="Quotation Template Line",
                                                 comodel_name="sale.quotation.template.line")
    state = fields.Selection(string="State",
                             related="quotation_id.state",
                             readonly=True)
    surface = fields.Float(string="Surface",
                           digits="Product Unit of Measure")
    surface_show_field = fields.Boolean(compute="_compute_surface_show_field")
    template_discount_ids = fields.Many2many(string="Template discounts",
                                             comodel_name="sale.quotation.template.discount",
                                             relation="sqt_discount_sq_line_rel",
                                             column1="sqt_discount_id",
                                             column2="sq_line_id")
    thickness = fields.Float(string="Thickness",
                             digits="Product Unit of Measure")
    thickness_measure = fields.Selection(string="Thickness measure",
                                         related="quotation_id.thickness_measure",
                                         readonly=True)
    thickness_show_field = fields.Boolean(compute="_compute_thickness_show_field")
    units = fields.Float(string="Units",
                         digits="Product Unit of Measure")
    units_show_field = fields.Boolean(compute="_compute_units_show_field")
    usage = fields.Float(string="Usage",
                         digits="Product Unit of Measure")
    usage_show_field = fields.Boolean(compute="_compute_usage_show_field")
    weight = fields.Float(string="Weight",
                          digits="Stock Weight")
    width = fields.Float(string="Width",
                         digits="Product Unit of Measure")
    width_show_field = fields.Boolean(compute="_compute_width_show_field")

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_coefficient_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_coefficient" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.coefficient_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_dosage_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_dosage" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.dosage_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_efficiency_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_efficiency" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.efficiency_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_days_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_days" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_days_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_efficiency_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_efficiency" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_efficiency_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_length_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_length" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_length_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_perimeter_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_perimeter" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_perimeter_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_surface_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_surface" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_surface_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_thickness_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_thickness" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_thickness_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_width_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_width" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_width_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_header_workers_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "header_workers" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.header_workers_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_height_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_height" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.height_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_length_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_length" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.length_show_field = res

    @api.depends("display_type", "price_total", "product_id", "quotation_id",
                 "quotation_id.length", "quotation_id.surface")
    def _compute_price_distributed(self):
        for rec in self:
            if not rec.display_type and not rec.product_id:
                rec.price_distributed = 0.0
            else:
                formula = rec.formula_price_distributed
                results = rec._get_formula_fields()
                safe_eval(formula, results, mode="exec", nocopy=True)
                rec.price_distributed = float(results.get("result", "0.0"))

    @api.depends("discount", "display_type", "price_unit", "product_id", "quantity")
    def _compute_price_total(self):
        for rec in self:
            if not rec.display_type and not rec.product_id:
                rec.price_total = 0.0
            else:
                formula = rec.formula_price_total
                results = rec._get_formula_fields()
                safe_eval(formula, results, mode="exec", nocopy=True)
                rec.price_total = float(results.get("result", "0.0"))

    @api.depends("coefficient", "display_type", "dosage", "efficiency", "height", "length", "product_id",
                 "quotation_id", "quotation_id.days", "quotation_id.efficiency", "quotation_id.length",
                 "quotation_id.surface", "quotation_id.thickness", "quotation_id.width",
                 "quotation_id.workers", "surface", "thickness", "units", "usage", "width")
    def _compute_quantity(self):
        for rec in self:
            if not rec.display_type and not rec.product_id:
                rec.quantity = 0.0
            else:
                formula = rec.formula_quantity
                results = rec._get_formula_fields()
                safe_eval(formula, results, mode="exec", nocopy=True)
                rec.quantity = float(results.get("result", "0.0"))

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_surface_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_surface" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.surface_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_thickness_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_thickness" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.thickness_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_units_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_units" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.units_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_usage_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_usage" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.usage_show_field = res

    @api.depends("quotation_id", "quotation_id.field_ids", "quotation_id.field_ids.code")
    def _compute_width_show_field(self):
        for rec in self:
            res = False
            if rec.quotation_id and rec.quotation_id.field_ids:
                if "line_width" in rec.quotation_id.field_ids.mapped("code"):
                    res = True
            rec.width_show_field = res

    def _get_formula_fields(self):
        self.ensure_one()
        return {"ceil": math.ceil,
                "header": self.quotation_id,
                "line": self,
                "product": self.product_id}

    @api.onchange("coefficient")
    def _onchange_coefficient(self):
        if self.coefficient < 1.0:
            update_vals = {"coefficient": 1.0}
            self.update(update_vals)

    @api.onchange("discount_id")
    def _onchange_discount_id(self):
        update_vals = {"discount": 0.0,
                       "product_commission": 0.0}
        if self.discount_id and self.discount_id.discount:
            update_vals["discount"] = self.discount_id.discount
        if self.discount_id and self.product_id and self.product_id.quotation_commission_ids:
            product_commissions = self.product_id.quotation_commission_ids.filtered(lambda f: f.discount_id == self.discount_id)
            if product_commissions:
                update_vals["product_commission"] = product_commissions[:1].commission
        self.update(update_vals)

    @api.onchange("price_unit")
    def _onchange_price_unit(self):
        if self.price_unit < self.min_price_unit:
            update_vals = {"price_unit": self.min_price_unit}
            self.update(update_vals)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        min_discount = False
        for discount in self.template_discount_ids:
            if not min_discount:
                min_discount = discount
            if discount.discount < min_discount.discount:
                min_discount = discount
        update_vals = {"coefficient": self.coefficient_default_value,
                       "description": False,
                       "discount_id": min_discount.id if min_discount else False,
                       "discount_ids": [(6, 0, self.template_discount_ids.ids)],
                       "dosage": self.dosage_default_value,
                       "efficiency": self.efficiency_default_value,
                       "length": self.length_default_value,
                       "price_unit": max([self.price_unit_default_value, self.min_price_unit]),
                       "surface": self.surface_default_value,
                       "thickness": self.thickness_default_value,
                       "units": self.units_default_value,
                       "usage": self.usage_default_value,
                       "weight": 0.0}
        if self.product_id and self.product_id.coefficient:
            update_vals["coefficient"] = self.product_id.coefficient
        if self.product_id and self.product_id.display_name:
            update_vals["description"] = self.product_id.display_name
        if self.product_id and self.product_id.dosage:
            update_vals["dosage"] = self.product_id.dosage
        if self.product_id and self.product_id.efficiency:
            update_vals["efficiency"] = self.product_id.efficiency
        if self.product_id and self.product_id.length:
            update_vals["length"] = self.product_id.length
        if self.priority_price and self.priority_price == "product":
            if self.product_id and self.product_id.standard_price:
                update_vals["price_unit"] = max([self.product_id.standard_price, self.min_price_unit])
        if self.product_id and self.product_id.surface:
            update_vals["surface"] = self.product_id.surface
        if self.product_id and self.product_id.thickness:
            update_vals["thickness"] = self.product_id.thickness
        if self.product_id and self.product_id.units:
            update_vals["units"] = self.product_id.units
        if self.product_id and self.product_id.usage:
            update_vals["usage"] = self.product_id.usage
        if self.product_id and self.product_id.weight:
            update_vals["weight"] = self.product_id.weight
        if self.product_id and self.product_id.quotation_commission_ids:
            product_discounts = self.product_id.quotation_commission_ids.mapped("discount_id")
            if product_discounts:
                update_vals["discount_ids"] = [(6, 0, product_discounts.ids)]
                min_discount = False
                for discount in product_discounts:
                    if not min_discount:
                        min_discount = discount
                    if discount.discount < min_discount.discount:
                        min_discount = discount
                update_vals["discount_id"] = min_discount.id if min_discount else False
        self.update(update_vals)

    def _prepare_sale_order_line_vals(self):
        self.ensure_one()
        return {"account_analytic_id": self.quotation_id.analytic_account_id.id if self.quotation_id and self.quotation_id.analytic_account_id else False,
                "name": self.description,
                "price_unit": self.price_total,
                "product_id": self.quotation_id.sale_product_id.id if self.quotation_id and self.quotation_id.sale_product_id else False,
                "product_uom_qty": 1.0}

    def copy_line(self):
        self.ensure_one()
        default = {"duplicated_line": True}
        self.copy(default=default)
        self.quotation_id._onchange_line_ids()
        return True

    def get_price_distributed_section(self):
        self.ensure_one()
        res = 0.0
        filtered_lines = self.quotation_id.line_ids.filtered(lambda f: f.sequence > self.sequence)
        for line in filtered_lines.sorted(key=lambda s: s.sequence):
            if line.display_type == "line_section":
                break
            line._compute_price_distributed()
            res += line.price_distributed
        return res

    def get_price_total_section(self):
        self.ensure_one()
        res = 0.0
        filtered_lines = self.quotation_id.line_ids.filtered(lambda f: f.sequence > self.sequence)
        for line in filtered_lines.sorted(key=lambda s: s.sequence):
            if line.display_type == "line_section":
                break
            line._compute_price_total()
            res += line.price_total
        return res

    def unlink_line(self):
        self.ensure_one()
        quotation = self.quotation_id
        self.unlink()
        quotation._onchange_line_ids()
        return True
