# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ConstructionWorksheet(models.Model):
    _name = "construction.worksheet"
    _description = "Construction Worksheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    allowance_id = fields.Many2one(string="Allowance",
                                   comodel_name="product.product")
    analytic_account_id = fields.Many2one(string="Analytic account",
                                          comodel_name="account.analytic.account",
                                          tracking=True)
    collection_id = fields.Many2one(string="Collection order",
                                    comodel_name="collection.order")
    company_id = fields.Many2one(string="Company",
                                 comodel_name="res.company",
                                 default=lambda self: self.env.company.id,
                                 tracking=True)
    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction",
                                      tracking=True)
    construction_location_id = fields.Many2one(string="Construction location",
                                               comodel_name="stock.location",
                                               tracking=True)
    construction_warehouse_id = fields.Many2one(string="Construction warehouse",
                                                comodel_name="stock.warehouse",
                                                tracking=True)
    date = fields.Date(string="Date",
                       tracking=True)
    hours = fields.Float(string="Hours")
    internal_notes = fields.Text(string="Internal notes",
                                 tracking=True)
    line_ids = fields.One2many(string="Lines",
                               comodel_name="construction.worksheet.line",
                               inverse_name="worksheet_id")
    material_ids = fields.One2many(string="Materials",
                                   comodel_name="construction.worksheet.material",
                                   inverse_name="worksheet_id")
    name = fields.Char(string="Name",
                       tracking=True)
    operating_unit_id = fields.Many2one(string="Operating unit",
                                        comodel_name="operating.unit",
                                        tracking=True)
    pickings_count = fields.Integer(string="Pickings count",
                                    compute="_compute_pickings_count",
                                    store=True)
    picking_ids = fields.One2many(string="Pickings",
                                  comodel_name="stock.picking",
                                  inverse_name="worksheet_id")
    project_id = fields.Many2one(string="Project",
                                 comodel_name="project.project",
                                 tracking=True)
    state = fields.Selection(string="State",
                             selection=[("draft", "Draft"),
                                        ("done", "Done")],
                             default="draft",
                             tracking=True)
    toxics = fields.Boolean(string="Toxics")
    user_id = fields.Many2one(string="User",
                              comodel_name="res.users",
                              default=lambda self: self.env.user.id,
                              tracking=True)

    @api.depends("picking_ids")
    def _compute_pickings_count(self):
        for rec in self:
            rec.pickings_count = len(rec.picking_ids) if rec.picking_ids else 0

    @api.onchange("allowance_id")
    def _onchange_allowance_id(self):
        if self.allowance_id:
            vals = {"allowance_id": self.allowance_id.id,
                    "allowance_qty": 1.0}
            self.line_ids.update(vals)

    @api.onchange("hours")
    def _onchange_hours(self):
        vals = {"force_hours": self.hours}
        self.line_ids.update(vals)

    @api.onchange("toxics")
    def _onchange_toxics(self):
        vals = {"toxics": self.toxics}
        if self.toxics:
            vals["toxics_qty"] = 1.0
        else:
            vals["toxics_qty"] = 0.0
        self.line_ids.update(vals)

    def _prepare_stock_picking_vals(self):
        self.ensure_one()
        if not self.construction_warehouse_id:
            raise UserError(_("Construction warehouse not selected."))
        spt_domain = [("code", "=", "outgoing"),
                      ("warehouse_id", "=", self.construction_warehouse_id.id)]
        picking_type = self.env["stock.picking.type"].search(spt_domain, limit=1)
        if not picking_type:
            raise UserError(_("Picking type not found for selected warehouse."))
        sl_domain = [("usage", "=", "customer")]
        customer_location = self.env["stock.location"].search(sl_domain, limit=1)
        if not customer_location:
            raise UserError(_("Customer location not found."))
        return {"construction_id": self.construction_id.id if self.construction_id else False,
                "location_dest_id": customer_location.id,
                "location_id": self.construction_location_id.id,
                "origin": self.name,
                "picking_type_id": picking_type.id,
                "worksheet_id": self.id}

    def action_done(self):
        for rec in self:
            if rec.line_ids.filtered(lambda f: f.hours <= 0):
                raise UserError(_("Zero or negative hours cannot be set."))
            if rec.material_ids.filtered(lambda f: f.product_uom_qty <= 0):
                raise UserError(_("Zero or negative quantities cannot be set."))
            for line in rec.line_ids:
                aal_vals = line._prepare_account_analytic_line_vals()
                self.env["account.analytic.line"].create(aal_vals)
                if line.allowance_id:
                    allowance_aal_vals = line._prepare_allowance_account_analytic_line_vals()
                    self.env["account.analytic.line"].create(allowance_aal_vals)
            if rec.material_ids.filtered(lambda f: f.product_uom_qty > 0):
                sp_values = rec._prepare_stock_picking_vals()
                picking = self.env["stock.picking"].create(sp_values)
                for material in rec.material_ids:
                    aal_vals = material._prepare_account_analytic_line_vals()
                    self.env["account.analytic.line"].create(aal_vals)
                    sm_vals = material._prepare_stock_move_line_vals(picking)
                    self.env["stock.move.line"].create(sm_vals)
                picking.scheduled_date = "%s 00:00:00" % rec.date.strftime("%Y-%m-%d")
                picking.with_context(cancel_backorder=True)._action_done()
            rec.state = "done"

    def button_view_pickings(self):
        self.ensure_one()
        if self.picking_ids:
            return {"domain": [("id", "in", self.picking_ids.ids)],
                    "name": _("Pickings"),
                    "res_model": "stock.picking",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def unlink(self):
        for rec in self:
            if rec.state == "done":
                error_msg = _("You can't delete a done construction worksheet.")
                raise UserError(error_msg)
            rec.line_ids.unlink()
            rec.material_ids.unlink()
        return super(ConstructionWorksheet, self).unlink()


class ConstructionWorksheetLine(models.Model):
    _name = "construction.worksheet.line"
    _description = "Construction Worksheet Line"

    allowance_id = fields.Many2one(string="Allowance",
                                   comodel_name="product.product")
    allowance_qty = fields.Float(string="Allowance quantity",
                                 digits="Product Unit of Measure")
    employee_id = fields.Many2one(string="Employee",
                                  comodel_name="hr.employee")
    end_date = fields.Datetime(string="End date")
    force_hours = fields.Float(string="Force hours")
    hours = fields.Float(string="Hours",
                         compute="_compute_hours",
                         store=True)
    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    start_date = fields.Datetime(string="Start date")
    toxics = fields.Boolean(string="Toxics")
    toxics_qty = fields.Float(string="Toxics quantity",
                              digits="Product Unit of Measure")
    worksheet_id = fields.Many2one(string="Construction worksheet",
                                   comodel_name="construction.worksheet")

    @api.depends("end_date", "force_hours", "start_date")
    def _compute_hours(self):
        for rec in self:
            if rec.force_hours:
                hours = rec.force_hours
            elif rec.end_date and rec.start_date:
                diff = rec.end_date - rec.start_date
                hours = round(diff.total_seconds() / 3600.0, 2)
            else:
                hours = 0.0
            rec.hours = hours

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        update_vals = {"name": False}
        if self.employee_id and self.worksheet_id:
            update_vals["name"] = "%s - %s" % (self.worksheet_id.name, self.employee_id.name)
        self.update(update_vals)

    def _prepare_allowance_account_analytic_line_vals(self):
        self.ensure_one()
        hours_uom = self.env.ref("uom.product_uom_hour")
        name = "%s - %s" % (self.name, self.allowance_id.display_name)
        return {"account_id": self.worksheet_id.analytic_account_id.id if self.worksheet_id and self.worksheet_id.analytic_account_id else False,
                "amount": ((self.allowance_id.standard_price if self.allowance_id else 0.0) * self.allowance_qty) * -1,
                "company_id": self.worksheet_id.company_id.id if self.worksheet_id.company_id else False,
                "date": self.worksheet_id.date,
                "employee_id": self.employee_id.id if self.employee_id else False,
                "name": name,
                "product_id": self.allowance_id.id if self.allowance_id else False,
                "product_uom_id": hours_uom.id if hours_uom else False,
                "unit_amount": 1.0}

    def _prepare_account_analytic_line_vals(self):
        self.ensure_one()
        hours_uom = self.env.ref("uom.product_uom_hour")
        return {"account_id": self.worksheet_id.analytic_account_id.id if self.worksheet_id and self.worksheet_id.analytic_account_id else False,
                "amount": ((self.employee_id.timesheet_cost if self.employee_id else 0.0) * self.hours) * -1,
                "company_id": self.worksheet_id.company_id.id if self.worksheet_id.company_id else False,
                "date": self.worksheet_id.date,
                "employee_id": self.employee_id.id if self.employee_id else False,
                "name": self.name,
                "product_uom_id": hours_uom.id if hours_uom else False,
                "unit_amount": self.hours}


class ConstructionWorksheetMaterial(models.Model):
    _name = "construction.worksheet.material"
    _description = "Construction Worksheet Material"

    name = fields.Char(string="Name")
    product_collection_ids = fields.Many2many(string="Collection products",
                                              comodel_name="product.product",
                                              relation="product_product_construction_worksheet_material_rel",
                                              column1="product_product_id",
                                              column2="construction_worksheet_material_id",
                                              compute="_compute_product_collection_ids",
                                              store=True)
    product_id = fields.Many2one(string="Product",
                                 comodel_name="product.product")
    product_uom_id = fields.Many2one(string="UoM",
                                     comodel_name="uom.uom")
    product_uom_qty = fields.Float(string="Quantity",
                                   digits="Product Unit of Measure")
    sequence = fields.Integer(string="Sequence")
    worksheet_id = fields.Many2one(string="Construction worksheet",
                                   comodel_name="construction.worksheet")

    @api.depends("worksheet_id", "worksheet_id.collection_id", "worksheet_id.collection_id.line_ids",
                 "worksheet_id.collection_id.line_ids.product_id")
    def _compute_product_collection_ids(self):
        for rec in self:
            if rec.worksheet_id and rec.worksheet_id.collection_id and rec.worksheet_id.collection_id.line_ids:
                rec.product_collection_ids = [(6, 0, rec.worksheet_id.collection_id.line_ids.mapped("product_id").ids)]
            else:
                rec.product_collection_ids = [(5, 0, 0)]

    @api.onchange("product_id")
    def _onchange_product_id(self):
        update_vals = {"name": False,
                       "product_uom_id": False}
        if self.product_id and self.worksheet_id:
            update_vals["name"] = "%s - %s" % (self.worksheet_id.name, self.product_id.display_name)
        if self.product_id and self.product_id.uom_id:
            update_vals["product_uom_id"] = self.product_id.uom_id.id
        self.update(update_vals)

    def _prepare_account_analytic_line_vals(self):
        self.ensure_one()
        return {"account_id": self.worksheet_id.analytic_account_id.id if self.worksheet_id.analytic_account_id else False,
                "amount": ((self.product_id.standard_price if self.product_id else 0.0) * self.product_uom_qty) * -1,
                "company_id": self.worksheet_id.company_id.id if self.worksheet_id.company_id else False,
                "date": self.worksheet_id.date,
                "name": self.name,
                "product_id": self.product_id.id if self.product_id else False,
                "product_uom_id": self.product_uom_id.id if self.product_uom_id else False,
                "unit_amount": self.product_uom_qty}

    def _prepare_stock_move_line_vals(self, picking=False):
        self.ensure_one()
        return {"location_dest_id": picking.location_dest_id.id if picking and picking.location_dest_id else False,
                "location_id": picking.location_id.id if picking and picking.location_id else False,
                "picking_id": picking.id if picking else False,
                "product_id": self.product_id.id if self.product_id else False,
                "product_uom_id": self.product_uom_id.id if self.product_uom_id else False,
                "qty_done": self.product_uom_qty}
