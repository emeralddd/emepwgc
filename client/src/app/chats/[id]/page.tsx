"use client";

import { apiURL } from "@/utils/VariableName";
import Link from "next/link";
import { FormEvent, use, useState } from "react";
const { useChats } = require("@/hooks/useChats");

export default function ChatScreen({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const { getChatById, newConversation } = useChats();
    const [error, setError] = useState<null | string>(null);
    const [loading, setLoading] = useState(false);

    const chat = getChatById(id);

    const handleNewConversation = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (loading) return; // Prevent multiple submissions
        const form = e.currentTarget;
        const message = String(new FormData(form).get("message") || "");

        try {
            setLoading(true);
            const result = await newConversation(id, message);
            if (!result || !result.success) {
                console.error("Error creating new conversation:", result?.message);
                setError(result?.message || "Failed to create a new conversation.");
            }
            form.reset();
            setError(null);
        } catch (error) {
            console.error("Error creating new conversation:", error);
            setError("An unexpected error occurred while creating a new conversation.");
        } finally {
            setLoading(false);
        }
    }

    const handleDownload = () => {
        // Click to URL to download the package
        if (chat?.package) {
            const url = `${apiURL}/api/sessions/${chat.id}/download`;
            window.open(url, "_blank");
        } else {
            setError("Package is not completed yet. Please wait for the process to finish.");
        }
    }

    return (
        <main className="min-h-screen bg-[#f5f7f2] text-[#17211b]">
            <header className="border-b border-[#dce4d8] bg-[#eaf0e5]">
                <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-5 sm:px-8">
                    <Link href="/" className="text-lg font-black tracking-[-0.04em]">
                        Eme<span className="text-[#65a30d]">.</span>ProbWriter
                    </Link>
                    <Link href="/" className="text-sm font-bold text-[#617061] transition hover:text-[#17211b]">
                        ← All chats
                    </Link>
                </div>
            </header>

            <div className="mx-auto max-w-3xl px-5 py-8 sm:px-8 sm:py-12">
                <div className="mb-8">
                    <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#65a30d]">
                        Problem workspace
                    </p>
                    <h1 className="mt-3 text-3xl font-black tracking-[-0.05em] sm:text-5xl">
                        {chat?.title || "Loading problem..."}
                    </h1>
                </div>

                {error && (
                    <div role="alert" className="mb-5 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">
                        {error}
                    </div>
                )}

                <div className="space-y-4">
                    {chat?.conversations?.map(
                        (message: { role: string; content: string }, index: number) => (
                            <div
                                key={index}
                                className={`max-w-[92%] whitespace-pre-wrap rounded-3xl px-5 py-4 text-sm leading-7 shadow-sm ${
                                    message.role === "user"
                                        ? "ml-auto bg-[#17211b] text-white"
                                        : "border border-[#dce4d8] bg-white text-[#455345]"
                                }`}
                            >
                                <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] opacity-60">
                                    {message.role === "user" ? "You" : "EmeProbWriter"}
                                </p>
                                {message.content}
                            </div>
                        ),
                    )}
                </div>

                {chat?.package ? (
                    <div className="mt-8 flex flex-col gap-4 rounded-3xl border border-[#bef264] bg-[#ecfccb] p-6 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <p className="font-bold">Your package is ready.</p>
                            <p className="mt-1 text-sm text-[#526052]">
                                The statement, solution, and tests are bundled for download.
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={handleDownload}
                            className="rounded-2xl bg-[#17211b] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#314532]"
                        >
                            Download package
                        </button>
                    </div>
                ) : (
                    <form
                        onSubmit={handleNewConversation}
                        className="mt-8 flex gap-3 rounded-3xl border border-[#dce4d8] bg-white p-3 shadow-[0_20px_60px_-35px_rgba(23,33,27,0.35)]"
                    >
                        <input
                            required
                            disabled={loading}
                            name="message"
                            type="text"
                            placeholder="Share feedback or ask for a revision..."
                            className="min-w-0 flex-1 rounded-2xl bg-[#f8faf7] px-4 py-3 text-sm outline-none focus:ring-4 focus:ring-[#d9f99d]/60"
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="rounded-2xl bg-[#17211b] px-4 py-3 text-sm font-bold text-white transition hover:bg-[#314532] disabled:opacity-60"
                        >
                            {loading ? "Sending" : "Send  →"}
                        </button>
                    </form>
                )}
            </div>
        </main>
    );
}