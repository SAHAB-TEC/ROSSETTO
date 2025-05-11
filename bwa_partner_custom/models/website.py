
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

from odoo.http import request
from odoo.osv import expression
from odoo.addons.http_routing.models.ir_http import url_for

class Website(models.Model):
    _inherit = 'website'





    # def _prepare_sale_order_values(self, partner_sudo):
    #     self.ensure_one()
    #     addr = partner_sudo.address_get(['delivery'])
    #     if not request.website.is_public_user():
    #         # FIXME VFE why not use last_website_so_id field ?
    #         last_sale_order = self.env['sale.order'].sudo().search(
    #             [('partner_id', '=', partner_sudo.id)],
    #             limit=1,
    #             order="date_order desc, id desc",
    #         )
    #         if last_sale_order and last_sale_order.partner_shipping_id.active:  # first = me
    #             addr['delivery'] = last_sale_order.partner_shipping_id.id
    #
    #     affiliate_id = request.session.get('affiliate_id')
    #     salesperson_user_sudo = self.env['res.users'].sudo().browse(affiliate_id).exists()
    #     if not salesperson_user_sudo:
    #         salesperson_user_sudo = self.salesperson_id or partner_sudo.parent_id.user_id or partner_sudo.user_id
    #
    #     pricelist_id = self._get_current_pricelist_id(partner_sudo)
    #     fiscal_position_id = self._get_current_fiscal_position_id(partner_sudo)
    #     print(' partner_sudo =======>  ', partner_sudo.name)
    #     print(' partner_sudo =======>  ', partner_sudo)
    #     print(' addr =======>  ', addr)
    #     values = {
    #         'company_id': self.company_id.id,
    #         'fiscal_position_id': fiscal_position_id,
    #         'partner_id': partner_sudo.id,
    #         'partner_id2': addr['delivery'],
    #         'delivery_address': 'partner_sudo.street',
    #         'partner_invoice_id': partner_sudo.id,
    #         'partner_shipping_id': addr['delivery'],
    #         'pricelist_id': pricelist_id,
    #         'payment_term_id': self.sale_get_payment_term(partner_sudo),
    #         'team_id': self.salesteam_id.id or partner_sudo.parent_id.team_id.id or partner_sudo.team_id.id,
    #         'user_id': salesperson_user_sudo.id,
    #         'website_id': self.id,
    #     }
    #
    #     return values
