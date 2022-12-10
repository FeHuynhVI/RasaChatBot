import React from 'react';
import Toolbar from './components/Toolbar';
import {StyleChat as Chat} from './components/Chat';
import './App.css';

import ChatService from './components/ChatService';

import {
    BasicStorage,
    ChatMessage,
    ChatProvider,
    Conversation,
    ConversationId,
    ConversationRole,
    IStorage,
    MessageContentType,
    Participant,
    Presence,
    TypingUsersList,
    UpdateState,
    User,
    UserStatus,
    AutoDraft
} from '@chatscope/use-chat';

import {
    ncovidModel,
    users
} from './data/data';

// Storage needs to generate id for messages and groups
const messageIdGenerator = () => {

};

const groupIdGenerator = () => {

};

// Create serviceFactory
const serviceFactory = (storage, updateState) => {
    return new ChatService(storage, updateState);
};

const ncovidStorage = new BasicStorage({groupIdGenerator, messageIdGenerator});
const chatStorage = new BasicStorage({groupIdGenerator, messageIdGenerator});

const ncovid = new User({
    id: ncovidModel.name,
    presence: new Presence({
        status: UserStatus.Available,
        description: ''
    }),
    firstName: '',
    lastName: '',
    username: ncovidModel.name,
    email: '',
    avatar: ncovidModel.avatar,
    bio: ''
});

const chats = [
    {
        name: 'ncovid',
        storage: ncovidStorage
    },
];

function createConversation(id, name) {
    return new Conversation({
        id,
        participants: [new Participant({
            id: name,
            role: new ConversationRole([])
        })],
        unreadCounter: 0,
        typingUsers: new TypingUsersList({items: []}),
        draft: ''
    });
}

// Add users and conversations to the states
chats.forEach(c => {
    users.forEach(u => {
        if (u.name === c.name) {
            return;
        }

        c.storage.addUser(new User({
            id: u.name,
            presence: new Presence({
                status: UserStatus.Available,
                description: ''
            }),
            firstName: '',
            lastName: '',
            username: u.name,
            email: '',
            avatar: u.avatar,
            bio: ''
        }));

        const conversationId = '321321321';

        const myConversation = c.storage.getState().conversations.find(cv => typeof cv.participants.find(p => p.id === u.name) !== 'undefined');
        if (!myConversation) {
            c.storage.addConversation(createConversation(conversationId, u.name));

            const chat = chats.find(chat => chat.name === u.name);
            if (!chat) {
                return;
            }

            const hisConversation = chat.storage.getState().conversations.find(cv => typeof cv.participants.find(p => p.id === c.name) !== 'undefined');
            if (!hisConversation) {
                chat.storage.addConversation(createConversation(conversationId, c.name));
            }
        }
    });

});


function App() {
    return (<div className="App">
        <Toolbar></Toolbar>

        <ChatProvider serviceFactory={serviceFactory} storage={chatStorage} config={{
            typingThrottleTime: 250,
            typingDebounceTime: 900,
            debounceTyping: true,
            autoDraft: AutoDraft.Save | AutoDraft.Restore
        }}>
            <Chat user={ncovid}></Chat>
        </ChatProvider>
    </div>);
}

export default App;