from odoo import models, fields, api


class BusCounter(models.Model):
    _name = "bus_demo.counter"
    _description = "global counter"
    _inherit = ["bus.listener.mixin"]

    value = fields.Integer()
    active = fields.Boolean()

    @api.model
    def change_counter(self, value):
        record = self.env["bus_demo.counter"].search([("active", "=", True)])
        if not record:
            return
        record.value += value
        record._bus_send("bus_demo/update_counter", {"new_value": record.value})

    @api.model
    def get_or_create_counter(self):
        record = self.env["bus_demo.counter"].search([("active", "=", True)])
        if not record:
            record = self.env["bus_demo.counter"].create({"value": 0, "active": True})
        return record
