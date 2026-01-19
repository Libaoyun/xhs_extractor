"use client";

import { useState, useEffect } from "react";
import dynamic from 'next/dynamic';

function ExtractorPage() {
  const [url, setUrl] = useState("http://xhslink.com/o/1KNnDz3hi7o");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState("");
  const [aiResult, setAiResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  // 获取历史记录
  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:8000/history");
      const data = await res.json();
      if (data.status === "success") {
        setHistory(data.data);
      }
    } catch (e) {
      console.error("Failed to fetch history:", e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleExtract = async () => {
    if (!url) {
      setError("请输入小红书链接");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);
    setAiResult(null);
    setAiStatus("");

    try {
      const response = await fetch("http://localhost:8000/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error("提取失败，请检查后端服务是否启动");

      const data = await response.json();
      setTimeout(() => {
        setResult({ ...data.data, file_path: data.file_path });
        setLoading(false);
        fetchHistory();
      }, 500);
    } catch (err: any) {
      setError(err.message || "发生未知错误");
      setLoading(false);
    }
  };

  const handleAIRecreate = async () => {
    if (!result) return;
    setAiLoading(true);
    setAiStatus("Agent 正在思考中...");
    setAiResult(null);
    setError("");

    try {
      const statusTimer = setTimeout(() => setAiStatus("正在生成爆款文案..."), 1500);

      const response = await fetch("http://localhost:8000/recreate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: result.title,
          content: result.content,
          file_path: result.file_path,
          url: url,
        }),
      });

      clearTimeout(statusTimer);
      const data = await response.json();

      if (data.status === "success") {
        setAiResult(data.data);
        fetchHistory();
      } else {
        setError(data.message || "AI 生成失败");
      }
    } catch (err: any) {
      setError("AI 服务连接失败");
    } finally {
      setAiLoading(false);
      setAiStatus("");
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    const btn = document.getElementById(id);
    if (btn) {
      const originalText = btn.innerHTML;
      btn.innerHTML = `<span class="flex items-center text-emerald-400"><svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>已复制</span>`;
      setTimeout(() => (btn.innerHTML = originalText), 2000);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 font-sans pb-20">
      {/* 顶部导航 */}
      <nav className="bg-zinc-900/50 border-b border-zinc-800 sticky top-0 z-50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/20">X</div>
            <span className="font-bold text-xl tracking-tight text-zinc-100">XHS Extractor</span>
          </div>
          <div className="text-sm text-zinc-500">AI Powered Content Engine</div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">

        {/* 搜索区域 */}
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h1 className="text-4xl font-extrabold text-zinc-100 tracking-tight">
            一键提取，<span className="text-blue-500">AI 二创</span>
          </h1>
          <p className="text-lg text-zinc-400">
            复制小红书笔记链接，立即获取爆款文案灵感
          </p>

          <div className="relative flex items-center shadow-2xl rounded-2xl bg-zinc-900 ring-1 ring-zinc-800 focus-within:ring-2 focus-within:ring-blue-500 transition-all overflow-hidden">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="在此粘贴链接..."
              className="flex-1 border-0 bg-transparent py-4 pl-6 pr-4 text-zinc-100 placeholder:text-zinc-600 focus:ring-0 sm:text-lg"
              onKeyDown={(e) => e.key === "Enter" && handleExtract()}
            />
            <div className="pr-2">
              <button
                onClick={handleExtract}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2.5 rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    <span>提取中</span>
                  </>
                ) : (
                  <span>开始提取</span>
                )}
              </button>
            </div>
          </div>
          {error && <p className="text-red-400 text-sm font-medium animate-pulse">{error}</p>}
        </div>

        {/* 主内容区 */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

            {/* 左侧：原文卡片 */}
            <div className="lg:col-span-5 bg-zinc-900 rounded-2xl border border-zinc-800 shadow-sm overflow-hidden sticky top-24">
              <div className="p-6 border-b border-zinc-800 bg-zinc-900/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-400 font-bold border border-zinc-700">
                    {result.author?.[0] || "A"}
                  </div>
                  <div>
                    <h3 className="font-bold text-zinc-200 text-sm">{result.author}</h3>
                    <p className="text-xs text-zinc-500">原文内容</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium border border-emerald-500/20">已提取</span>
              </div>

              <div className="p-6 space-y-4">
                <h2 className="text-xl font-bold text-zinc-100 leading-snug">{result.title}</h2>
                <div className="max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                  <p className="text-zinc-400 whitespace-pre-wrap leading-relaxed text-sm">{result.content}</p>
                </div>
              </div>

              <div className="p-4 bg-zinc-900 border-t border-zinc-800 flex justify-between items-center">
                <button
                  id="btn-copy-original"
                  onClick={() => handleCopy(`【${result.title}】\n${result.content}`, "btn-copy-original")}
                  className="text-zinc-500 hover:text-zinc-300 text-sm font-medium transition-colors flex items-center gap-1.5"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                  复制原文
                </button>
                <button
                  onClick={handleAIRecreate}
                  disabled={aiLoading}
                  className={`px-5 py-2 rounded-lg font-bold text-sm transition-all flex items-center gap-2 shadow-lg ${aiLoading
                      ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
                      : "bg-blue-600 hover:bg-blue-500 text-white active:scale-95 shadow-blue-500/20"
                    }`}
                >
                  {aiLoading ? (
                    <>
                      <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                      <span>{aiStatus || "生成中..."}</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                      <span>AI 爆款二创</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* 右侧：AI 结果 */}
            <div className="lg:col-span-7 space-y-6">
              {aiResult ? (
                <div className="grid grid-cols-1 gap-6">
                  {[
                    { id: 'style_a', name: '🔥 高反差风格', desc: '观点犀利 · 颠覆认知', bg: 'bg-orange-500/10', border: 'border-orange-500/20', text: 'text-orange-400', icon: 'text-orange-500' },
                    { id: 'style_b', name: '📚 干货拆解', desc: '逻辑清晰 · 步骤详尽', bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400', icon: 'text-blue-500' },
                    { id: 'style_c', name: '💡 情绪共鸣', desc: '故事感强 · 引发共情', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', text: 'text-emerald-400', icon: 'text-emerald-500' }
                  ].map((style) => (
                    <div key={style.id} className={`bg-zinc-900 rounded-2xl border ${style.border} p-6 shadow-sm hover:bg-zinc-800/80 transition-colors`}>
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-lg ${style.bg} flex items-center justify-center ${style.icon}`}>
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
                          </div>
                          <div>
                            <h4 className={`font-bold ${style.text}`}>{style.name}</h4>
                            <p className="text-xs text-zinc-500">{style.desc}</p>
                          </div>
                        </div>
                        <button
                          id={`btn-copy-${style.id}`}
                          onClick={() => handleCopy(`【${aiResult[style.id]?.recreation_title}】\n${aiResult[style.id]?.recreation_content}`, `btn-copy-${style.id}`)}
                          className="text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-400 px-3 py-1.5 rounded-md border border-zinc-700 transition-colors font-medium hover:text-zinc-200"
                        >
                          复制
                        </button>
                      </div>

                      <h3 className="text-lg font-bold text-zinc-100 mb-3">
                        {aiResult[style.id]?.recreation_title}
                      </h3>
                      <p className="text-zinc-400 text-sm leading-relaxed whitespace-pre-wrap mb-5">
                        {aiResult[style.id]?.recreation_content}
                      </p>

                      <div className="bg-black/20 rounded-xl p-4 border border-zinc-800 flex gap-3">
                        <div className="mt-0.5 text-zinc-600">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                        </div>
                        <div className="space-y-1">
                          <p className="text-xs text-zinc-300 font-medium">封面建议："{aiResult[style.id]?.visual_suggestion?.cover_text}"</p>
                          <p className="text-xs text-zinc-500">背景描述：{aiResult[style.id]?.visual_suggestion?.bg_description}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-full min-h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-zinc-800 rounded-2xl bg-zinc-900/30 text-zinc-600 space-y-4">
                  <div className="w-16 h-16 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center shadow-sm">
                    <svg className="w-8 h-8 text-zinc-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                  </div>
                  <p className="text-sm font-medium">点击左侧“AI 爆款二创”开始创作</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 历史记录 */}
        {history.length > 0 && (
          <div className="pt-12 border-t border-zinc-800">
            <h2 className="text-xl font-bold text-zinc-100 mb-6">
              历史记录
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {history.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    setResult({ ...item, file_path: null });
                    if (item.ai_result) setAiResult(item.ai_result);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                  className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-blue-500/50 cursor-pointer transition-all group"
                >
                  <h4 className="font-bold text-zinc-200 truncate mb-2 group-hover:text-blue-400 transition-colors text-sm">{item.title || "无标题"}</h4>
                  <p className="text-xs text-zinc-500 line-clamp-2 mb-3 leading-relaxed">{item.content}</p>
                  <div className="flex justify-between items-center text-[10px] text-zinc-600">
                    <span>{new Date(item.created_at).toLocaleString()}</span>
                    {item.ai_result && (
                      <span className="bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-full font-medium border border-blue-500/20">已二创</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </main>
  );
}

const Home = dynamic(() => Promise.resolve(ExtractorPage), { ssr: false });
export default Home;
