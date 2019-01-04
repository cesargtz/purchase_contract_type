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

    tons_reception = fields.Float(compute='_compute_tons_reception', string="Toneladas Entregadas", store=False,  help="Son las toneladas que se recibierón y transfirierón, más menos los traspasos parciales entre contratos, menos las salidas de excedentes transferidas")
    tons_free = fields.Float(compute='_compute_tons_free', string="Toneladas Disponibles", store=False, help="Son las toneladas que tiene el productor para preciar. Suma las toneladas de contrato y las de afuera del contrato.")

    @api.one
    def _compute_tons_reception(self):
        self.tons_reception = self._get_tons_avalible(self.name)

    @api.one
    def _compute_tons_free(self):
        tons_priced = sum(tons.pinup_tons for tons in self.env['pinup.price.purchase'].search(
            [('purchase_order_id', '=', self.name), ('state', '=', 'close')]))
        self.tons_free = self.tons_reception - tons_priced

    @api.multi
    def _get_tons_avalible(self,contract_id,):
        available = 0
        for line in self.env['truck.reception'].search([('contract_id', '=', contract_id), ('state', '=', 'done')]):
            if line.stock_picking_id:
                available = available + (line.clean_kilos / 1000)
        for line in self.env['split.receptions'].search([('contract_id', '=', contract_id), ('state', '=', 'close')]):
            available = available - line.tons_transfer
        for line in self.env['split.receptions'].search([('contract_dest_id', '=', contract_id), ('state', '=', 'close')]):
            available = available + line.tons_transfer
        for line in self.env['return.truck'].search([('contract_id', '=', contract_id), ('state', '=', 'done')]):
            available = available - (line.raw_kilos/1000)
        for line in self.env['bridge.warehouse'].search([('purchase_order', '=', contract_id), ('state','=','done')]):
            available = available + (line.clean_kilos/1000)
        return available

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
