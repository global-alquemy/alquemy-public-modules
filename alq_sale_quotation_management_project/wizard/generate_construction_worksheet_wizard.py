# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class GenerateConstructionWorksheetWizard(models.TransientModel):
    _inherit = "generate.construction.worksheet.wizard"

    filtered_piecework_ids = fields.Many2many(string="Filtered pieceworks",
                                              comodel_name="construction.piecework",
                                              relation="filtered_cp_gcww_rel",
                                              column1="cp_id",
                                              column2="gcww_id",
                                              compute="_compute_filtered_piecework_ids",
                                              store=True)
    piecework_ids = fields.Many2many(string="Pieceworks auto-generated",
                                     comodel_name="construction.piecework",
                                     relation="cp_gcww_rel",
                                     column1="cp_id",
                                     column2="gcww_id")

    @api.depends("date", "project_id", "project_id.business_line_id", "project_id.chief_id",
                 "project_id.chief_id.job_id", "project_id.employee_ids", "project_id.employee_ids.job_id",
                 "project_id.operating_unit_id", "project_id.surface_id")
    def _compute_filtered_piecework_ids(self):
        for rec in self:
            filtered_pieceworks = False
            cp_domain = []
            if rec.project_id and rec.project_id.business_line_id:
                cp_domain += [("business_line_id", "=", rec.project_id.business_line_id.id)]
            if rec.project_id and rec.project_id.chief_id and rec.project_id.employee_ids:
                job_ids = []
                if rec.project_id.chief_id.job_id:
                    job_ids += [rec.project_id.chief_id.job_id.id]
                for employee in rec.project_id.employee_ids:
                    if employee.job_id:
                        job_ids += [employee.job_id.id]
                if job_ids:
                    job_ids = list(set(job_ids))
                    cp_domain += [("job_id", "in", job_ids)]
            if rec.project_id and rec.project_id.operating_unit_id:
                cp_domain += [("operating_unit_ids", "in", [rec.project_id.operating_unit_id.id])]
            if rec.project_id and rec.project_id.surface_id:
                cp_domain += [("surface_id", "=", rec.project_id.surface_id.id)]
            pieceworks = self.env["construction.piecework"].search(cp_domain)
            if pieceworks and rec.date:
                filtered_pieceworks = pieceworks.filtered(lambda f: (not f.start_date or rec.date >= f.start_date) and (not f.end_date or rec.date <= f.end_date))
            if filtered_pieceworks:
                rec.filtered_piecework_ids = [(6, 0, filtered_pieceworks.ids)]
            else:
                rec.filtered_piecework_ids = [(5, 0, 0)]

    def generate_construction_worksheet(self):
        res = super(GenerateConstructionWorksheetWizard, self).generate_construction_worksheet()
        self.ensure_one()
        if res.get("res_model", False) and res.get("res_id", False):
            worksheet = self.env[res["res_model"]].browse(res["res_id"])
            if worksheet and self.auto_employee_lines and self.piecework_ids:
                line_sequence = 10
                if self.project_id.chief_id:
                    for piecework in self.piecework_ids:
                        if self.project_id.chief_id.job_id and piecework.job_id and self.project_id.chief_id.job_id.id == piecework.job_id.id:
                            cwp_vals = self.project_id._prepare_worksheet_piecework_vals(employee=self.project_id.chief_id,
                                                                                        piecework=piecework,
                                                                                        sequence=line_sequence)
                            cwp_vals["worksheet_id"] = worksheet.id
                            self.env["construction.worksheet.piecework"].create(cwp_vals)
                            line_sequence += 10
                for employee in self.project_id.employee_ids:
                    for piecework in self.piecework_ids:
                        if employee.job_id and piecework.job_id and employee.job_id.id == piecework.job_id.id:
                            cwp_vals = self.project_id._prepare_worksheet_piecework_vals(employee=employee,
                                                                                        piecework=piecework,
                                                                                        sequence=line_sequence)
                            cwp_vals["worksheet_id"] = worksheet.id
                            self.env["construction.worksheet.piecework"].create(cwp_vals)
                            line_sequence += 10
        return res
