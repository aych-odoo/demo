from odoo.http import Controller, request, route


class AwesomeBusController(Controller):
    @route("/bus_demo/change_counter", type="jsonrpc", auth="user")
    def change_counter(self, change_amount):
        request.env["bus_demo.counter"].change_counter(change_amount)

    @route("/bus_demo/get_counter", type="jsonrpc", auth="user")
    def get_counter(self):
        return request.env["bus_demo.counter"].get_or_create_counter().value

    @route("/bus_demo/get_topics", type="jsonrpc", auth="user")
    def get_topics(self):
        return request.env["bus_demo.topic"].get_topics()

    @route("/bus_demo/add_topic", type="jsonrpc", auth="user")
    def add_topic(self, name):
        return request.env["bus_demo.topic"].create({"name": name})

    @route("/bus_demo/send_topic_message", type="jsonrpc", auth="user")
    def send_topic_message(self, topicId, message):
        topic = request.env["bus_demo.topic"].search([("id", "=", topicId)])
        if not topic:
            return
        topic.send_topic_message(message)
