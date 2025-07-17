import { Component, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ResetNotifications extends Component {
    static template = xml`
    <div class="p-4 border bg-light rounded">
        <button class="btn btn-primary mb-3" t-on-click="resetNotifications">
            <i class="fa fa-refresh mr-2"></i> Reset Notifications
        </button>
        <p class="mb-2">
            Clicking the button above will update the last seen notification ID and reload the page.
            This triggers a fresh fetch of all past notifications from the server.
        </p>
        <p class="mb-2">
            You can observe the reloaded notifications in the browser console. This action also helps demonstrate 
            the <strong>error handling</strong> and <strong>reliability</strong> of the bus service.
        </p>
        <p class="mb-0 text-muted">
            Tip: Try subscribing/unsubscribing to topics or sending messages before resetting 
            to better see how these features interact.
        </p>
    </div>`;

    setup() {
        this.multiTabService = useService("multi_tab");
    }

    resetNotifications() {
        this.multiTabService.setSharedValue("last_notification_id", 1);
        window.location.reload();
    }
}
