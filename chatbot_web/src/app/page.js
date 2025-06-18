
"use client";
import { useState, useRef, useEffect } from "react";
import { MapPin, Loader2  } from "lucide-react"; // 아이콘 필요시

export default function ChatBot() {
  const [messages, setMessages] = useState([
    { role: "bot", content: "어서 오세요! 후쿠오카 여행 도우미 챗봇입니다 😊\n무엇을 도와드릴까요?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false); // 로딩 상태
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (e) => {
  e.preventDefault();
  if (!input.trim()) return;

  const userMessage = { role: "user", content: input };
  setMessages((prev) => [...prev, userMessage]);
  setInput("");
  setLoading(true); // 응답 대기 중

  try {
    const res = await fetch(`http://localhost:8020/ask?question=${encodeURIComponent(input)}`);
    const data = await res.json();

    const botMessage = {
      role: "bot",
      content: data.answer || "죄송해요, 답변을 불러오지 못했어요 😢",
    };
    setMessages((prev) => [...prev, botMessage]);
  } catch (error) {
    console.error("API 호출 실패:", error);
    setMessages((prev) => [
      ...prev,
      { role: "bot", content: "서버 오류가 발생했어요 😢" },
    ]);
  }
  setLoading(false); // 응답 끝
};

  return (
    // 화면 정중앙에 1개 div만!
    <div className="min-h-screen flex items-center justify-center">
      <div
        className="
          w-full
          max-w-7xl
          min-h-[60vh]
          flex flex-col
          rounded-3xl
          shadow-2xl
          bg-white/85
          backdrop-blur-lg
          p-12
        "
      >
        {/* 헤더 */}
        <div className="flex items-center gap-2 pb-4 border-b border-sky-100 mb-4">
          <MapPin className="text-sky-500" />
          <span className="font-bold text-xl text-sky-700">Chat Bot</span>
        </div>
        {/* 메시지 영역 */}
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
              {/* 로딩 상태면 로딩 스피너 표시*/}
              {loading && (
                <div className="flex justify-start items-center gap-2">
                  <Loader2 className="w-5 h-5 text-sky-400 animate-spin" />
                  <span className="text-sky-400 font-medium">답변을 생성 중입니다...</span>
                </div>
              )}
          <div ref={messagesEndRef} />
        </div>
        {/* 입력창 */}
        <form onSubmit={sendMessage} className="flex gap-2 mt-4">
          <input
            className="flex-1 p-3 rounded-xl border border-sky-200 bg-sky-50 text-sky-900 outline-sky-400"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="여행지, 일정, 궁금한 것 등 입력해보세요..."
            autoFocus
            disabled={loading} // 로딩 중 입력창 비활성화(선택)
          />
          <button
            className="bg-sky-400 text-white px-7 rounded-xl font-bold hover:bg-sky-500 transition"
            type="submit"
            disabled={loading} // 로딩 중 버튼 비활성화(선택)
          >
            보내기
          </button>
        </form>
      </div>
    </div>
  );
}
