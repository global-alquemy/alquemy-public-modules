# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    business_line_id = fields.Many2one(string="Business line",
                                       comodel_name="sale.quotation.template.business",
                                       tracking=True)
    default_piecework_ids = fields.Many2many(string="Default pieceworks",
                                             comodel_name="construction.piecework",
                                             relation="c_piecework_p_project_rel",
                                             column1="piecework_id",
                                             column2="project_id")
    filtered_piecework_ids = fields.Many2many(string="Filtered pieceworks",
                                              comodel_name="construction.piecework",
                                              relation="filtered_cp_pp_rel",
                                              column1="piecework_id",
                                              column2="project_id",
                                              compute="_compute_filtered_piecework_ids",
                                              store=True)
    labor_quotation_amount = fields.Monetary(string="Labor quotation amount",
                                             compute="_compute_labor_quotation_amount",
                                             currency_field="currency_id",
                                             store=True)
    quotation_id = fields.Many2one(string="Quotation",
                                   comodel_name="sale.quotation",
                                   tracking=True)
    surface_id = fields.Many2one(string="Surface type",
                                 comodel_name="construction.surface")

    @api.depends("business_line_id", "chief_id", "chief_id.job_id",
                 "date", "date_start", "employee_ids", "employee_ids.job_id",
                 "operating_unit_id", "surface_id")
    def _compute_filtered_piecework_ids(self):
        for rec in self:
            filtered_pieceworks = False
            cp_domain = []
            if rec.business_line_id:
                cp_domain += [("business_line_id", "=", rec.business_line_id.id)]
            if rec.chief_id and rec.employee_ids:
                job_ids = []
                if rec.chief_id.job_id:
                    job_ids += [rec.chief_id.job_id.id]
                for employee in rec.employee_ids:
                    if employee.job_id:
                        job_ids += [employee.job_id.id]
                if job_ids:
                    job_ids = list(set(job_ids))
                    cp_domain += [("job_id", "in", job_ids)]
            if rec.operating_unit_id:
                cp_domain += [("operating_unit_ids", "in", [rec.operating_unit_id.id])]
            if rec.surface_id:
                cp_domain += [("surface_id", "=", rec.surface_id.id)]
            pieceworks = self.env["construction.piecework"].search(cp_domain)
            if pieceworks and rec.date_start:
                filtered_pieceworks = pieceworks.filtered(lambda f: (not f.start_date or rec.date_start >= f.start_date) and (not f.end_date or rec.date_start <= f.end_date))
            if pieceworks and rec.date:
                filtered_pieceworks = pieceworks.filtered(lambda f: (not f.start_date or rec.date >= f.start_date) and (not f.end_date or rec.date <= f.end_date))
            if filtered_pieceworks:
                rec.filtered_piecework_ids = [(6, 0, filtered_pieceworks.ids)]
            else:
                rec.filtered_piecework_ids = [(5, 0, 0)]

    @api.depends("quotation_id", "quotation_id.line_ids",
                 "quotation_id.line_ids.is_project_labor", "quotation_id.line_ids.price_total")
    def _compute_labor_quotation_amount(self):
        for rec in self:
            labor_quotation_amount = 0
            if rec.quotation_id and rec.quotation_id.line_ids:
                labor_quotation_amount = sum(rec.quotation_id.line_ids.filtered(lambda f: f.is_project_labor).mapped("price_total"))
            rec.labor_quotation_amount = labor_quotation_amount

    def _prepare_worksheet_piecework_vals(self, employee=False, piecework=False, sequence=10):
        self.ensure_one()
        return {"employee_id": employee.id if employee else False,
                "piecework_id": piecework.id if piecework else False,
                "sequence": sequence,
                "uom_qty": 1.0}

    def action_construction_worksheets_new(self):
        res = super(ProjectProject, self).action_construction_worksheets_new()
        self.ensure_one()
        if res.get("res_id", False) and res.get("res_model", False):
            wizard = self.env[res["res_model"]].browse(res["res_id"])
            if wizard and self.default_piecework_ids:
                wizard.piecework_ids = [(6, 0, self.default_piecework_ids.ids)]
        return res
