import { Component, onWillDestroy, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class GlobalCounter extends Component {
    static template = "bus_demo.GlobalCounter";

    setup() {
        this.state = useState({ value: 0 });
        this.busService = useService("bus_service");

        onWillStart(async () => {
            this.busService.subscribe("bus_demo/update_counter", ({ new_value }) => {
                this.state.value = new_value;
            });

            try {
                const counter = await rpc("/bus_demo/get_counter");
                this.state.value = counter;
            } catch {}
        });
    }

    async changeCounter(changeBy) {
        await rpc("/bus_demo/change_counter", {
            change_amount: changeBy,
        });
    }
}
