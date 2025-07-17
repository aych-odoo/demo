from odoo import api, fields, models
from odoo.tools.misc import (
    limited_field_access_token,
    verify_limited_field_access_token,
)


class BusTopic(models.Model):
    _name = "bus_demo.topic"
    _description = "Topics"
    _inherit = ["bus.listener.mixin"]

    name = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        topics = super().create(vals_list)
        group_id = self.env["res.groups"].search([
            ("id", "in", self.env.ref("base.group_user").ids)
        ])
        for topic in topics:
            group_id._bus_send(
                "bus_demo/add_topic",
                {
                    "name": topic.name,
                    "access_token": topic.get_access_token(),
                    "id": topic.id,
                },
            )
        return topics

    def get_access_token(self):
        self.ensure_one()
        return f"topic:{self.id}:" + limited_field_access_token(
            self, "name", scope="bus_demo.topic"
        )

    def verify_access_token(self, access_token):
        return verify_limited_field_access_token(
            self, "name", access_token, scope="bus_demo.topic"
        )

    def send_topic_message(self, message):
        self.ensure_one()
        self._bus_send(
            "bus_demo/topic_message",
            {"from": self.env.user.name, "message": message, "topic": self.name},
        )

    @api.model
    def get_topics(self):
        topics = self.env["bus_demo.topic"].search([])
        result = []
        for topic in topics:
            result.append({
                "id": topic.id,
                "name": topic.name,
                "access_token": topic.get_access_token(),
            })
        return result
