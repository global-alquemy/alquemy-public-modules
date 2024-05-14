# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _


SELECTION_HEADER_OPTIONS = [("readonly", _("Readonly"))]

SELECTION_HEADER_SPECIAL_OPTIONS = [("compute", _("Compute")),
                                    ("readonly", _("Readonly"))]

SELECTION_LINE_OPTIONS = [("invisible", _("Invisible")),
                          ("readonly", _("Readonly"))]

SELECTION_MEASURE = [("linear", _("Linear meter")),
                     ("square", _("Square meter"))]

SELECTION_THICKNESS_MEASURE = [("cm", _("Centimeters")),
                               ("mm", _("Millimeters"))]
