from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_uom_id = fields.Many2one(
        'uom.uom',
        string="Purchase UoM",
        related='product_id.conversion_uom_id',
        store=True,
        readonly=True
    )

    conversion_qty = fields.Float(
        string="Qty in Purchase UoM",
        compute="_compute_conversion_qty",
        store=True,
        digits=(16, 4)
    )

    price_per_conversion = fields.Float(
        string="Price per Purchase Unit",
        digits=(16, 2)
    )

    @api.depends('product_qty', 'product_id')
    def _compute_conversion_qty(self):
        for line in self:
            ratio = line.product_id.conversion_ratio or 1
            line.conversion_qty = line.product_qty * ratio

    @api.onchange('product_id')
    def _onchange_product_id_set_conversion(self):
        for line in self:
            if line.product_id:
                # ALWAYS pick from conversion_uom_id
                line.purchase_uom_id = line.product_id.conversion_uom_id
                
                # fallback logic (only for safety, invisible to user)
                if not line.purchase_uom_id:
                    line.purchase_uom_id = line.product_id.uom_id

                line.price_per_conversion = line.product_id.price_per_conversion or 0.0

    @api.onchange('price_per_conversion')
    def _onchange_price_conversion(self):
        for line in self:
            ratio = line.product_id.conversion_ratio or 1
            line.price_unit = line.price_per_conversion * ratio