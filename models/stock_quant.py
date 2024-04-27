from odoo import _, api, fields, models, exceptions


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    adjustment_reason = fields.Char("Adjustment Reason")