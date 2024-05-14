# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    chief_id = fields.Many2one(string="Chief",
                               comodel_name="hr.employee",
                               tracking=True)
    collection_id = fields.Many2one(string="Collection order",
                                    comodel_name="collection.order",
                                    tracking=True)
    construction_closed = fields.Boolean(string="Construction closed",
                                         tracking=True)
    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction")
    construction_location_id = fields.Many2one(string="Construction location",
                                               comodel_name="stock.location",
                                               tracking=True)
    construction_team_id = fields.Many2one(string="Construction team",
                                           comodel_name="construction.team")
    construction_warehouse_id = fields.Many2one(string="Construction warehouse",
                                                comodel_name="stock.warehouse",
                                                tracking=True)
    employee_ids = fields.Many2many(string="Employees",
                                    comodel_name="hr.employee",
                                    relation="hr_employee_project_project_rel",
                                    column1="hr_employee_id",
                                    column2="project_project_id")
    is_construction = fields.Boolean(string="Is construction",
                                     tracking=True)
    partner_shipping_id = fields.Many2one(string="Delivery address",
                                          comodel_name="res.partner",
                                          tracking=True)
    vehicle_ids = fields.Many2many(string="Vehicles",
                                   comodel_name="fleet.vehicle",
                                   relation="fleet_vehicle_project_project_rel",
                                   column1="fleet_vehicle_id",
                                   column2="project_project_id")
    worksheet_ids = fields.One2many(string="Worksheets",
                                    comodel_name="construction.worksheet",
                                    inverse_name="project_id")
    worksheet_picking_ids = fields.Many2many(string="Worksheet pickings",
                                             comodel_name="stock.picking",
                                             relation="worksheet_picking_project_rel",
                                             column1="picking_id",
                                             column2="project_id",
                                             compute="_compute_worksheet_pickings",
                                             store=True)
    worksheet_pickings_count = fields.Integer(string="Worksheet pickings count",
                                              compute="_compute_worksheet_pickings",
                                              store=True)
    worksheets_count = fields.Integer(string="Worksheets count",
                                      compute="_compute_worksheets_count",
                                      store=True)

    @api.depends("worksheet_ids", "worksheet_ids.picking_ids")
    def _compute_worksheet_pickings(self):
        for rec in self:
            pickings = rec.mapped("worksheet_ids.picking_ids")
            if pickings:
                rec.worksheet_picking_ids = [(6, 0, pickings.ids)]
                rec.worksheet_pickings_count = len(pickings)
            else:
                rec.worksheet_picking_ids = [(5, 0, 0)]
                rec.worksheet_pickings_count = 0

    @api.depends("worksheet_ids")
    def _compute_worksheets_count(self):
        for rec in self:
            rec.worksheets_count = len(rec.worksheet_ids) if rec.worksheet_ids else 0

    @api.onchange("construction_team_id")
    def _onchange_construction_team_id(self):
        chief_id = False
        employee_ids = []
        if self.construction_team_id and self.construction_team_id.chief_id:
            chief_id = self.construction_team_id.chief_id.id
        if self.construction_team_id and self.construction_team_id.employee_ids:
            employee_ids += self.construction_team_id.employee_ids.ids
        self.employee_ids = [(6, 0, employee_ids)] if employee_ids else [(5, 0, 0)]
        self.chief_id = chief_id

    def _prepare_worksheet_line_vals(self, date=False, employee=False, sequence=10):
        self.ensure_one()
        name = "%s PT%s - %s" % (self.name, date.strftime("%Y%m%d") if date else "n/a", employee.name)
        return {"employee_id": employee.id if employee else False,
                "name": name,
                "sequence": sequence}

    def _prepare_worksheet_material_vals(self, date=False, product=False, quantity=0.0, sequence=10):
        self.ensure_one()
        name = "%s PT%s - %s" % (self.name, date.strftime("%Y%m%d") if date else "n/a", product.display_name if product else "n/a")
        return {"name": name,
                "product_id": product.id if product else False,
                "product_uom_id": product.uom_id.id if product and product.uom_id else False,
                "product_uom_qty": quantity,
                "sequence": sequence}

    def _prepare_worksheet_vals(self, date=False):
        self.ensure_one()
        name = "%s PT%s" % (self.name, date.strftime("%Y%m%d") if date else "n/a")
        return {"analytic_account_id": self.analytic_account_id.id if self.analytic_account_id else False,
                "collection_id": self.collection_id.id if self.collection_id else False,
                "company_id": self.company_id.id if self.company_id else False,
                "construction_id": self.construction_id.id if self.construction_id else False,
                "construction_location_id": self.construction_location_id.id if self.construction_location_id else False,
                "construction_warehouse_id": self.construction_warehouse_id.id if self.construction_warehouse_id else False,
                "date": date,
                "name": name,
                "operating_unit_id": self.operating_unit_id.id if self.operating_unit_id else False,
                "project_id": self.id,
                "state": "draft",
                "user_id": self.env.user.id}

    def action_close_construction_project(self):
        for rec in self:
            if not rec.date:
                raise UserError(_("Please, set an end date before closing."))
            sq_domain = [("location_id", "child_of", [rec.construction_location_id.id])]
            if rec.company_id:
                sq_domain += [("company_id", "=", rec.company_id.id)]
            quants = self.env["stock.quant"].search(sq_domain)
            if quants.filtered(lambda f: f.quantity != 0.0):
                raise UserError(_("Please, check the construction stock before closing."))
            rec.construction_closed = True

    def action_construction_worksheets_new(self):
        self.ensure_one()
        gcww_values = {"project_id": self.id}
        wizard = self.env["generate.construction.worksheet.wizard"].create(gcww_values)
        return {"res_id": wizard.id,
                "res_model": "generate.construction.worksheet.wizard",
                "target": "new",
                "type": "ir.actions.act_window",
                "view_id": self.env.ref("alq_project_management.generate_construction_worksheet_wizard_form").id,
                "view_mode": "form"}

    def action_reopen_construction_project(self):
        for rec in self:
            values = {"date": False,
                      "construction_closed": False}
            rec.write(values)

    def button_view_construction_worksheets(self):
        self.ensure_one()
        if self.worksheet_ids:
            return {"domain": [("id", "in", self.worksheet_ids.ids)],
                    "name": _("Construction worksheets"),
                    "res_model": "construction.worksheet",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def button_view_current_stock(self):
        self.ensure_one()
        locations = [self.construction_location_id.id] if self.construction_location_id else []
        action = self.env.ref("stock.location_open_quants").read()[0]
        if action:
            action["context"] = {"search_default_productgroup": 1}
            action["domain"] = [("location_id", "child_of", locations)]
        else:
            action = {"context": {"search_default_productgroup": 1},
                      "domain": [("location_id", "child_of", locations)],
                      "name": _("Current stock"),
                      "res_model": "stock.quant",
                      "src_model": "project.project",
                      "src_id": self.id,
                      "target": "main",
                      "type": "ir.actions.act_window",
                      "view_mode": "tree,form"}
        return action

    def button_view_worksheet_pickings(self):
        self.ensure_one()
        if self.worksheet_picking_ids:
            return {"domain": [("id", "in", self.worksheet_picking_ids.ids)],
                    "name": _("Pickings"),
                    "res_model": "stock.picking",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def unlink(self):
        for rec in self:
            if rec.is_construction:
                error_msg = _("You can't delete construction project.")
                raise UserError(error_msg)
        return super(ProjectProject, self).unlink()
