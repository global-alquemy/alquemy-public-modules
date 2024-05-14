# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Alquemy Construction Base",
    "version": "15.0.0.0.0",
    "author": "Alquemy",
    "website": "https://www.alquemy.es",
    "license": "AGPL-3",
    "category": "Project Management",
    "depends": ["base",
                "hr",
                "base_location"],
    "data": ["security/ir.model.access.csv",
             "views/construction_view.xml"],
    "installable": True,
    "application": True,
}
