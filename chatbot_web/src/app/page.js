"use client";
import { useState, useRef, useEffect } from "react";
import { MapPin } from "lucide-react";

export default function Home() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      content: "어서 오세요! 후쿠오카 여행 도우미 챗봇입니다 😊 무엇을 도와드릴까요?",
    },
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages((prev) => [
      ...prev,
      { role: "user", content: input },
    ]);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: "💡 여행 관련 질문을 입력해보세요!",
        },
      ]);
    }, 900);
    setInput("");
  };

  return (
    <div className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg z-10">
      {/* 채팅 박스 */}
      <div className="bg-white/95 rounded-3xl shadow-2xl border border-white px-8 py-6 min-h-[600px] flex flex-col">
        {/* 헤더 */}
        <div className="flex items-center gap-2 pb-3 border-b border-sky-100 mb-2">
          <MapPin className="text-sky-500" />
          <span className="font-bold text-lg text-sky-700">Chat Bot</span>
        </div>
        {/* 채팅 메시지 */}
        <div className="flex-1 overflow-y-auto space-y-4 py-2">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`px-4 py-2 rounded-xl text-base max-w-[80%] whitespace-pre-line shadow
                  ${msg.role === "user"
                    ? "bg-sky-100 text-sky-900"
                    : "bg-green-50 text-green-900 border border-green-200"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        {/* 입력창 */}
        <form onSubmit={sendMessage} className="flex gap-2 mt-2">
          <input
            className="flex-1 p-3 rounded-xl border border-sky-200 bg-sky-50 text-sky-900 outline-sky-400"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="여행지, 일정, 궁금한 것 등 입력해보세요..."
            autoFocus
          />
          <button
            className="bg-sky-400 text-white px-5 rounded-xl font-bold hover:bg-sky-500 transition"
            type="submit"
          >
            보내기
          </button>
        </form>
      </div>
    </div>
  );
}