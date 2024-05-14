# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _
from odoo.exceptions import UserError


class GenerateConstructionWorksheetWizard(models.TransientModel):
    _name = "generate.construction.worksheet.wizard"
    _description = "Generate Construction Worksheet Wizard"

    auto_employee_lines = fields.Boolean(string="Employee lines auto-generation",
                                         default=True)
    consume_remaining_material = fields.Boolean(string="Consume remaining material")
    date = fields.Date(string="Date",
                       default=fields.Date.today)
    project_id = fields.Many2one(string="Project",
                                 comodel_name="project.project")

    def generate_construction_worksheet(self):
        self.ensure_one()
        if not self.project_id:
            raise UserError(_("You must select a project."))
        cw_vals = self.project_id._prepare_worksheet_vals(date=self.date)
        worksheet = self.env["construction.worksheet"].create(cw_vals)
        if worksheet and self.auto_employee_lines:
            line_sequence = 10
            if self.project_id.chief_id:
                cwl_vals = self.project_id._prepare_worksheet_line_vals(date=self.date,
                                                                        employee=self.project_id.chief_id,
                                                                        sequence=line_sequence)
                cwl_vals["worksheet_id"] = worksheet.id
                self.env["construction.worksheet.line"].create(cwl_vals)
                line_sequence += 10
            for employee in self.project_id.employee_ids:
                cwl_vals = self.project_id._prepare_worksheet_line_vals(self.date,
                                                                        employee=employee,
                                                                        sequence=line_sequence)
                cwl_vals["worksheet_id"] = worksheet.id
                self.env["construction.worksheet.line"].create(cwl_vals)
                line_sequence += 10
        if worksheet and not self.consume_remaining_material and self.project_id and self.project_id.collection_id:
            material_sequence = 10
            for product in self.project_id.collection_id.line_ids.filtered(lambda f: f.material_control).mapped("product_id"):
                quantity = 0.0
                cwm_vals = self.project_id._prepare_worksheet_material_vals(date=self.date,
                                                                            product=product,
                                                                            quantity=quantity,
                                                                            sequence=line_sequence)
                cwm_vals["worksheet_id"] = worksheet.id
                self.env["construction.worksheet.material"].create(cwm_vals)
                material_sequence += 10
        if worksheet and self.consume_remaining_material and self.project_id.construction_location_id:
            material_sequence = 10
            sq_domain = [("location_id", "child_of", [self.project_id.construction_location_id.id])]
            if self.project_id.company_id:
                sq_domain += [("company_id", "=", self.project_id.company_id.id)]
            quants = self.env["stock.quant"].search(sq_domain)
            for product in quants.mapped("product_id"):
                quantity = sum(quants.filtered(lambda f: f.product_id == product).mapped("quantity"))
                if quantity > 0:
                    cwm_vals = self.project_id._prepare_worksheet_material_vals(date=self.date,
                                                                                product=product,
                                                                                quantity=quantity,
                                                                                sequence=line_sequence)
                    cwm_vals["worksheet_id"] = worksheet.id
                    self.env["construction.worksheet.material"].create(cwm_vals)
                    material_sequence += 10
        form_view = self.env.ref("alq_project_management.construction_worksheet_form")
        return {"context": {},
                "name": _("Construction worksheet"),
                "res_model": "construction.worksheet",
                "res_id": worksheet.id,
                "src_model": "generate.construction.worksheet.wizard",
                "src_id": self.id,
                "target": "current",
                "type": "ir.actions.act_window",
                "view_id": form_view.id if form_view else False,
                "view_mode": "form"}
