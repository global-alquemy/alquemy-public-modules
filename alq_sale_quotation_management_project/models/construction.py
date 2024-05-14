# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ConstructionHour(models.Model):
    _name = "construction.hour"
    _description = "Construction Hour"

    business_line_ids = fields.Many2many(string="Business lines",
                                         comodel_name="sale.quotation.template.business",
                                         relation="sqt_business_construction_hour_rel",
                                         column1="sqt_business_id",
                                         column2="construction_hour_id")
    company_id = fields.Many2one(string="Company",
                                 comodel_name="res.company",
                                 default=lambda self: self.env.company.id)
    end_date = fields.Date(string="End date")
    name = fields.Char(string="Name")
    operating_unit_ids = fields.Many2many(string="Operating unit",
                                          comodel_name="operating.unit",
                                          relation="operating_unit_construction_hour_rel",
                                          column1="operating_unit_id",
                                          column2="construction_hour_id")
    regular_hours = fields.Float(string="Regular hours")
    start_date = fields.Date(string="Start date")

    def duplicate_hours(self):
        for rec in self:
            copy_text = _("copy")
            default = {"name": "%s (%s)" % (rec.name, copy_text)}
            rec.copy(default=default)

    @api.depends("name", "surface_id")
    def name_get(self):
        res = []
        for rec in self:
            display_name = ""
            if rec.name:
                display_name += rec.name
            if rec.name and rec.regular_hours:
                display_name += " ("
            if rec.regular_hours:
                display_name += "%s)" % "{0:02.0f}:{1:02.0f}".format(*divmod(rec.regular_hours * 60, 60))
            res.append((rec.id, display_name))
        return res


class ConstructionPiecework(models.Model):
    _name = "construction.piecework"
    _description = "Construction Piecework"

    amount = fields.Float(string="Amount",
                          digits="Product Price")
    business_line_id = fields.Many2one(string="Business line",
                                       comodel_name="sale.quotation.template.business")
    company_id = fields.Many2one(string="Company",
                                 comodel_name="res.company",
                                 default=lambda self: self.env.company.id)
    end_date = fields.Date(string="End date")
    job_id = fields.Many2one(string="Job",
                             comodel_name="hr.job")
    min_amount = fields.Float(string="Min. amount",
                              digits="Product Price")
    min_uom_qty = fields.Float(string="Min. quantity",
                               digits="Product Unit of Measure")
    name = fields.Char(string="Name")
    operating_unit_ids = fields.Many2many(string="Operating unit",
                                          comodel_name="operating.unit",
                                          relation="operating_unit_construction_piecework_rel",
                                          column1="operating_unit_id",
                                          column2="construction_piecework_id")
    settlement_type = fields.Selection(string="Settlement type",
                                       selection=[("construction", "Per construction"),
                                                  ("diary", "Diary"),
                                                  ("monthly", "Monthly")])
    start_date = fields.Date(string="Start date")
    surface_id = fields.Many2one(string="Surface type",
                                 comodel_name="construction.surface")
    uom_id = fields.Many2one(string="UoM",
                             comodel_name="uom.uom")

    def duplicate_pieceworks(self):
        for rec in self:
            copy_text = _("copy")
            default = {"name": "%s (%s)" % (rec.name, copy_text)}
            rec.copy(default=default)

    @api.depends("name", "surface_id")
    def name_get(self):
        res = []
        for rec in self:
            display_name = ""
            if rec.name:
                display_name += rec.name
            if rec.name and rec.job_id and rec.job_id.name:
                display_name += " ["
            if rec.job_id and rec.job_id.name:
                display_name += "%s]" % rec.job_id.name
            if rec.name and rec.surface_id and rec.surface_id.name:
                display_name += " ("
            if rec.surface_id and rec.surface_id.name:
                display_name += "%s)" % rec.surface_id.name
            res.append((rec.id, display_name))
        return res


class ConstructionSurface(models.Model):
    _name = "construction.surface"
    _description = "Construction Surface"

    name = fields.Char(string="Name")


class ConstructionWorksheet(models.Model):
    _inherit = "construction.worksheet"

    piecework_ids = fields.One2many(string="Pieceworks",
                                    comodel_name="construction.worksheet.piecework",
                                    inverse_name="worksheet_id")


class ConstructionWorksheetLine(models.Model):
    _inherit = "construction.worksheet.line"

    extra_hours = fields.Float(string="Extra hours",
                               compute="_compute_hours",
                               store=True)
    hours = fields.Float(compute="_compute_hours")

    @api.depends("end_date", "force_hours", "start_date", "worksheet_id", "worksheet_id.company_id",
                 "worksheet_id.project_id", "worksheet_id.project_id.business_line_id",
                 "worksheet_id.project_id.operating_unit_id")
    def _compute_hours(self):
        for rec in self:
            extra_hours = 0.0
            if rec.force_hours:
                hours = rec.force_hours
            elif rec.end_date and rec.start_date:
                diff = rec.end_date - rec.start_date
                hours = round(diff.total_seconds() / 3600.0, 2)
            else:
                hours = 0.0
            ch_domain = []
            if rec.worksheet_id and rec.worksheet_id.project_id and rec.worksheet_id.project_id.business_line_id:
                ch_domain += [("business_line_ids", "in", [rec.worksheet_id.project_id.business_line_id.id])]
            if rec.worksheet_id and rec.worksheet_id.company_id:
                ch_domain += [("company_id", "=", rec.worksheet_id.company_id.id)]
            if rec.worksheet_id and rec.worksheet_id.project_id and rec.worksheet_id.project_id.operating_unit_id:
                ch_domain += [("operating_unit_ids", "in", [rec.worksheet_id.project_id.operating_unit_id.id])]
            construction_hours = self.env["construction.hour"].search(ch_domain)
            if construction_hours and rec.worksheet_id and rec.worksheet_id.date:
                filtered_construction_hours = construction_hours.filtered(lambda f: (not f.start_date or rec.worksheet_id.date >= f.start_date) and (not f.end_date or rec.worksheet_id.date <= f.end_date))
                if filtered_construction_hours and filtered_construction_hours[:1] and filtered_construction_hours[:1].regular_hours:
                    extra_hours = hours - filtered_construction_hours[:1].regular_hours
                    hours = filtered_construction_hours[:1].regular_hours
            rec.extra_hours = extra_hours
            rec.hours = hours


class ConstructionWorksheetPiecework(models.Model):
    _name = "construction.worksheet.piecework"
    _description = "Construction Worksheet Piecework"

    employee_id = fields.Many2one(string="Employee",
                                  comodel_name="hr.employee")
    piecework_id = fields.Many2one(string="Construction piecework",
                                   comodel_name="construction.piecework")
    piecework_ids = fields.Many2many(string="Pieceworks",
                                     comodel_name="construction.piecework",
                                     relation="construction_piecework_construction_worksheet_piecework_rel",
                                     column1="construction_piecework_id",
                                     column2="construction_worksheet_piecework_id",
                                     compute="_compute_piecework_ids",
                                     store=True)
    sequence = fields.Integer(string="Sequence")
    uom_id = fields.Many2one(string="UoM",
                             comodel_name="uom.uom",
                             related="piecework_id.uom_id",
                             readonly=True)
    uom_qty = fields.Float(string="Quantity",
                           digits="Product Unit of Measure")
    worksheet_id = fields.Many2one(string="Construction worksheet",
                                   comodel_name="construction.worksheet")

    @api.depends("employee_id", "employee_id.job_id", "worksheet_id", "worksheet_id.company_id",
                 "worksheet_id.date", "worksheet_id.project_id", "worksheet_id.project_id.business_line_id",
                 "worksheet_id.project_id.operating_unit_id", "worksheet_id.project_id.surface_id")
    def _compute_piecework_ids(self):
        for rec in self:
            filtered_pieceworks = False
            cp_domain = []
            if rec.worksheet_id and rec.worksheet_id.project_id and rec.worksheet_id.project_id.business_line_id:
                cp_domain += [("business_line_id", "=", rec.worksheet_id.project_id.business_line_id.id)]
            if rec.worksheet_id and rec.worksheet_id.company_id:
                cp_domain += [("company_id", "=", rec.worksheet_id.company_id.id)]
            if rec.employee_id and rec.employee_id.job_id:
                cp_domain += [("job_id", "=", rec.employee_id.job_id.id)]
            if rec.worksheet_id and rec.worksheet_id.project_id and rec.worksheet_id.project_id.operating_unit_id:
                cp_domain += [("operating_unit_ids", "in", [rec.worksheet_id.project_id.operating_unit_id.id])]
            if rec.worksheet_id and rec.worksheet_id.project_id and rec.worksheet_id.project_id.surface_id:
                cp_domain += [("surface_id", "=", rec.worksheet_id.project_id.surface_id.id)]
            pieceworks = self.env["construction.piecework"].search(cp_domain)
            if pieceworks and rec.worksheet_id and rec.worksheet_id.date:
                filtered_pieceworks = pieceworks.filtered(lambda f: (not f.start_date or rec.worksheet_id.date >= f.start_date) and (not f.end_date or rec.worksheet_id.date <= f.end_date))
            if filtered_pieceworks:
                rec.piecework_ids = [(6, 0, filtered_pieceworks.ids)]
            else:
                rec.piecework_ids = [(5, 0, 0)]
