
from odoo import models, fields, _, api
from odoo.exceptions import UserError,ValidationError

class Partner(models.Model):
    _inherit = 'res.partner'


class Country(models.Model):
    _inherit = 'res.country'

    zip_required = fields.Boolean(compute='get_zip_required')

    def get_zip_required(self):
        for rec in self:
            rec.zip_required = False





