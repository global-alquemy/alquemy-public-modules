# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Alquemy Sale Quotation Management CRM",
    "version": "15.0.0.0.0",
    "author": "Alquemy",
    "website": "https://www.alquemy.es",
    "license": "AGPL-3",
    "category": "Sales Management",
    "depends": ["base",
                "crm",
                "sale",
                "sale_crm",
                "crm_operating_unit",
                "alq_analytic_sale",
                "alq_construction_base",
                "alq_sale_quotation_management"],
    "data": ["views/construction_view.xml",
             "views/crm_view.xml",
             "views/sale_quotation_view.xml",
             "views/sale_view.xml",
             "wizard/generate_sale_quotation_wizard_view.xml"],
    "installable": True,
    "application": True,
}
