"use client";

import { createContext, useEffect, useState } from "react";
import { apiURL, LOCAL_STORAGE_DATA_NAME } from "@/utils/VariableName";
import axios from "axios";

axios.defaults.timeout = 0;

export const ChatsContext = createContext(null);

const ChatsContextProvider = ({ children }) => {
    const [chats, setChats] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadChats = async () => {
        setLoading(true);
        const storedChats = localStorage.getItem(LOCAL_STORAGE_DATA_NAME);

        if (storedChats) {
            setChats(JSON.parse(storedChats));
            setLoading(false);
            return;
        }

        setChats([]);
        setLoading(false);
    };

    useEffect(() => {
        loadChats();
    }, []);

    useEffect(() => {
        console.log("Chats updated:", chats, loading);
        if (!loading) {
            saveChats();
        }
    }, [chats]);

    const saveChats = async () => {
        localStorage.setItem(LOCAL_STORAGE_DATA_NAME, JSON.stringify(chats));
    }

    const getChatById = (chatId) => {
        return chats.find((c) => c.id === chatId);
    };

    const newChat = async (idea, language, test) => {
        try {
            const response = await axios.post(`${apiURL}/api/sessions`, { 
                question: idea,
                language,
                test_count: test
            });

            if (!response.data || !response.data.thread_id) {
                return {
                    success: false,
                    message: "Failed to create a new chat."
                }
            }

            const newChat = {
                id: response.data.thread_id,
                title: idea,
                package: false,
                conversations: [{ role: "user", content: idea }, { 
                    role: "assistant", 
                    content: response.data.checkpoint.message + "\r\n" + response.data.checkpoint.draft 
                }],
            };
            setChats((prevChats) => [...prevChats, newChat]);
            return {
                success: true,
                payload: newChat.id
            }
        } catch (error) {
            return {
                success: false,
                message: "Failed to create a new chat."
            }
        }
    }

    const addConversation = async (chatId, role, content) => {
        setChats((prevChats) =>
            prevChats.map((c) => {
                if (c.id === chatId) {
                    return {
                        ...c,
                        conversations: [...c.conversations, { role, content }]
                    };
                }
                return c;
            })
        );
    }

    const markedAsPackageCompleted = async (chatId) => {
        const chat = getChatById(chatId);
        if (!chat) {
            return;
        }

        const updatedChat = { ...chat, package: true };
        setChats((prevChats) => prevChats.map((c) => (c.id === chat.id ? updatedChat : c)));
    }

    const newConversation = async (chatId, content) => {
        try {
            const chat = getChatById(chatId);
            if (!chat) {
                return { success: false, message: "Chat not found." };
            }

            addConversation(chatId, "user", content);

            const response = await axios.post(`${apiURL}/api/sessions/${chatId}/resume`, { feedback: content });

            if (!response.data || !response.data.thread_id) {
                return { success: false, message: "Failed to add a new conversation." };
            }

            console.log(response.data);

            if (response.data.status === "done") {
                markedAsPackageCompleted(chatId);
                addConversation(chatId, "assistant", response.data.result.content + "\r\n" + response.data.result.solution_code + "\r\n" + response.data.result.tests_summary);
            } else {
                addConversation(chatId, "assistant", response.data.checkpoint.message + "\r\n" + response.data.checkpoint.draft);
            }

            return { success: true };
        } catch (error) {
            return { success: false, message: "Failed to add a new conversation." };
        }
    };

    const chatContextValue = {
        chats,
        loadChats,
        getChatById,
        newChat,
        newConversation
    };

    return (
        <ChatsContext.Provider value={chatContextValue}>
            {children}
        </ChatsContext.Provider>
    );
};

export default ChatsContextProvider;