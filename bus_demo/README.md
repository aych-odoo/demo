# Overview of the Bus Service Architecture

The bus service is a real-time notification system that enables communication between a server (e.g., Python-based backend like Odoo) and clients via WebSockets. It uses a SharedWorker in the browser for efficient handling of connections and messages. Key features include channel subscriptions, message broadcasting, and hooks for database commits.

## Key Components and Methods

Here are the primary files and methods involved:

- **bus_service.js**: `startWorker()`, `initializeConnection()`
- **websocket_worker.js**: `_onClientMessage()`, `_sendToServer()`, `_onWebsocketMessage()`, `sendToClient()`, `channelsByClient` (a mapping of clients to their subscribed channels)
- **ir_websocket.py**: `_build_bus_channels_list()` (builds the list of channels a WebSocket can subscribe to)
- **bus.py**: `ImDispatch` (handles dispatching notifications), `_channels_to_ws` (maps channels to WebSockets), `_sendone()` (sends a single message), `_ensure_hooks()` (sets up commit hooks)
- **bus_listener_mixin.py**: `_bus_send()` (sends notifications), `_bus_channel()` (defines channels for models like `res_groups`, `res_partner`, `res_users`)
- **bus_service** (general): `subscribe()` (subscribes to channels), `addChannel()` (adds channels dynamically)


## End-to-End Flow

The bus service facilitates real-time notifications from server to client. Here's the step-by-step flow:

1. **Initialization**:
    - The `bus_service` is loaded.
    - It calls the worker bundle to load a SharedWorker from assets.
    - The worker starts listening for messages from the client via `_onClientMessage()`.
2. **Connection Setup**:
    - `bus_service` calls `initializeWorkerConnection()`.
    - It sends an `"initialize_connection"` message to the worker with relevant data.
    - The worker's `initializeConnection()` handles logic like checking if a connection exists, closing it if the user is logged out, etc.
3. **Starting the Worker**:
    - `bus_service` sends a `"start"` message to the worker.
    - The worker calls its `_start()` method:
        - Removes any existing event listeners.
        - Creates a new WebSocket and connects to the server.
4. **Handshake and Subscription**:
    - The handshake begins.
    - The server calls `_build_bus_channels_list()` to determine eligible channels.
    - The WebSocket subscribes to these channels.
5. **Ongoing Operations**:
    - Channels can be added dynamically (see "Channels and Subscriptions" below).
    - Messages are dispatched from server to clients via WebSockets.
    - The frontend handles incoming notifications.

## Channels and Subscriptions

Channels (or "rooms") are the core mechanism for routing notifications. They are tuples like `(db_name, model_name, record_id, optional_string)`.

- **Default Channels**: Automatically added based on context (e.g., user groups, partners).
- **Dynamic Channels**: Added at runtime via the frontend's `bus_service.addChannel()` method. The server verifies if the user is authorized to subscribe.
- **Subscription Process**:
    - Once subscribed, the `ImDispatch` updates `_channels_to_ws`, a mapping like `{channel_tuple: [WebSocket instances]}`.
- **Frontend Subscription**:
    - Use `bus_service.subscribe("notification_type", handler)` to listen for specific types (e.g., `"mail.store/insert"`). This triggers handlers when notifications arrive.


## Message Sending Architecture

Messages are sent from models (e.g., via `discuss_channel._bus_send(notification_type: string, message: any)`) and propagated through the system.

- **Channel Determination**:
    - The target channel is defined by `_bus_channel()` in `bus_listener_mixin.py` (inherited by models):
        - `res_users`: Maps to `partner_id`.
        - `res_partner`: Maps to `self`.
        - `res_groups`: Similar logic for group-based channels.
- **Sending a Message**:
    - `_bus_send()` is a wrapper around `bus._sendone()`.
    - `bus._sendone()`:
        - Dumps the message data to JSON.
        - Creates a channel tuple (e.g., `(db_name, model_name, record_id, string)`).
        - Adds the message to a pre-commit hook (via `_ensure_hooks()`).
        - Creates records in the `bus.bus` table during the pre-commit phase.
- **Post-Commit Dispatch**:
    - After database commit, adds channels to a post-commit hook.
    - Calls `pg_notify('imbus', channels_list)` to notify listeners.
    - `ImDispatch` listens to `'imbus'` and gets the channel names.
    - It triggers `trigger_notification_dispatching()` on the WebSocket, adding a dispatch command to a priority queue.
- **Polling and Delivery**:
    - When the command is processed, messages are fetched via `bus.bus._poll()`.
    - `_poll()` retrieves messages for the channels where:
        - Message ID > last known ID, or
        - Timestamp is within the last 50 seconds (to avoid overwhelming with old data).
    - If data volume is high, it's partitioned internally.


## Frontend Handling

- **Receiving Data**:
    - The server sends data to the client via WebSocket (handled by `_onWebsocketMessage()` in the worker).
    - Data arrives as "notification" type; the client doesn't know the original channel, only the notification type.
    - The SharedWorker receives it and forwards to clients:
        - `broadcast()`: Sends to all connected clients.
        - `sendToClient()`: Sends to a specific client (using `channelsByClient` mapping).
- **Processing in bus_service**:
    - `_handleMessage()` listens for incoming data.
    - If it's a notification, triggers `notificationBus`.
    - Listeners (e.g., via `bus_service.subscribe("mail.store/insert", handler)`) react to these events in the UI.


## Sending Data to the Server via WebSocket

While most communication is server-to-client, clients can send data to the server (though it's minimized for efficiency).

- **Client Side**:
    - `bus_service` sends a "send" command to the worker.
    - The worker checks if it needs to forward to the server via `_sendToServer()`.
- **Server Side**:
    - Handled by `_serve_ir_websocket()` in `ir_websocket.py`.
    - Common uses:
        - Subscribing to channels: Send a `"subscribe"` event.
        - Specific features like `mail.presence` (sent via WebSocket).

This architecture ensures efficient, real-time notifications with minimal overhead, leveraging database hooks, WebSockets, and a SharedWorker for scalability.
