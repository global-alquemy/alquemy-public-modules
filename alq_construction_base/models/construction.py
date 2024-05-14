# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ConstructionConstruction(models.Model):
    _name = "construction.construction"
    _description = "Construction Construction"

    city = fields.Char(string="City")
    code = fields.Char(string="Code")
    country_id = fields.Many2one(string="Country",
                                 comodel_name="res.country")
    name = fields.Char(string="Name")
    state_id = fields.Many2one(string="State",
                               comodel_name="res.country.state")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    zip = fields.Char(string="Zip")
    zip_id = fields.Many2one(string="Zip location",
                             comodel_name="res.city.zip")

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        if self.zip_id:
            self.city = self.zip_id.city_id.name if self.zip_id.city_id else False
            self.country_id = self.zip_id.country_id.id if self.zip_id.country_id else False
            self.state_id = self.zip_id.state_id.id if self.zip_id.state_id else False
            self.zip = self.zip_id.name


class ConstructionTeam(models.Model):
    _name = "construction.team"
    _description = "Construction Team"

    chief_id = fields.Many2one(string="Chief",
                               comodel_name="hr.employee")
    code = fields.Char(string="Code")
    employee_ids = fields.Many2many(string="Employees",
                                    comodel_name="hr.employee",
                                    relation="hr_employee_construction_team_rel",
                                    column1="hr_employee_id",
                                    column2="construction_team_id")
    name = fields.Char(string="Name")
