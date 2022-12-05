import {useState, useEffect} from 'react';
import io from 'socket.io-client';

import {UserTypingEvent, MessageDirection} from '@chatscope/use-chat';

// https://socket.io/get-started/private-messaging-part-1/
// https://socket.io/docs/v3/rooms/
const ChatService = (storage, update, url, path, customData) => {
    this.eventHandlers = {
        onMessage: () => {
        },
        onConnectionStateChanged: () => {
        },
        onUserConnected: () => {
        },
        onUserDisconnected: () => {
        },
        onUserPresenceChanged: () => {
        },
        onUserTyping: () => {
        },
    };

    this.url = url;
    this.path = path;
    this.customData = customData;
    this.storage = storage;
    this.updateState = update;

    this.socket = io(this.url, {path: this.path});
    this.socket.on('connect', () => {
        console.log(`connect:${this.socket.id}`);
        this.socket.customData = this.customData;
    });

    const [isConnected, setIsConnected] = useState(this.socket.connected);
    const [lastPong, setLastPong] = useState(null);

    useEffect(() => {
        this.socket.on('chat/session_connect', () => {
            setIsConnected(true);
        });

        this.socket.on('chat/session_disconnect', (reason) => {
            console.log(reason);
            setIsConnected(false);
        });

        this.socket.on('chat/session_connect_error', (error) => {
            console.error(error);
            setIsConnected(false);
        });

        this.socket.on('chat/session_pong', () => {
            setLastPong(new Date().toISOString());
        });

        return () => {
            this.socket.off('chat/session_connect');
            this.socket.off('chat/session_disconnect');
            this.socket.off('chat/session_pong');
        };
    }, []);

    // We set a function on session_confirm here so as to avoid any race condition
    // this will be called first and will set those parameters for everyone to use.
    this.socket.on('chat/session_confirm', (sessionObject) => {
        this.sessionConfirmed = true;
        this.sessionId = (sessionObject && sessionObject.session_id) ? sessionObject.session_id : sessionObject;
    });

    this.socket.on('chat/message_receive', function (data) {
        const {message, conversationId} = data;
        // We send messages using a CustomEvent dispatched to the window object.
        // They are received in the callback assigned in the constructor.
        // In a real application, instead of dispatching the event here,
        // you will implement sending messages to your chat server.
        const messageEvent = new CustomEvent('chat-protocol', {
            detail: {
                type: 'message',
                message,
                conversationId,
                sender: this,
            },
        });

        window.dispatchEvent(messageEvent);
    });

    // For communication we use CustomEvent dispatched to the window object.
    // It allows you to simulate sending and receiving data from the server.
    // In a real application, instead of adding a listener to the window,
    // you will implement here receiving data from your chat server.
    window.addEventListener('chat-protocol', (evt) => {
        const event = evt;
        const {detail: {conversationId, type,}, detail,} = event;
        switch (type) {
            case  'message':
                const message = detail.message;
                message.direction = MessageDirection.Incoming;
                if (this.eventHandlers.onMessage && detail.sender !== this) {
                    // Running the onMessage callback registered by ChatProvider will cause:
                    // 1. Add a message to the conversation to which the message was sent
                    // 2. If a conversation with the given id exists and is not active,
                    //    its unreadCounter will be incremented
                    // 3. Remove information about the sender who is writing from the conversation
                    // 4. Re-render
                    //
                    // Note!
                    // If a conversation with such id does not exist,
                    // the message will be added, but the conversation object will not be created.
                    // You have to take care of such a case yourself.
                    // You can check here if there is already a conversation in storage.
                    // If it is not there, you can create it before calling onMessage.
                    // After adding a conversation to the list, you don't need to manually run updateState
                    // because ChatProvider in onMessage will do it.
                    this.eventHandlers.onMessage(new MessageEvent({
                        message,
                        conversationId
                    }));
                }
                break;
            case 'typing':
                const {
                    userId,
                    isTyping,
                    conversationId,
                    content,
                    sender
                } = detail;

                if (this.eventHandlers.onUserTyping && sender !== this) {
                    // Running the onUserTyping callback registered by ChatProvider will cause:
                    // 1. Add the user to the list of users who are typing in the conversation
                    // 2. Debounce
                    // 3. Re-render
                    this.eventHandlers.onUserTyping(new UserTypingEvent({
                        userId,
                        isTyping,
                        conversationId,
                        content,
                    }));
                }
                break;
        }
    });

    const sendPing = () => {
        this.socket.emit('chat/session_ping');
    };

    const isInitialized = () => {
        return this.socket !== null && this.socket.connected;
    };

    const close = () => {
        if (this.socket) {
            this.socket.close();
        }
    };

    const emit = (message, data) => {
        if (this.socket) {
            this.socket.emit(message, data);
        }
    };

    const sendMessage = ({message, conversationId}) => {
        this.emit('chat/send_message', {
            message,
            conversationId,
        });
    };

    const sendTyping = ({isTyping, content, conversationId, userId,}) => {
        // We send the "typing" signalization using a CustomEvent dispatched to the window object.
        // It is received in the callback assigned in the constructor
        // In a real application, instead of dispatching the event here,
        // you will implement sending signalization to your chat server.
        const typingEvent = new CustomEvent('chat-protocol', {
            detail: {
                type: 'typing',
                isTyping,
                content,
                conversationId,
                userId,
                sender: this,
            },
        });
        window.dispatchEvent(typingEvent);
    };

    // The ChatProvider registers callbacks with the service.
    // These callbacks are necessary to notify the provider of the changes.
    // For , when your service receives a message, you need to run an onMessage callback,
    // because the provider must know that the new message arrived.
    // Here you need to implement callback registration in your service.
    // You can do it in any way you like. It's important that you will have access to it elsewhere in the service.
    const on = (evtType, evtHandler) => {
        const key = `on${evtType.charAt(0).toUpperCase()}${evtType.substring(1)}`;
        if (key in this.eventHandlers) {
            this.eventHandlers[key] = evtHandler;
        }
        // this.socket.on(event, callback);
    };

    // The ChatProvider can unregister the callback.
    // In this case remove it from your service to keep it clean.
    const off = (evtType, eventHandler) => {
        const key = `on${evtType.charAt(0).toUpperCase()}${evtType.substring(1)}`;
        if (key in this.eventHandlers) {
            this.eventHandlers[key] = () => {
            };
        }
    };
};

export default ChatService;