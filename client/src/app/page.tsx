"use client";

import { useChats } from "@/hooks/useChats";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

type HomeChat = { id: string; title: string; package?: boolean };
type HomeChatsApi = {
    chats: HomeChat[];
    newChat: (idea: string, language: string, testCount: string) => Promise<{ success: boolean; payload?: string; message?: string }>;
};

export default function Home() {
    const { chats, newChat } = useChats() as HomeChatsApi;
    const [error, setError] = useState<null | string>(null);
    const [loading, setLoading] = useState(false);

    const router = useRouter();

    const handleNewChat = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (loading) return; // Prevent multiple submissions
        const formData = new FormData(e.currentTarget);
        const idea = String(formData.get("idea") || "");
        const language = String(formData.get("language") || "");
        const testCount = String(formData.get("testCount") || "");

        try {
            setLoading(true);
            const newChatResult = await newChat(idea, language, testCount);
            if (!newChatResult || !newChatResult.success) {
                console.error("Error creating new chat:", newChatResult?.message);
                setError(newChatResult?.message || "Failed to create a new chat.");
                return;
            }

            router.replace(`/chats/${newChatResult.payload}`);
        } catch (error) {
            console.error("Error creating new chat:", error);
            setError("An unexpected error occurred while creating a new chat.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-[#f5f7f2] text-[#17211b]">
            <div className="mx-auto grid min-h-screen max-w-7xl lg:grid-cols-[280px_1fr]">
                <aside className="border-b border-[#dce4d8] bg-[#eaf0e5] px-6 py-7 lg:border-b-0 lg:border-r">
                    <div className="flex items-center justify-between lg:block">
                        <Link href="/" className="text-lg font-black tracking-[-0.04em]">Eme<span className="text-[#65a30d]">.</span>ProbWriter</Link>
                        <span className="rounded-full bg-[#17211b] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-[#d9f99d]">AI studio</span>
                    </div>
                    <div className="mt-12 hidden lg:block">
                        <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#708070]">Workspace</p>
                        <h1 className="mt-3 text-3xl font-black leading-none tracking-[-0.06em]">Your problem<br />lab.</h1>
                        <p className="mt-4 text-sm leading-6 text-[#5e6d60]">Turn a rough idea into a polished programming problem, test suite, and solution.</p>
                    </div>
                    <div className="mt-8 lg:mt-20">
                        <div className="flex items-center justify-between">
                            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#708070]">Recent chats</p>
                            <span className="text-xs text-[#708070]">{chats.length}</span>
                        </div>
                        <div className="mt-3 space-y-2">
                            {chats.length === 0 ? <p className="text-sm text-[#708070]">Your ideas will appear here.</p> : chats.map((chat) => (
                                <Link key={chat.id} href={`/chats/${chat.id}`} className="block truncate rounded-xl px-3 py-2.5 text-sm font-medium text-[#526052] transition hover:bg-white hover:text-[#17211b]">
                                    {chat.title}
                                </Link>
                            ))}
                        </div>
                    </div>
                </aside>
                <section className="px-5 py-8 sm:px-10 sm:py-12 lg:px-20 lg:py-20">
                    <div className="mx-auto max-w-2xl">
                        <div className="mb-14 lg:hidden">
                            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#708070]">Workspace</p>
                            <h1 className="mt-3 text-4xl font-black tracking-[-0.06em]">Your problem lab.</h1>
                        </div>
                        <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#65a30d]">New problem</p>
                        <h2 className="mt-3 max-w-lg text-4xl font-black leading-[0.98] tracking-[-0.06em] sm:text-6xl">Start with a spark.</h2>
                        <p className="mt-6 max-w-lg text-base leading-7 text-[#617061]">Describe the challenge in plain language. EmeProbWriter will help shape the constraints, examples, and implementation details.</p>
                        <form onSubmit={handleNewChat} className="mt-10 space-y-5 rounded-3xl border border-[#dce4d8] bg-white p-5 shadow-[0_20px_60px_-35px_rgba(23,33,27,0.35)] sm:p-8">
                            <label className="block"><span className="mb-2 block text-xs font-bold uppercase tracking-[0.14em] text-[#708070]">Problem idea</span><textarea required disabled={loading} name="idea" rows={4} placeholder="e.g. Find the shortest route through a shifting maze..." className="w-full resize-none rounded-2xl border border-[#dce4d8] bg-[#f8faf7] px-4 py-3 text-sm outline-none transition placeholder:text-[#9aa69b] focus:ring-4 focus:ring-[#d9f99d]/60" /></label>
                            <div className="grid gap-5 sm:grid-cols-2"><label className="block"><span className="mb-2 block text-xs font-bold uppercase tracking-[0.14em] text-[#708070]">Language</span><input required disabled={loading} name="language" type="text" placeholder="cpp / python" className="w-full rounded-2xl border border-[#dce4d8] bg-[#f8faf7] px-4 py-3 text-sm outline-none transition placeholder:text-[#9aa69b] focus:ring-4 focus:ring-[#d9f99d]/60" /></label><label className="block"><span className="mb-2 block text-xs font-bold uppercase tracking-[0.14em] text-[#708070]">Test count</span><input required disabled={loading} name="testCount" type="number" min="1" placeholder="5" className="w-full rounded-2xl border border-[#dce4d8] bg-[#f8faf7] px-4 py-3 text-sm outline-none transition placeholder:text-[#9aa69b] focus:ring-4 focus:ring-[#d9f99d]/60" /></label></div>
                            {error && <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
                            <button type="submit" disabled={loading} className="flex w-full items-center justify-center rounded-2xl bg-[#17211b] px-5 py-4 text-sm font-bold text-white transition hover:bg-[#314532] disabled:cursor-wait disabled:opacity-60">{loading ? "Creating your workspace..." : "Start planning  →"}</button>
                        </form>
                    </div>
                </section>
            </div>
        </main>
    );
}
