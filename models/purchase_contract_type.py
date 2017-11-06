# -*- coding: utf-8 -*-

from odoo import api, fields, models
import amount_to_text_es_MX


class PurchaseContractType(models.Model):
    _inherit = 'purchase.order'

    is_signed = fields.Boolean()

    auxiliary_contract = fields.Many2one('purchase.order', readonly=True)

    contract_type = fields.Selection([
        ('axc', 'AxC'),
        ('pf', 'Precio Fijo'),
        ('pm', 'Precio Minimo'),
        ('pd', 'Precio Despues'),
        ('pb', 'Precio Base'),
	('sv', 'Servicios'),
        ('surplus', 'Excedente'),
        ('na', 'No aplica'),
    ], default='na', required=True)

    tons = fields.Float(compute='_compute_tons', store=False)
    tons_text = fields.Text(compute='_compute_tons_text', store=False)
    product = fields.Many2one('product.product', compute='_compute_product', store=False)

    tons_reception = fields.Float(compute='_compute_tons_reception', string="Toneladas Disponibles", store=False)

    @api.one
    def _compute_tons_reception(self):
        available = 0
        for line in self.env['truck.reception'].search([('contract_id', '=', self.name), ('state', '=', 'done')]):
            if line.stock_picking_id:
                available = available + (line.clean_kilos / 1000)
        for line in self.env['split.receptions'].search([('contract_id', '=', self.name), ('state', '=', 'close')]):
            available = available - line.tons_transfer
        for line in self.env['split.receptions'].search([('contract_dest_id', '=', self.name), ('state', '=', 'close')]):
            available = available + line.tons_transfer
        self.tons_reception = available

    @api.one
    @api.depends('order_line')
    def _compute_tons(self):
        self.tons = 0
        for line in self.order_line:
            self.tons = line.product_qty
            break

    @api.one
    @api.depends('tons')
    def _compute_tons_text(self):
        self.tons_text = amount_to_text_es_MX.get_amount_to_text(self, self.tons, 'es_MX', 'MX')

    @api.one
    @api.depends('order_line')
    def _compute_product(self):
        product = False
        for line in self.order_line:
            product = line.product_id
            break
        self.product = product
