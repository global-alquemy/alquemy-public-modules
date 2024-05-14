# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction")
    next_subsequence = fields.Char(string="Next subsequence",
                                   default="A")
    next_version = fields.Integer(string="Next version",
                                  default=1)
    operating_unit_blocked = fields.Boolean(string="Operating unit blocked",
                                            compute="_compute_operating_unit_blocked")
    operating_unit_id = fields.Many2one(related=False,
                                        store=True)
    quotation_count = fields.Integer(compute="_compute_quotation_data")
    quotation_ids = fields.One2many(string="Quotations",
                                    comodel_name="sale.quotation",
                                    inverse_name="lead_id")
    quotation_sequence = fields.Char(string="Quotation sequence")
    sale_amount_total = fields.Monetary(compute="_compute_sale_data")
    sale_order_count = fields.Integer(compute="_compute_sale_data")

    @api.depends("quotation_ids", "quotation_ids.state")
    def _compute_operating_unit_blocked(self):
        for rec in self:
            rec.operating_unit_blocked = False
            if rec.quotation_ids and rec.quotation_ids.filtered(lambda f: f.state == "done"):
                rec.operating_unit_blocked = True

    @api.depends("quotation_ids")
    def _compute_quotation_data(self):
        for rec in self:
            rec.quotation_count = len(rec.quotation_ids) if rec.quotation_ids else 0

    @api.depends("order_ids", "order_ids.amount_untaxed", "order_ids.currency_id", "order_ids.company_id", "order_ids.date_order", "order_ids.state")
    def _compute_sale_data(self):
        for rec in self:
            total = 0.0
            sale_order_count = 0
            company_currency = rec.company_currency or self.env.company.currency_id
            for order in rec.order_ids:
                if order.state not in ["cancel", "draft", "sent"]:
                    sale_order_count += 1
                    total += order.currency_id._convert(order.amount_untaxed,
                                                        company_currency,
                                                        order.company_id,
                                                        order.date_order or fields.Date.today())
            rec.sale_amount_total = total
            rec.sale_order_count = sale_order_count

    def action_sale_quotations_new(self):
        self.ensure_one()
        construction_address = False
        if self.partner_id and self.construction_id:
            rp_domain = [("name", "=", self.construction_id.name),
                         ("parent_id", "=", self.partner_id.id),
                         ("type", "=", "delivery")]
            construction_address = self.env["res.partner"].search(rp_domain, limit=1)
            if not construction_address:
                rp_values = {"city": self.construction_id.city,
                             "country_id": self.construction_id.country_id.id if self.construction_id.country_id else False,
                             "name": self.construction_id.name,
                             "parent_id": self.partner_id.id,
                             "state_id": self.construction_id.state_id.id if self.construction_id.state_id else False,
                             "street": self.construction_id.street,
                             "street2": self.construction_id.street2,
                             "type": "delivery",
                             "zip": self.construction_id.zip}
                construction_address = self.env["res.partner"].create(rp_values)
        dsipw_values = {"lead_id": self.id,
                        "operating_unit_id": self.operating_unit_id.id if self.operating_unit_id else False,
                        "partner_id": self.partner_id.id if self.partner_id else False,
                        "partner_shipping_id": construction_address.id if construction_address else False}
        if self.quotation_sequence and self.next_subsequence:
            dsipw_values["quotation_name"] = "%s-%s-a" % (self.quotation_sequence, self.next_subsequence)
        wizard = self.env["generate.sale.quotation.wizard"].create(dsipw_values)
        return {"res_id": wizard.id,
                "res_model": "generate.sale.quotation.wizard",
                "target": "new",
                "type": "ir.actions.act_window",
                "view_id": self.env.ref("alq_sale_quotation_management.generate_sale_quotation_wizard_form").id,
                "view_mode": "form"}

    def action_view_sale_quotation(self):
        self.ensure_one()
        if self.quotation_ids:
            return {"domain": [("id", "in", self.quotation_ids.ids)],
                    "name": _("Sale quotations"),
                    "res_model": "sale.quotation",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}
