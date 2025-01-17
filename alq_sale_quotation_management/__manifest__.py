# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Alquemy Sale Quotation Management",
    "version": "15.0.0.0.0",
    "author": "Alquemy",
    "website": "https://www.alquemy.es",
    "license": "AGPL-3",
    "category": "Sales Management",
    "depends": ["base",
                "account",
                "analytic",
                "mail",
                "product",
                "sale",
                "commission",
                "operating_unit",
                "sale_operating_unit",
                "partner_manual_rank",
                "product_dimension",
                "web_domain_field",
                "alq_analytic_sale",
                "alq_construction_base"],
    "data": ["security/ir.model.access.csv",
             "data/ir_sequence.xml",
             "data/mail_template.xml",
             "data/product_product.xml",
             "data/sale_quotation_template_discount.xml",
             "data/sale_quotation_template_field.xml",
             "views/account_view.xml",
             "views/product_view.xml",
             "views/res_view.xml",
             "views/sale_quotation_template_view.xml",
             "views/sale_quotation_view.xml",
             "views/sale_view.xml",
             "wizard/generate_sale_quotation_wizard_view.xml",
             "wizard/sale_advance_payment_inv_view.xml"],
    "assets": {"web.assets_common": ["alq_sale_quotation_management/static/src/css/quotation.scss",
                                     "alq_sale_quotation_management/static/src/js/form_renderer.js"]},
    "installable": True,
    "application": True,
}
