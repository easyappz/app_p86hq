import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMessages, sendMessage } from '../../api/messages';
import { getCurrentUser } from '../../api/auth';
import './styles.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const navigate = useNavigate();
  const intervalRef = useRef(null);
  const prevScrollHeightRef = useRef(0);

  // Load current user
  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await getCurrentUser();
        setCurrentUser(userData);
      } catch (error) {
        console.error('Failed to load user:', error);
        navigate('/login');
      }
    };
    loadUser();
  }, [navigate]);

  // Load initial messages
  useEffect(() => {
    if (currentUser) {
      loadMessages(1, true);
    }
  }, [currentUser]);

  // Auto-refresh messages every 3 seconds
  useEffect(() => {
    if (currentUser) {
      intervalRef.current = setInterval(() => {
        loadMessages(1, true, true);
      }, 3000);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [currentUser, page]);

  // Scroll to bottom on new messages
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const loadMessages = async (pageNum, isInitial = false, isAutoRefresh = false) => {
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      const data = await getMessages(pageNum, 20);
      
      if (isInitial) {
        setMessages(data.results.reverse());
        setHasMore(!!data.next);
        setTimeout(scrollToBottom, 100);
      } else if (isAutoRefresh) {
        // Only add new messages on auto-refresh
        const newMessages = data.results.reverse();
        setMessages(prev => {
          const lastId = prev.length > 0 ? prev[prev.length - 1].id : 0;
          const filtered = newMessages.filter(msg => msg.id > lastId);
          if (filtered.length > 0) {
            setTimeout(scrollToBottom, 100);
            return [...prev, ...filtered];
          }
          return prev;
        });
      } else {
        // Load older messages (pagination)
        const olderMessages = data.results.reverse();
        setMessages(prev => [...olderMessages, ...prev]);
        setHasMore(!!data.next);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
      if (error.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleScroll = () => {
    if (messagesContainerRef.current) {
      const { scrollTop } = messagesContainerRef.current;
      
      if (scrollTop === 0 && hasMore && !isLoading) {
        prevScrollHeightRef.current = messagesContainerRef.current.scrollHeight;
        const nextPage = page + 1;
        setPage(nextPage);
        loadMessages(nextPage, false, false);
      }
    }
  };

  useEffect(() => {
    if (messagesContainerRef.current && prevScrollHeightRef.current > 0) {
      const newScrollHeight = messagesContainerRef.current.scrollHeight;
      messagesContainerRef.current.scrollTop = newScrollHeight - prevScrollHeightRef.current;
      prevScrollHeightRef.current = 0;
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!messageText.trim() || isSending) return;

    setIsSending(true);
    try {
      const newMessage = await sendMessage(messageText.trim());
      setMessages(prev => [...prev, newMessage]);
      setMessageText('');
      setTimeout(scrollToBottom, 100);
    } catch (error) {
      console.error('Failed to send message:', error);
      if (error.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setIsSending(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  return (
    <div className="chat-container" data-easytag="id1-react/src/components/Chat/index.jsx">
      <div className="chat-header">
        <h1 className="chat-title">Групповой чат</h1>
        <button className="profile-button" onClick={handleProfileClick}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
          </svg>
        </button>
      </div>

      <div 
        className="messages-container" 
        ref={messagesContainerRef}
        onScroll={handleScroll}
      >
        {isLoading && page === 1 && (
          <div className="loading-indicator">Загрузка...</div>
        )}
        
        {messages.map((message) => {
          const isOwn = currentUser && message.author.id === currentUser.id;
          
          return (
            <div 
              key={message.id} 
              className={`message ${isOwn ? 'message-own' : 'message-other'}`}
            >
              <div className="message-content">
                {!isOwn && (
                  <div className="message-author">{message.author.username}</div>
                )}
                <div className="message-text">{message.text}</div>
                <div className="message-time">{formatTime(message.created_at)}</div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      <form className="message-input-container" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="message-input"
          placeholder="Введите сообщение..."
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          disabled={isSending}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={!messageText.trim() || isSending}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="currentColor"/>
          </svg>
        </button>
      </form>
    </div>
  );
};

export default Chat;
