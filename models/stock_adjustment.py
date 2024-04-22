from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from lxml import etree


class StockAdjustmentOrder(models.Model):
    _name = 'stock.adjustment.order'

    # location_id = fields.Many2one("stock.location", "Area", domain=(
    #     [('location_type', 'not in', ['rack', 'bin']), ('check_type', 'ilike', '_stock')]))
    location_id = fields.Many2one("stock.location", "Area")
    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime("End Date")
    check_order_ids = fields.One2many(
        "stock.check.order", "adjustment_order_id")


class StockCheckOrder(models.Model):
    _name = 'stock.check.order'

    location_id = fields.Many2one(
        "stock.location", "Rack", domain=([('location_type', '=', 'rack')]))
    worker_id = fields.Many2many("res.partner")
    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime("End Date")
    adjustment_order_id = fields.Many2one("stock.adjustment.order")

    @api.onchange('adjustment_order_id')
    def onchange_adjustment_order_id(self):
        if self.adjustment_order_id:
            self.location_id = self.adjustment_order_id.location_id
        else:
            self.location_id = False
