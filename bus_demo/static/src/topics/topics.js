import { Component, onWillDestroy, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

export class Topic extends Component {
    static template = "bus_demo.Topic";
    static props = ["topic", "subscribe", "unsubscribe"];

    setup() {
        this.state = useState({ message: "" });

        onWillDestroy(() => {
            this.unsubscribe();
        });
    }

    async onSend() {
        if (!this.props.topic.isSubscribed) return;
        await rpc("/bus_demo/send_topic_message", {
            topicId: this.props.topic.id,
            message: this.state.message,
        });
        this.state.message = "";
    }

    subscribe() {
        this.props.subscribe(this.props.topic.id);
    }

    unsubscribe() {
        this.props.unsubscribe(this.props.topic.id);
    }

    /** @param {KeyboardEvent} ev */
    onKeydown(ev) {
        if (ev.key == "Enter") {
            this.onSend();
        }
    }
}

export class Topics extends Component {
    static components = { Topic };
    static template = "bus_demo.Topics";

    setup() {
        this.newTopicState = useState({ addTopic: "" });
        this.topics = useState({ value: [] });
        this.notificationService = useService("notification");
        this.busService = useService("bus_service");
        onWillStart(async () => {
            this.busService.subscribe("bus_demo/add_topic", (newTopic) => {
                this.topics.value.push({ ...newTopic, isSubscribed: false });
            });

            this.busService.subscribe("bus_demo/topic_message", ({ message, from, topic }) => {
                this.notificationService.add(`${topic}: ${from} sent ${message}`, {
                    type: "info",
                    sticky: true,
                });
            });

            try {
                const topics = await rpc("/bus_demo/get_topics");
                this.topics.value = topics.map((e) => ({ ...e, isSubscribed: false }));
            } catch {}
        });
    }

    async onAddTopic() {
        if (!this.newTopicState.addTopic) return;
        await rpc("/bus_demo/add_topic", { name: this.newTopicState.addTopic });
        this.newTopicState.addTopic = "";
    }

    subscribe(id) {
        const topic = this.topics.value.find((e) => e.id === id);
        this.busService.addChannel(topic.access_token);
        topic.isSubscribed = true;
    }

    unsubscribe(id) {
        const topic = this.topics.value.find((e) => e.id === id);
        this.busService.deleteChannel(topic.access_token);
        topic.isSubscribed = false;
    }
}
