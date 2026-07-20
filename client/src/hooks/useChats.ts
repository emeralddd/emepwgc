"use client";

import { useContext } from "react";
import { ChatsContext } from "@/contexts/ChatsContext";

// Custom hook to access chat context
export const useChats = () => {
    const context = useContext(ChatsContext);
    if (!context) {
        throw new Error("useChats must be used within a ChatsContextProvider");
    }
    return context;
}