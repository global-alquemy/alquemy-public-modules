# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Alquemy Project Management",
    "version": "15.0.0.0.0",
    "author": "Alquemy",
    "website": "https://www.alquemy.es",
    "license": "AGPL-3",
    "category": "Project Management",
    "depends": ["base",
                "account",
                "analytic",
                "fleet",
                "product",
                "project",
                "purchase",
                "stock",
                "hr_timesheet",
                "operating_unit",
                "partner_manual_rank",
                "project_template",
                "project_timeline",
                "purchase_location_by_line",
                "stock_operating_unit",
                "alq_construction_base"],
    "data": ["security/ir.model.access.csv",
             "views/base_construction_menu_view.xml",
             "views/collection_view.xml",
             "views/construction_view.xml",
             "views/product_view.xml",
             "views/project_view.xml",
             "views/purchase_view.xml",
             "views/stock_view.xml",
             "wizard/generate_construction_worksheet_wizard_view.xml"],
    "installable": True,
    "application": True,
}
