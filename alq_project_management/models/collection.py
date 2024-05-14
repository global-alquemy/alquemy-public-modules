# -*- coding: utf-8 -*-
# 2024 Alquemy - Carlos Sánchez Cifuentes <csanchez@alquemy.es>
# 2024 Alquemy - José Antonio Fernández Valls <jafernandez@alquemy.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CollectionOrder(models.Model):
    _name = "collection.order"
    _description = "Collection Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    all_picking_ids = fields.Many2many(string="Stock pickings",
                                       comodel_name="stock.picking",
                                       relation="all_stock_picking_collection_order_rel",
                                       column1="all_stock_picking_id",
                                       column2="collection_order_id",
                                       compute="_compute_all_pickings",
                                       store=True)
    all_pickings_count = fields.Integer(string="All pickings count",
                                        compute="_compute_all_pickings",
                                        store=True)
    analytic_account_id = fields.Many2one(string="Analytic account",
                                          comodel_name="account.analytic.account",
                                          tracking=True)
    company_id = fields.Many2one(string="Company",
                                 comodel_name="res.company",
                                 default=lambda self: self.env.company.id,
                                 tracking=True)
    construction_id = fields.Many2one(string="Construction",
                                      comodel_name="construction.construction",
                                      tracking=True)
    construction_location_id = fields.Many2one(string="Construction location",
                                               comodel_name="stock.location",
                                               tracking=True)
    construction_warehouse_id = fields.Many2one(string="Construction warehouse",
                                                comodel_name="stock.warehouse",
                                                tracking=True)
    end_date = fields.Date(string="End date",
                           tracking=True)
    internal_notes = fields.Text(string="Internal notes",
                                 tracking=True)
    line_ids = fields.One2many(string="Lines",
                               comodel_name="collection.order.line",
                               inverse_name="collection_id")
    name = fields.Char(string="Name",
                       tracking=True)
    operating_unit_id = fields.Many2one(string="Operating unit",
                                        comodel_name="operating.unit",
                                        tracking=True)
    owner_id = fields.Many2one(string="Owner",
                               comodel_name="res.users",
                               tracking=True)
    partner_id = fields.Many2one(string="Partner",
                                 comodel_name="res.partner",
                                 tracking=True)
    partner_shipping_id = fields.Many2one(string="Delivery address",
                                          comodel_name="res.partner",
                                          tracking=True)
    project_id = fields.Many2one(string="Project",
                                 comodel_name="project.project",
                                 tracking=True)
    purchase_order_ids = fields.Many2many(string="Purchase orders",
                                          comodel_name="purchase.order",
                                          relation="purchase_order_collection_order_rel",
                                          column1="purchase_order_id",
                                          column2="collection_order_id",
                                          compute="_compute_purchase_orders",
                                          store=True)
    purchase_orders_count = fields.Integer(string="Purchase orders count",
                                           compute="_compute_purchase_orders",
                                           store=True)
    revision_date = fields.Date(string="Revision date",
                                tracking=True)
    start_date = fields.Date(string="Start date",
                             tracking=True)
    state = fields.Selection(string="State",
                             selection=[("draft", "Draft"),
                                        ("revised", "Revised"),
                                        ("in_progress", "In progress"),
                                        ("done", "Done")],
                             default="draft",
                             tracking=True)
    stock_picking_ids = fields.Many2many(string="Stock pickings",
                                         comodel_name="stock.picking",
                                         relation="stock_picking_collection_order_rel",
                                         column1="stock_picking_id",
                                         column2="collection_order_id",
                                         compute="_compute_stock_pickings",
                                         store=True)
    stock_pickings_count = fields.Integer(string="Stock pickings count",
                                          compute="_compute_stock_pickings",
                                          store=True)
    user_id = fields.Many2one(string="User",
                              comodel_name="res.users",
                              tracking=True)

    @api.depends("purchase_order_ids", "purchase_order_ids.picking_ids", "stock_picking_ids")
    def _compute_all_pickings(self):
        for rec in self:
            purchase_pickings = rec.purchase_order_ids.mapped("picking_ids")
            stock_pickings = rec.stock_picking_ids
            all_pickings = purchase_pickings | stock_pickings
            if all_pickings:
                rec.all_picking_ids = [(6, 0, all_pickings.ids)]
                rec.all_pickings_count = len(all_pickings)
            else:
                rec.all_picking_ids = [(5, 0, 0)]
                rec.all_pickings_count = 0

    @api.depends("line_ids", "line_ids.purchase_line_ids", "line_ids.purchase_line_ids.order_id")
    def _compute_purchase_orders(self):
        for rec in self:
            orders = rec.line_ids.mapped("purchase_line_ids.order_id")
            if orders:
                rec.purchase_order_ids = [(6, 0, orders.ids)]
                rec.purchase_orders_count = len(orders)
            else:
                rec.purchase_order_ids = [(5, 0, 0)]
                rec.purchase_orders_count = 0

    @api.depends("line_ids", "line_ids.stock_move_ids", "line_ids.stock_move_ids.picking_id")
    def _compute_stock_pickings(self):
        for rec in self:
            pickings = rec.line_ids.mapped("stock_move_ids.picking_id")
            if pickings:
                rec.stock_picking_ids = [(6, 0, pickings.ids)]
                rec.stock_pickings_count = len(pickings)
            else:
                rec.stock_picking_ids = [(5, 0, 0)]
                rec.stock_pickings_count = 0

    def action_done(self):
        for rec in self:
            rec.state = "done"
            if not rec.end_date:
                rec.end_date = fields.Date.today()

    def action_draft(self):
        for rec in self:
            rec.state = "draft"

    def action_process_lines(self):
        for rec in self:
            purchase_orders = rec.purchase_order_ids.filtered(lambda r: r.state == "draft")
            pickings = self.env["stock.picking"]
            for line in rec.line_ids.filtered(lambda r: r.action and r.product_uom_qty):
                if line.product_id and line.product_id.is_generic:
                    generic_error_msg = _("The following product is generic, please change it:")
                    raise UserError("%s %s" % (generic_error_msg, line.product_id.display_name))
                if line.action == "purchase":
                    spt_domain = [("code", "=", "incoming"),
                                  ("warehouse_id", "=", rec.construction_warehouse_id.id)]
                    picking_type = self.env["stock.picking.type"].search(spt_domain, limit=1)
                    if not picking_type:
                        raise UserError(_("Picking type not found for selected warehouse."))
                    purchase_order = purchase_orders.filtered(lambda r: r.partner_id == line.partner_id)[:1]
                    if not purchase_order:
                        po_values = {"collection_id": rec.id,
                                     "construction_id": rec.construction_id.id if rec.construction_id else False,
                                     "company_id": rec.company_id.id if rec.company_id else False,
                                     "construction_location_id": rec.construction_location_id.id,
                                     "origin": rec.name,
                                     "operating_unit_id": rec.operating_unit_id.id if rec.operating_unit_id else False,
                                     "partner_id": line.partner_id.id,
                                     "picking_type_id": picking_type.id,
                                     "requesting_operating_unit_id": rec.operating_unit_id.id if rec.operating_unit_id else False}
                        purchase_order = self.env["purchase.order"].create(po_values)
                        if purchase_order:
                            purchase_orders |= purchase_order
                    pol_values = {"account_analytic_id": rec.analytic_account_id.id if rec.analytic_account_id else False,
                                  "collection_notes": line.notes,
                                  "order_id": purchase_order.id,
                                  "product_id": line.product_id.id,
                                  "product_qty": line.product_uom_qty,
                                  "product_uom": line.product_uom_id.id}
                    purchase_order_line = self.env["purchase.order.line"].create(pol_values)
                    if purchase_order_line:
                        line.purchase_line_ids = [(4, purchase_order_line.id)]
                        colh_values = {"collection_line_id": line.id,
                                       "purchase_line_id": purchase_order_line.id}
                        self.env["collection.order.line.history"].create(colh_values)
                elif line.action == "transfer":
                    spt_domain = [("code", "=", "internal"),
                                  ("warehouse_id", "=", line.location_id.warehouse_id.id)]
                    picking_type = self.env["stock.picking.type"].search(spt_domain, limit=1)
                    if not picking_type:
                        raise UserError(_("Picking type not found for selected warehouse."))
                    picking = pickings.filtered(lambda r: r.location_dest_id == rec.construction_location_id and
                                                          r.picking_type_id == picking_type)[:1]
                    if not picking:
                        sp_values = {"collection_id": rec.id,
                                     "construction_id": rec.construction_id.id if rec.construction_id else False,
                                     "location_dest_id": rec.construction_location_id.id,
                                     "location_id": line.location_id.id,
                                     "partner_id": rec.partner_shipping_id.id,
                                     "picking_type_id": picking_type.id}
                        picking = self.env["stock.picking"].create(sp_values)
                        if picking:
                            pickings |= picking
                    sm_values = {"location_dest_id": rec.construction_location_id.id,
                                 "location_id": line.location_id.id,
                                 "name": line.name if line.name else line.product_id.display_name,
                                 "picking_id": picking.id,
                                 "product_id": line.product_id.id,
                                 "product_uom": line.product_uom_id.id,
                                 "product_uom_qty": line.product_uom_qty}
                    stock_move = self.env["stock.move"].create(sm_values)
                    if stock_move:
                        line.stock_move_ids = [(4, stock_move.id)]
                        colh_values = {"collection_line_id": line.id,
                                       "stock_move_id": stock_move.id}
                        self.env["collection.order.line.history"].create(colh_values)
                line.action = False
                line.location_id = False
                line.partner_id = False
                line.product_uom_qty = 0.0
            if pickings:
                pickings.action_confirm()
                pickings.action_assign()
            rec._compute_purchase_orders()
            rec._compute_stock_pickings()

    def action_in_progress(self):
        for rec in self:
            rec.state = "in_progress"
            if not rec.user_id:
                rec.user_id = self.env.user.id
            if not rec.start_date:
                rec.start_date = fields.Date.today()

    def action_revised(self):
        for rec in self:
            rec.state = "revised"
            if not rec.owner_id:
                rec.owner_id = self.env.user.id
            if not rec.revision_date:
                rec.revision_date = fields.Date.today()
            if rec.project_id and not rec.project_id.user_id:
                rec.project_id.user_id = self.env.user.id

    def button_view_all_pickings(self):
        self.ensure_one()
        if self.all_picking_ids:
            return {"context": {"search_default_pendings": 1},
                    "domain": [("id", "in", self.all_picking_ids.ids)],
                    "name": _("Stock pickings"),
                    "res_model": "stock.picking",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def button_view_purchase_orders(self):
        self.ensure_one()
        if self.purchase_order_ids:
            return {"domain": [("id", "in", self.purchase_order_ids.ids)],
                    "name": _("Purchase orders"),
                    "res_model": "purchase.order",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}

    def button_view_stock_pickings(self):
        self.ensure_one()
        if self.stock_picking_ids:
            return {"domain": [("id", "in", self.stock_picking_ids.ids)],
                    "name": _("Stock pickings"),
                    "res_model": "stock.picking",
                    "target": "current",
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,form"}


class CollectionOrderLine(models.Model):
    _name = "collection.order.line"
    _description = "Collection Order Line"

    action = fields.Selection(string="Action",
                              selection=[("purchase", "Purchase"),
                                         ("transfer", "Transfer")],
                              default=False)
    collection_id = fields.Many2one(string="Collection order",
                                    comodel_name="collection.order")
    company_id = fields.Many2one(string="Company",
                                 comodel_name="res.company",
                                 related="collection_id.company_id",
                                 readonly=True)
    currency_id = fields.Many2one(string="Currency",
                                  comodel_name="res.currency",
                                  related="collection_id.company_id.currency_id",
                                  readonly=True)
    done_qty = fields.Float(string="Done quantity",
                            digits="Product Unit of Measure",
                            compute="_compute_done_qty",
                            store=True)
    history_ids = fields.One2many(string="History lines",
                                  comodel_name="collection.order.line.history",
                                  inverse_name="collection_line_id")
    location_id = fields.Many2one(string="Location",
                                  comodel_name="stock.location")
    material_control = fields.Boolean(string="Material control")
    name = fields.Char(string="Name")
    notes = fields.Text(string="Notes")
    operating_unit_id = fields.Many2one(string="Operating unit",
                                        comodel_name="operating.unit",
                                        related="collection_id.operating_unit_id",
                                        readonly=True)
    partner_id = fields.Many2one(string="Partner",
                                 comodel_name="res.partner")
    product_id = fields.Many2one(string="Product",
                                 comodel_name="product.product")
    product_location_ids = fields.Many2many(string="Locations",
                                            comodel_name="stock.location",
                                            relation="stock_location_collection_order_line_rel",
                                            column1="stock_location_id",
                                            column2="collection_order_line_id",
                                            compute="_compute_product_location_ids",
                                            store=True)
    product_seller_ids = fields.Many2many(string="Suppliers",
                                          comodel_name="res.partner",
                                          relation="res_partner_collection_order_line_rel",
                                          column1="res_partner_id",
                                          column2="collection_order_line_id",
                                          compute="_compute_product_seller_ids",
                                          store=True)
    product_uom_id = fields.Many2one(string="UoM",
                                     comodel_name="uom.uom")
    product_uom_qty = fields.Float(string="Quantity",
                                   digits="Product Unit of Measure")
    purchase_line_ids = fields.Many2many(string="Purchase order lines",
                                         comodel_name="purchase.order.line",
                                         relation="purchase_order_line_collection_order_line_rel",
                                         column1="purchase_order_line_id",
                                         column2="collection_order_line_id")
    quotation_price_unit = fields.Float(string="Price unit",
                                        digits="Product Price")
    quotation_product_id = fields.Many2one(string="Quotation product",
                                           comodel_name="product.product")
    quotation_qty = fields.Float(string="Quotation quantity",
                                 digits="Product Unit of Measure")
    required_qty = fields.Float(string="Required quantity",
                                digits="Product Unit of Measure")
    stock_move_ids = fields.Many2many(string="Stock moves",
                                      comodel_name="stock.move",
                                      relation="stock_move_collection_order_line_rel",
                                      column1="stock_move_id",
                                      column2="collection_order_line_id")

    @api.depends("history_ids", "history_ids.purchase_order_state", "history_ids.qty", "history_ids.stock_picking_state")
    def _compute_done_qty(self):
        for rec in self:
            rec.done_qty = sum(rec.history_ids.filtered(lambda f: (f.purchase_order_state and f.purchase_order_state != "cancel") or (f.stock_picking_state and f.stock_picking_state != "cancel")).mapped("qty"))

    @api.depends("action", "product_id", "product_id.qty_available")
    def _compute_product_location_ids(self):
        for rec in self:
            if rec.action in [False, "transfer"]:
                if rec.product_id and rec.company_id:
                    locations = self.env["stock.location"]
                    if rec.product_id.detailed_type and rec.product_id.detailed_type == "product":
                        sq_domain = [("company_id", "in", [False, rec.company_id.id]),
                                    ("product_id", "=", rec.product_id.id),
                                    ("quantity", ">", 0.0)]
                        quants = self.env["stock.quant"].search(sq_domain)
                        locations = quants.filtered(lambda r: r.available_quantity > 0).mapped("location_id").filtered(lambda r: r.usage == "internal")
                    elif rec.product_id.detailed_type and rec.product_id.detailed_type == "consu":
                        sl_domain = [("company_id", "in", [False, rec.company_id.id]),
                                    ("usage", "=", "internal")]
                        locations = self.env["stock.location"].search(sl_domain)
                    if locations:
                        rec.product_location_ids = [(6, 0, locations.ids)]
                    else:
                        rec.product_location_ids = [(5, 0, 0)]
                else:
                    rec.product_location_ids = [(5, 0, 0)]

    @api.depends("product_id", "product_id.seller_ids", "product_id.seller_ids.name")
    def _compute_product_seller_ids(self):
        for rec in self:
            if rec.product_id and rec.product_id.seller_ids:
                rec.product_seller_ids = [(6, 0, rec.product_id.seller_ids.mapped("name").ids)]
            else:
                rec.product_seller_ids = [(5, 0, 0)]

    @api.onchange("product_id")
    def _onchange_product_id(self):
        update_vals = {"product_uom_id": False}
        if self.product_id and self.product_id.uom_id:
            update_vals["product_uom_id"] = self.product_id.uom_id.id
        self.update(update_vals)

    def button_view_history(self):
        self.ensure_one()
        if self.history_ids:
            tree_view = self.env.ref("alq_project_management.collection_order_line_history_tree")
            return {"domain": [("id", "in", self.history_ids.ids)],
                    "name": _("Collection history line"),
                    "res_model": "collection.order.line.history",
                    "target": "new",
                    "type": "ir.actions.act_window",
                    "view_id": tree_view.id if tree_view else False,
                    "view_mode": "tree"}


class CollectionOrderLineHistory(models.Model):
    _name = "collection.order.line.history"
    _description = "Collection Order Line History"

    collection_line_id = fields.Many2one(string="Collection order line",
                                         comodel_name="collection.order.line")
    currency_id = fields.Many2one(string="Currency",
                                  comodel_name="res.currency",
                                  related="collection_line_id.collection_id.company_id.currency_id",
                                  readonly=True)
    purchase_line_id = fields.Many2one(string="Purchase order line",
                                       comodel_name="purchase.order.line")
    purchase_order_id = fields.Many2one(string="Purchase order",
                                        comodel_name="purchase.order",
                                        related="purchase_line_id.order_id",
                                        readonly=True)
    purchase_order_state = fields.Selection(string="Purchase order state",
                                            related="purchase_line_id.order_id.state",
                                            readonly=True)
    purchase_price_unit = fields.Float(string="Purchase price unit",
                                       digits="Product Price",
                                       related="purchase_line_id.price_unit",
                                       readonly=True)
    qty = fields.Float(string="Quantity",
                       digits="Product Unit of Measure",
                       compute="_compute_qty",
                       store=True)
    src_location_id = fields.Many2one(string="Source location",
                                      comodel_name="stock.location",
                                      related="stock_move_id.location_id",
                                      readonly=True)
    stock_move_id = fields.Many2one(string="Stock move",
                                    comodel_name="stock.move")
    stock_picking_id = fields.Many2one(string="Stock picking",
                                       comodel_name="stock.picking",
                                       related="stock_move_id.picking_id",
                                       readonly=True)
    stock_picking_state = fields.Selection(string="Stock picking state",
                                           related="stock_move_id.picking_id.state",
                                           readonly=True)

    @api.depends("purchase_line_id", "purchase_line_id.product_qty",
                 "stock_move_id", "stock_move_id.product_uom_qty", "stock_move_id.quantity_done")
    def _compute_qty(self):
        for rec in self:
            res = 0.0
            if rec.purchase_line_id:
                res += rec.purchase_line_id.product_qty
            if rec.stock_move_id:
                if rec.stock_move_id.state and rec.stock_move_id.state == "done":
                    res += rec.stock_move_id.quantity_done
                else:
                    res += rec.stock_move_id.product_uom_qty
            rec.qty = res
