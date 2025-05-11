from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_company_domain(self):
        return [('id', 'in', self.env.company.ids)]

    company_id = fields.Many2one('res.company', domain=lambda self: self.get_company_domain())