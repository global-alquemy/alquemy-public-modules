# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Alquemy Sale Quotation Management Project",
    "version": "15.0.0.0.0",
    "author": "Alquemy",
    "website": "https://www.alquemy.es",
    "license": "AGPL-3",
    "category": "Sales Management",
    "depends": ["base",
                "account",
                "analytic",
                "project",
                "operating_unit",
                "project_operating_unit",
                "project_template",
                "stock_operating_unit",
                "alq_construction_base",
                "alq_project_management",
                "alq_sale_quotation_management"],
    "data": ["security/ir.model.access.csv",
             "views/collection_view.xml",
             "views/construction_view.xml",
             "views/project_view.xml",
             "views/sale_quotation_template_view.xml",
             "views/sale_quotation_view.xml",
             "wizard/generate_construction_worksheet_wizard_view.xml"],
    "installable": True,
    "application": True,
}
