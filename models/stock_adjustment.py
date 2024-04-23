from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from lxml import etree


class StockAdjustmentOrder(models.Model):
    _name = 'stock.adjustment.order'

    # location_id = fields.Many2one("stock.location", "Area", domain=(
    #     [('location_type', 'not in', ['rack', 'bin']), ('check_type', 'ilike', '_stock')]))
    location_id = fields.Many2one("stock.location", "Area")
    start_date = fields.Datetime("Start Date", default=fields.Datetime.now())
    end_date = fields.Datetime("End Date", default=fields.Datetime.now())
    check_order_ids = fields.One2many(
        "stock.check.order", "adjustment_order_id")
    name = fields.Char('Name', default='New')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')], default='draft')

    def action_confirm(self):
        for check_order in self.check_order_ids:
            if len(check_order.detail_ids) == 0:
                bin_ids = self.env['stock.location'].search(
                    [('location_type', '=', 'bin'), ('location_id', '=', check_order.location_id.id)])
                print(bin_ids)
                quants = self.env["stock.quant"].search(
                    [("location_id", "=", bin_ids.ids),
                     ("available_quantity", ">", 0),
                     ]
                )
                detail_list = []
                for quant in quants:
                    detail_list.append((0, 0, {
                        'bin_id': quant.location_id.id,
                        'product_id': quant.product_id.id,
                        'lot_id': quant.lot_id.id,
                        'available_qty': quant.available_quantity,
                        'on_hand_qty': quant.quantity,
                        'quant_id': quant.id
                    }))
                    print(type(quant.available_quantity))
                    print(type(quant.quantity))
                check_order.detail_ids = detail_list
                print(quants)
        self.state = 'confirmed'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.adjustment.order') or 'New'
        res = super(StockAdjustmentOrder, self).create(vals)
        return res


class StockCheckOrder(models.Model):
    _name = 'stock.check.order'
    parent_location = fields.Many2one(
        "stock.location", "Parent Location", related='adjustment_order_id.location_id')

    location_id = fields.Many2one(
        "stock.location", "Rack",
        domain="[('id', 'child_of', parent_location), ('id', '!=', parent_location),('location_type','=','rack')]")
    rack_name = fields.Char(related='location_id.name')
    worker_id = fields.Many2many("res.partner")
    start_date = fields.Datetime("Start Date", default=fields.Datetime.now())
    end_date = fields.Datetime("End Date", default=fields.Datetime.now())
    adjustment_order_id = fields.Many2one("stock.adjustment.order")
    detail_ids = fields.One2many("stock.check.order.detail", "check_order_id")
    name = fields.Char('Name', default='New')
    show_apply = fields.Boolean(compute='show_apply_button')

    def show_apply_button(self):
        for rec in self:
            rec.show_apply = any(rec.detail_ids.filtered(lambda line: line.difference != 0))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.check.order') or 'New'
        res = super(StockCheckOrder, self).create(vals)
        return res

    @api.onchange('adjustment_order_id')
    def onchange_adjustment_order_id(self):
        if self.adjustment_order_id:
            self.location_id = self.adjustment_order_id.location_id
        else:
            self.location_id = False

    def apply_new_difference_quantity(self):
        quant_to_update = []
        check_order_detail_to_update = []
        for detail in self.detail_ids:
            if detail.difference != 0:
                if detail.quant_id:
                    detail.quant_id.inventory_quantity = detail.counted_qty
                quant_to_update.append(detail.quant_id.id)
                check_order_detail_to_update.append(detail.id)
        domain = [('id', 'in', quant_to_update)]
        # hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_location = False
        # hide_lot = all(product.tracking == 'none' for product in self)
        hide_lot = False
        self = self.with_context(
            hide_location=hide_location, hide_lot=hide_lot,
            no_at_date=True, search_default_on_hand=True,
        )

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        self = self.with_context(check_order=self.id)
        self = self.with_context(quant_to_update=check_order_detail_to_update)
        self = self.with_context(save_check_order=True)
        context = self.env.context
        action = self.env['stock.quant'].action_view_inventory_stock_order()
        action['domain'] = domain
        action["name"] = _('Update Quantity')
        return action

    def save_check_order_detail(self, quant_to_update):
        context = self.env.context
        detail_to_update = self.detail_ids.filtered(lambda line: line.id in quant_to_update)
        for detail in detail_to_update:
            detail.available_qty = detail.quant_id.available_quantity
            detail.on_hand_qty = detail.quant_id.quantity
            detail.difference = 0

        return {
            'name': self.name,
            'res_model': "stock.check.order",
            'view_id': self.env.ref('autonsi_stock_adjustment.view_stock_check_order_form').id,
            "view_type": "form",
            "view_mode": "form",
            'target': "current",
            'res_id': self.id,
            'type': 'ir.actions.act_window'
        }


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def action_view_inventory_stock_order(self):
        """ Similar to _get_quants_action except specific for inventory adjustments (i.e. inventory counts). """
        self = self._set_view_context()
        self._quant_tasks()

        ctx = dict(self.env.context or {})
        ctx['no_at_date'] = True
        if self.user_has_groups('stock.group_stock_user') and not self.user_has_groups('stock.group_stock_manager'):
            ctx['search_default_my_count'] = True
        action = {
            'name': _('Inventory Adjustments'),
            'view_mode': 'list',
            'view_id': self.env.ref('autonsi_stock_adjustment.view_check_order_apply_quant').id,
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('location_id.usage', 'in', ['internal', 'transit'])],
            'help': """
                    <p class="o_view_nocontent_smiling_face">
                        {}
                    </p><p>
                        {} <span class="fa fa-long-arrow-right"/> {}</p>
                    """.format(_('Your stock is currently empty'),
                               _('Press the CREATE button to define quantity for each product in your stock or import them from a spreadsheet throughout Favorites'),
                               _('Import')),
        }
        return action
