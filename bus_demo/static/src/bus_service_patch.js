import { patch } from "@web/core/utils/patch";
import { busService } from "@bus/services/bus_service";

patch(busService, {
    // Log all the notifications coming from server
    _onMessage(env, id, type, payload) {
        console.log(type, payload);
    },
});
