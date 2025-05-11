
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo.exceptions import Warning
from datetime import timedelta, datetime, date

STATES = [
            ('draft', "قيد التجهيز"),
            ('sent', "تم الارسال"),
            ('sale', "قيد التوصيل"),
            ('delivered', "تم التسليم"),
            ('returned', "تم الإرجاع"),
            ('done', "مقفله"),
            ('cancel', "تم الالغاء"),
        ]

class SaleOrders(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    sale_delivery_date = fields.Datetime(" تاريخ التوصيل ")
    sale_receipt_date = fields.Datetime(" تاريخ التسليم ")
    sale_return_date = fields.Datetime(" تاريخ الارجاع ")
    is_package = fields.Boolean(tracking=True,string="جملة", copy=False)
    sale_state = fields.Selection(
        selection= [
            ('draft', "قيد التجهيز"),
            ('sale', "قيد التوصيل"),
            ('delivered', "تم التسليم"),
            ('returned', "تم الإرجاع"),
            ('cancel', "تم الالغاء"),],
        string="Sale Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='draft')
    state = fields.Selection(
        selection= STATES,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='draft')

    delivery_address = fields.Char(string='العنوان', required=True)
    mobile_number = fields.Char(copy=False,string='رقم الهاتف', required=True)
    mobile_number2 = fields.Char(copy=False,string='رقم الهاتف 2 ')
    sales_representative_id = fields.Many2one('sale.representative', string='مندوب توصيل')
    source_id = fields.Many2one('utm.source', string='Tag')
    partner_id2 = fields.Many2one('res.partner', string='Customer 2')
    total_qty = fields.Float(string='إجمالى الكميات', compute='_compute_total_qty')
    total_lines = fields.Float(string='عدد اﻻصناف', compute='_compute_total_qty')
    partner_phone = fields.Char(related='partner_id.phone', string="هاتف العميل")

    def action_sale(self):
        for rec in self:
            rec.state = 'sale'
            rec.sale_state = 'sale'

    def action_cancel_sale(self):
        for rec in self:
            rec.sale_state = 'cancel'

    def _action_cancel(self):
        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        inv.button_cancel()
        return self.write({'state': 'cancel','sale_state': 'cancel'})

    # def action_cancel(self):
    #     """ Cancel SO after showing the cancel wizard when needed. (cfr :meth:`_show_cancel_wizard`)
    #
    #     For post-cancel operations, please only override :meth:`_action_cancel`.
    #
    #     note: self.ensure_one() if the wizard is shown.
    #     """
    #     cancel_warning = self._show_cancel_wizard()
    #     if cancel_warning:
    #         self.ensure_one()
    #         template_id = self.env['ir.model.data']._xmlid_to_res_id(
    #             'sale.mail_template_sale_cancellation', raise_if_not_found=False
    #         )
    #         lang = self.env.context.get('lang')
    #         template = self.env['mail.template'].browse(template_id)
    #         if template.lang:
    #             lang = template._render_lang(self.ids)[self.id]
    #         ctx = {
    #             'default_use_template': bool(template_id),
    #             'default_template_id': template_id,
    #             'default_order_id': self.id,
    #             'mark_so_as_canceled': True,
    #             'default_email_layout_xmlid': "mail.mail_notification_layout_with_responsible_signature",
    #             'model_description': self.with_context(lang=lang).type_name,
    #         }
    #         return {
    #             'name': _('Cancel %s', self.type_name),
    #             'view_mode': 'form',
    #             'res_model': 'sale.order.cancel',
    #             'view_id': self.env.ref('sale.sale_order_cancel_view_form').id,
    #             'type': 'ir.actions.act_window',
    #             'context': ctx,
    #             'target': 'new'
    #         }
    #     else:
    #         return self._action_cancel()
    #         self.sale_state = 'cancel'

    def action_return(self):
        for rec in self:
            rec.sale_state = 'returned'

    def action_delivered(self):
        for rec in self:
            # rec.sale_delivery_date = datetime.today()
            rec.sale_state = 'delivered'

    @api.onchange('mobile_number')
    def onchange_mobile_number(self):
        if self.mobile_number:
            sales = self.env['sale.order'].sudo().search_count([('mobile_number', '=', self.mobile_number)])
            print('Sales 1 ===>  ', sales)
            if sales > 1:
                return {'warning': {
                                       'title': _('تنبيه'),
                                       'message': _('رقم الهاتف تم ادخاله سابقا')
                                   }
                        }

    @api.onchange('mobile_number2')
    def onchange_mobile_number2(self):
        if self.mobile_number2:
            sales = self.env['sale.order'].sudo().search_count([('mobile_number2', '=', self.mobile_number2)])
            print('Sales 2 ===>  ', sales)
            if sales > 1:
                return {'warning': {
                                       'title': _('تنبيه'),
                                       'message': _('رقم الهاتف 2 تم ادخاله سابقا')
                                   }
                        }

    @ api.depends('order_line')
    def _compute_total_qty(self):
        for rec in self:
            total_qty = total_lines = 0.0
            if rec.order_line:
                total_qty = sum(rec.order_line.mapped('product_uom_qty'))
                total_lines = len(rec.order_line)
            rec.total_qty = total_qty
            rec.total_lines = total_lines

    @api.constrains('mobile_number')
    def _mobile_number_constraints(self):
        if self.mobile_number and len(self.mobile_number) != 10:
            raise ValidationError(_('Mobile Number Must be just 10 Digits'))

    @api.constrains('mobile_number2')
    def _mobile_number2_constraints(self):
        if self.mobile_number2 and len(self.mobile_number2) != 10:
            raise ValidationError(_('Mobile Number 2 Must be just 10 Digits'))


    def _prepare_invoice(self):
        res = super(SaleOrders, self)._prepare_invoice()
        res.update({
            'delivery_address': self.delivery_address,
            'mobile_number': self.mobile_number,
            'mobile_number2': self.mobile_number2,
            'sales_representative_id': self.sales_representative_id.id,
        })
        self.sale_state = 'delivered'
        return res

    def action_return_delivery(self):
        # return_picking_vals = {'picking_id': self.picking_ids.ids[0], }
        # return_picking_obj = self.env['stock.return.picking'].with_context(picking_id=self.picking_ids.ids[0],
        #                                                                    active_model='stock.picking', ).create(
        #     return_picking_vals)

        # return_picking_obj._onchange_picking_id()
        # returned_pickings_vals = return_picking_obj.create_returns()
        # returned_pickings = self.env['stock.picking'].browse(returned_pickings_vals['res_id'])
        # returned_pickings.action_set_quantities_to_reservation()
        # returned_pickings.action_assign()
        # returned_pickings._action_done()

        # for picking in self.picking_ids:
        #     picking.action_cancel()
        # self.state = 'returned'

        return_picking_vals = {'picking_id': self.picking_ids.ids[0], }
        return_picking_obj = self.env['stock.return.picking'].with_context(picking_id=self.picking_ids.ids[0],
                                                                           active_model='stock.picking', ).create(
            return_picking_vals)
        return_picking_obj._onchange_picking_id()
        returned_pickings_vals = return_picking_obj.create_returns()
        returned_pickings = self.env['stock.picking'].browse(returned_pickings_vals['res_id'])
        returned_pickings.action_set_quantities_to_reservation()
        returned_pickings.action_assign()
        returned_pickings._action_done()
        self.sale_return_date = datetime.today()
        print("Status ==>  ", self.state)
        self.write({"sale_state": "returned"})


    def action_done_all(self):
        # self.action_delivery()
        for rec in self:
            order_invoice = rec._create_invoices()
            print(' =======>  ', order_invoice)
            order_invoice.action_post()
            default_payment_journal = rec.company_id.so_payment_journal_id
            payment_register_vals = {'payment_date': order_invoice.date,
                                     'journal_id': default_payment_journal.id, }
            payment_register_obj = self.env['account.payment.register'].with_context(active_ids=order_invoice.ids,
                                                                                     active_model='account.move').create(
                payment_register_vals)
            payment_register_obj._create_payments()
            rec.sale_receipt_date = datetime.today()
            rec.sale_state =  'delivered'

    def action_quick_confirm(self):
        self.action_confirm()
        self.action_delivery()
        self.sale_state = 'sale'
        self.sale_delivery_date = datetime.today()

    def action_delivery(self):
        for rec in self:
            for line in rec.order_line:
                if line.product_id.detailed_type == 'product' and line.product_uom_qty > line.product_id.qty_available:
                    raise ValidationError(_('Please Check This Product Qty \'%s\'.') % (line.product_id.name,))
            # rec.action_confirm()
            default_location_dest = self.company_id.so_delivery_location_id
            rec.picking_ids.location_dest_id = default_location_dest
            for picking in rec.picking_ids:
                for line in picking.move_ids_without_package:
                    line.quantity_done = line.product_uom_qty
                    line.forecast_availability = line.product_uom_qty
                picking.action_set_quantities_to_reservation()
                picking.action_assign()
                picking._action_done()

    def action_package(self):
        for rec in self:
            rec.action_confirm()
            rec.is_package = True
            self.sale_state = 'sale'

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_unit = fields.Float(
        string="سعر المنتج",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)

    product_available_qty = fields.Float(
        string="الكميه المتاحه",
        compute='_compute_product_available_qty', )
    can_edit_price = fields.Boolean()

    @api.onchange('can_edit_price')
    def _compute_can_edit_price(self):
        for rec in self:
            rec.can_edit_price = self.env.user.has_group('db_sales_custom.group_access_unit_price')

    @api.depends('product_id')
    def _compute_product_available_qty(self):
        for rec in self:
            product_available_qty = 0.0
            if rec.product_id:
                product_available_qty = sum(self.env['stock.quant'].search([('warehouse_id', '=', rec.warehouse_id.id),
                                                                            ('product_id', '=',
                                                                             rec.product_id.id), ]).mapped(
                    'available_quantity'))
            rec.product_available_qty = product_available_qty
