from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CheckOrderDetail(models.Model):
    _name = "stock.check.order.detail"
    check_order_id = fields.Many2one("stock.check.order")
    bin_id = fields.Many2one("stock.location")
    product_id = fields.Many2one("product.product")
    lot_id = fields.Many2one("stock.production.lot")
    available_qty = fields.Float("Available Quantity")
    on_hand_qty = fields.Float("On hand Quantity")
    counted_qty = fields.Float("Counted Quantity", default=lambda self: self.on_hand_qty)
    difference = fields.Float("Difference", compute='compute_difference', store=True)
    quant_id = fields.Many2one('stock.quant')

    @api.depends('counted_qty')
    def compute_difference(self):
        for rec in self:
            rec.difference = rec.counted_qty - rec.on_hand_qty

