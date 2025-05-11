from odoo import api, fields, models

# res.partner
class RES_PARTNER(models.Model):
    _inherit = 'res.partner'
    _description = 'RES_PARTNER'

    related_user_id = fields.Many2one(
        'res.users',
        string='Related User',
        help="User related to this partner",
        compute='_compute_user',
        store=False,
    )

    related_user_company_ids = fields.Many2many(
        'res.users',
        string='Related User Companies',
        help="Companies related to this user",
        compute='_compute_user',
        store=False,
    )

    def _compute_user(self):
        for partner in self:
            user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1)
            partner.related_user_id = user.id if user else False
            if user:
                partner.related_user_company_ids = user.company_ids.ids
            else:
                partner.related_user_company_ids = False