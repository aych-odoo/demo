import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { GlobalCounter } from "./global_counter/global_counter";
import { Topics } from "./topics/topics";
import { ResetNotifications } from "./reset_notifications/reset_notifications";

export class AwesomeBusClientAction extends Component {
    static components = { GlobalCounter, Topics, ResetNotifications };
    static template = "bus_demo.AwesomeBusClientAction";
}

registry.category("actions").add("action_bus_demo", AwesomeBusClientAction);
