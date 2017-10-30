# -*- coding: utf-8 -*-

from odoo import api, fields, models


class purchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    contract_type = fields.Selection(related="order_id.contract_type", store=True, readonly=True)
    is_signed = fields.Boolean(related="order_id.is_signed", readonly=True)
