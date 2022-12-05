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
    akaneModel,
    eliotModel,
    emilyModel,
    joeModel,
    users
} from './data/data';

// Storage needs to generate id for messages and groups
const messageIdGenerator = () => {

};

const groupIdGenerator = () => {

};

// Create serviceFactory
const serviceFactory = (storage, updateState) => {
    return ChatService(storage, updateState);
};

const akaneStorage = new BasicStorage({groupIdGenerator, messageIdGenerator});
const eliotStorage = new BasicStorage({groupIdGenerator, messageIdGenerator});
const emilyStorage = new BasicStorage({groupIdGenerator, messageIdGenerator});
const joeStorage = new BasicStorage({groupIdGenerator, messageIdGenerator});
const chatStorage = new BasicStorage({groupIdGenerator, messageIdGenerator});

const akane = new User({
    id: akaneModel.name,
    presence: new Presence({
        status: UserStatus.Available,
        description: ''
    }),
    firstName: '',
    lastName: '',
    username: akaneModel.name,
    email: '',
    avatar: akaneModel.avatar,
    bio: ''
});

const emily = new User({
    id: emilyModel.name,
    presence: new Presence({
        status: UserStatus.Available,
        description: ''
    }),
    firstName: '',
    lastName: '',
    username: emilyModel.name,
    email: '',
    avatar: emilyModel.avatar,
    bio: ''
});

const eliot = new User({
    id: eliotModel.name,
    presence: new Presence({
        status: UserStatus.Available,
        description: ''
    }),
    firstName: '',
    lastName: '',
    username: eliotModel.name,
    email: '',
    avatar: eliotModel.avatar,
    bio: ''
});

const joe = new User({
    id: joeModel.name,
    presence: new Presence({
        status: UserStatus.Available,
        description: ''
    }),
    firstName: '',
    lastName: '',
    username: joeModel.name,
    email: '',
    avatar: joeModel.avatar,
    bio: ''
});

const chats = [
    {
        name: 'Akane',
        storage: akaneStorage
    },
    {
        name: 'Eliot',
        storage: eliotStorage
    },
    {
        name: 'Emily',
        storage: emilyStorage
    },
    {
        name: 'Joe',
        storage: joeStorage
    }
];

function createConversation(id: ConversationId,
                            name: string): Conversation {
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
        if (u.name !== c.name) {
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
                if (chat) {
                    const hisConversation = chat.storage.getState().conversations.find(cv => typeof cv.participants.find(p => p.id === c.name) !== 'undefined');
                    if (!hisConversation) {
                        chat.storage.addConversation(createConversation(conversationId, c.name));
                    }
                }
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
            <Chat user={akane}></Chat>
        </ChatProvider>


        <ChatProvider serviceFactory={serviceFactory} storage={eliotStorage} config={{
            typingThrottleTime: 250,
            typingDebounceTime: 900,
            debounceTyping: true,
            autoDraft: AutoDraft.Save | AutoDraft.Restore
        }}>
            <Chat user={eliot}/>
        </ChatProvider>


        <ChatProvider serviceFactory={serviceFactory} storage={emilyStorage} config={{
            typingThrottleTime: 250,
            typingDebounceTime: 900,
            debounceTyping: true,
            autoDraft: AutoDraft.Save | AutoDraft.Restore
        }}>
            <Chat user={emily}/>
        </ChatProvider>
        <ChatProvider serviceFactory={serviceFactory} storage={joeStorage} config={{
            typingThrottleTime: 250,
            typingDebounceTime: 900,
            debounceTyping: true,
            autoDraft: AutoDraft.Save | AutoDraft.Restore
        }}>
            <Chat user={joe}/>
        </ChatProvider>
    </div>);
}

export default App;