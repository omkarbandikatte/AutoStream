import { useState, useRef, useEffect } from 'react';
import EmojiPicker from 'emoji-picker-react';

// Simple markdown parser function
const parseMarkdown = (text) => {
  if (!text) return null;
  
  // Split by newlines first
  const lines = text.split('\n');
  
  return lines.map((line, lineIdx) => {
    const elements = [];
    let currentIdx = 0;
    
    // Parse line for bold (**text**), line breaks, etc.
    const boldRegex = /\*\*([^*]+)\*\*/g;
    let match;
    let lastIndex = 0;
    
    while ((match = boldRegex.exec(line)) !== null) {
      // Add text before bold
      if (match.index > lastIndex) {
        elements.push(line.substring(lastIndex, match.index));
      }
      // Add bold text
      elements.push(
        <strong key={`bold-${lineIdx}-${match.index}`}>{match[1]}</strong>
      );
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < line.length) {
      elements.push(line.substring(lastIndex));
    }
    
    // Return line with proper JSX structure
    return (
      <div key={`line-${lineIdx}`}>
        {elements.length > 0 ? elements : line}
      </div>
    );
  });
};

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'system',
      text: "Welcome! I'm AutoStream Assistant. I can help you with pricing, plans, and answer your questions. What can I help you with today?",
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    // Generate or retrieve session ID from localStorage
    const saved = localStorage.getItem('autostream_session_id');
    const id = saved || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('autostream_session_id', id);
    return id;
  });
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
    const emojiPickerRef = useRef(null);
    const messagesContainerRef = useRef(null);

  const handleSend = async () => {
    if (input.trim() && !isLoading) {
      const userMessage = {
        id: messages.length + 1,
        type: 'user',
        text: input,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages(prev => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      // Add loading indicator
      const loadingMessage = {
        id: messages.length + 2,
        type: 'searching',
        text: 'Agent is processing your request...',
      };
      setMessages(prev => [...prev, loadingMessage]);

      try {
        const response = await fetch('https://autostream-backend.onrender.com/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            message: input,
            session_id: sessionId
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to get response from server');
        }

        const data = await response.json();
        
        // Update session ID if returned
        if (data.session_id) {
          setSessionId(data.session_id);
          localStorage.setItem('autostream_session_id', data.session_id);
        }

        // Remove loading message and add agent response
        setMessages(prev => {
          const withoutLoading = prev.filter(msg => msg.type !== 'searching');
          return [
            ...withoutLoading,
            {
              id: prev.length + 1,
              type: 'agent',
              text: data.reply,
              time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
            },
          ];
        });
      } catch (error) {
        console.error('Error:', error);
        // Remove loading message and show error
        setMessages(prev => {
          const withoutLoading = prev.filter(msg => msg.type !== 'searching');
          return [
            ...withoutLoading,
            {
              id: prev.length + 1,
              type: 'agent',
              text: 'Sorry, I encountered an error. Please make sure the backend server is running and try again.',
              time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
            },
          ];
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

    const onEmojiClick = (emojiData) => {
      setInput(prev => prev + emojiData.emoji);
    };

    // Close emoji picker when clicking outside
    useEffect(() => {
      const handleClickOutside = (event) => {
        if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target)) {
          setShowEmojiPicker(false);
        }
      };

      if (showEmojiPicker) {
        document.addEventListener('mousedown', handleClickOutside);
      }

      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }, [showEmojiPicker]);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
      const container = messagesContainerRef.current;
      if (!container) return;
      // Scroll to bottom smoothly after messages render
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }, [messages]);

  return (
    <div className="h-screen flex flex-col overflow-hidden text-slate-900 bg-slate-50">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-4 bg-white border-b border-slate-200 z-20 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center size-9 bg-primary rounded-xl text-white shadow-lg shadow-primary/20">
            <span className="material-symbols-outlined text-xl">auto_videocam</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-800">
            AutoStream Assistant
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden flex justify-center">
        <div className="w-full max-w-4xl flex flex-col h-full relative">
          {/* Messages */}
          <div ref={messagesContainerRef} className="flex-1 overflow-y-auto custom-scrollbar px-6 py-10 space-y-8">
            {messages.map((message) => {
              if (message.type === 'system' || message.type === 'agent') {
                return (
                  <div key={message.id} className="flex items-start gap-4 mr-12 md:mr-24">
                    <div className="flex items-center justify-center bg-white border border-slate-200 shadow-sm rounded-full size-10 shrink-0">
                      <span className="material-symbols-outlined text-primary text-xl">
                        {message.type === 'system' ? 'smart_toy' : 'database'}
                      </span>
                    </div>
                    <div className="space-y-3">
                      <div className="bg-slate-100 text-slate-800 px-6 py-4 rounded-2xl rounded-tl-none text-[15px] leading-relaxed shadow-sm">
                        <div className="whitespace-pre-wrap">
                          {parseMarkdown(message.text)}
                        </div>
                      </div>
                      {message.time && (
                        <p className="text-[11px] text-slate-400 ml-1 uppercase tracking-wider font-semibold">
                          {message.time}
                        </p>
                      )}
                    </div>
                  </div>
                );
              } else if (message.type === 'user') {
                return (
                  <div key={message.id} className="flex items-start gap-4 justify-end ml-12 md:ml-24">
                    <div className="space-y-1 flex flex-col items-end">
                      <div className="bg-primary text-white px-6 py-4 rounded-2xl rounded-tr-none text-[15px] leading-relaxed shadow-lg shadow-primary/10">
                        {message.text}
                      </div>
                      {message.time && (
                        <p className="text-[11px] text-slate-400 mr-1 uppercase tracking-wider font-semibold">
                          {message.time}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center justify-center bg-slate-200 rounded-full size-10 shrink-0 overflow-hidden border-2 border-white shadow-sm">
                      <span className="material-symbols-outlined text-slate-600">person</span>
                    </div>
                  </div>
                );
              } else if (message.type === 'searching') {
                return (
                  <div key={message.id} className="flex items-start gap-4 mr-12 md:mr-24">
                    <div className="flex items-center justify-center bg-white border border-slate-200 shadow-sm rounded-full size-10 shrink-0">
                      <span className="material-symbols-outlined text-primary text-xl">
                        database
                      </span>
                    </div>
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center gap-3 px-5 py-3 bg-white border border-slate-200 rounded-2xl rounded-tl-none shadow-sm">
                        <div className="flex gap-1">
                          <div className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce"></div>
                          <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                          <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                        </div>
                        <span className="text-sm text-slate-500 font-medium italic">
                          {message.text}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              }
              return null;
            })}
          </div>

          {/* Input Area */}
          <div className="p-6 bg-transparent">
            <div className="max-w-4xl mx-auto">
              <div className="relative bg-white rounded-3xl shadow-2xl border border-slate-200 flex flex-col p-2 transition-all focus-within:ring-4 focus-within:ring-primary/5">
                <div className="flex items-center gap-1 px-3 py-1.5 border-b border-slate-50 mb-1">
                  <button
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                    className="p-2 hover:bg-slate-50 rounded-xl text-slate-500 transition-colors"
                    title="Emoji"
                  >
                    <span className="material-symbols-outlined text-xl">mood</span>
                  </button>
                </div>
                  {/* Emoji Picker */}
                  {showEmojiPicker && (
                    <div ref={emojiPickerRef} className="absolute bottom-16 left-3 z-50">
                      <EmojiPicker
                        onEmojiClick={onEmojiClick}
                        width={350}
                        height={400}
                        theme="light"
                        searchDisabled={false}
                        skinTonesDisabled={false}
                        previewConfig={{ showPreview: false }}
                      />
                    </div>
                  )}
                <div className="flex items-end gap-3 px-3 pb-3">
                  <textarea
                    className="flex-1 bg-transparent border-none focus:ring-0 text-slate-800 placeholder-slate-400 resize-none min-h-[50px] max-h-40 text-[15px] py-3 leading-relaxed outline-none"
                    placeholder="Ask about your content or search your knowledge base..."
                    rows="1"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                  <button
                    onClick={handleSend}
                    className="bg-primary hover:bg-primary/90 text-white rounded-2xl w-12 h-12 flex items-center justify-center transition-all active:scale-95 shadow-xl shadow-primary/20 shrink-0"
                  >
                    <span className="material-symbols-outlined text-2xl">send</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ChatPage;
