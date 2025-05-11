from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    analytic_distribution = fields.Json()
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )
