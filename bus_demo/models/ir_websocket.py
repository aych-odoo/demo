from odoo import models
import re

TOPIC_CHANNEL_PATTERN = r"^topic:\d+:[a-f0-9]+o0x[a-f0-9]+$"


class IrWebsocket(models.AbstractModel):
    """Override to handle discuss specific features (channel in particular)."""

    _inherit = "ir.websocket"

    def _build_bus_channel_list(self, channels):
        """
        Build and return the final list of bus channels a user should be subscribed to.

        This method is triggered when the frontend establishes a WebSocket connection and
        emits a "subscribe" event. Regardless of whether the client specifies any channels,
        this method ensures that authorized users are automatically subscribed to relevant
        backend-defined channels.

        Main behavior:
        - If the user is internal (e.g., admin or employee), they may be subscribed to extra channels:
            - Any channel strings matching the `topic:<id>:<token>` format are validated and converted
            into actual `bus_demo.topic` records after token verification.
            - All internal users are automatically subscribed to a global counter channel.
        - This logic allows the backend to enforce secure, default subscriptions as needed.

        ⚠️ Note:
        Proper token verification is essential to avoid unauthorized channel access.

        Args:
            channels (list): A list of channels sent from the frontend. These may be:
                            - Record objects (already resolved)
                            - String-based identifiers like 'topic:1:<token>'

        Returns:
            list: The final list of validated channel subscriptions.
        """
        if self.env.user._is_internal():
            # Handle string-based topic subscriptions
            for channel in list(channels):  # Copy to allow safe modification
                if re.match(TOPIC_CHANNEL_PATTERN, channel):
                    split_channel = channel.split(":")
                    try:
                        topic_id = int(split_channel[1])
                        token = split_channel[2]
                    except (IndexError, ValueError):
                        continue  # Skip malformed strings

                    # Verify token and convert to topic record
                    topic = self.env["bus_demo.topic"].browse(topic_id)
                    if topic and topic.verify_access_token(token):
                        channels.append(topic)
                        channels.remove(channel)

            # Add the internal user to a shared counter channel
            counter = self.env["bus_demo.counter"].get_or_create_counter()
            channels.append(counter)

        return super()._build_bus_channel_list(channels)
