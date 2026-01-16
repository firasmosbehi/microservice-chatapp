import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import './index.css';

const API_BASE_URL = 'http://localhost:8000'; // Gateway service

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    password: '',
    firstName: '',
    lastName: ''
  });
  const [showRegister, setShowRegister] = useState(false);
  
  const [rooms, setRooms] = useState([]);
  const [currentRoom, setCurrentRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastMessageId, setLastMessageId] = useState(null);
  const messagesEndRef = useRef(null);

  // Memoized API functions to prevent unnecessary re-renders
  const apiClient = useRef(
    axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json'
      }
    })
  );

  // Update auth token when it changes
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      apiClient.current.defaults.headers.Authorization = `Bearer ${token}`;
    }
  }, []);

  // Scroll to bottom of messages
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load rooms function
  const loadRooms = useCallback(async () => {
    try {
      const response = await apiClient.current.get('/api/chat/rooms');
      setRooms(response.data);
      if (response.data.length > 0 && !currentRoom) {
        setCurrentRoom(response.data[0]);
      }
    } catch (error) {
      console.warn('Failed to load rooms:', error.message);
    }
  }, [currentRoom]);

  // Load messages function
  const loadMessages = useCallback(async (roomId) => {
    try {
      const response = await apiClient.current.get(`/api/messages/rooms/${roomId}/messages`);
      
      const newMessages = response.data || [];
      
      // Only update if there are new messages
      if (newMessages.length > 0) {
        const latestMessageId = Math.max(...newMessages.map(m => m.id));
        if (latestMessageId !== lastMessageId) {
          setMessages(newMessages);
          setLastMessageId(latestMessageId);
        }
      }
    } catch (error) {
      console.warn('Failed to load messages:', error.message);
    }
  }, [lastMessageId]);

  // Load rooms when logged in
  useEffect(() => {
    if (isLoggedIn && currentUser) {
      loadRooms();
    }
  }, [isLoggedIn, currentUser, loadRooms]);

  // Load messages when room changes
  useEffect(() => {
    let intervalId;
    
    if (currentRoom) {
      loadMessages(currentRoom.id);
      // Set up polling for new messages
      intervalId = setInterval(() => {
        loadMessages(currentRoom.id);
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [currentRoom, loadMessages]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await apiClient.current.post('/api/auth/login', loginForm);
      localStorage.setItem('token', response.data.tokens.accessToken);
      setCurrentUser(response.data.user);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login error:', error);
      alert(`Login failed: ${error.response?.data?.message || 'Invalid credentials'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await apiClient.current.post('/api/auth/register', registerForm);
      localStorage.setItem('token', response.data.tokens.accessToken);
      setCurrentUser(response.data.user);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Registration error:', error);
      alert(`Registration failed: ${error.response?.data?.message || 'Registration error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete apiClient.current.defaults.headers.Authorization;
    setIsLoggedIn(false);
    setCurrentUser(null);
    setRooms([]);
    setMessages([]);
    setCurrentRoom(null);
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !currentRoom) return;
    
    try {
      const messageData = {
        room_id: currentRoom.id,
        content: newMessage.trim(),
        message_type: 'text'
      };
      
      await apiClient.current.post('/api/messages/messages', messageData);
      
      setNewMessage('');
      // Force refresh to show the new message
      setTimeout(() => {
        loadMessages(currentRoom.id);
      }, 100);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    }
  };

  const joinRoom = async (room) => {
    try {
      await apiClient.current.post(`/api/chat/rooms/${room.id}/join`, {
        user_id: currentUser.id,
        username: currentUser.username
      });
      setCurrentRoom(room);
    } catch (error) {
      console.warn('Failed to join room:', error.message);
    }
  };

  const createRoom = async () => {
    const roomName = prompt('Enter room name:');
    if (!roomName) return;
    
    try {
      // Convert user ID string to integer for chat service
      // Using a hash-based approach to convert string ID to number
      const userIdHash = currentUser.id.split('').reduce((acc, char) => {
        return acc + char.charCodeAt(0);
      }, 0);
      
      const response = await apiClient.current.post('/api/chat/rooms', {
        name: roomName,
        creator_id: userIdHash,
        description: 'Chat room'
      });
      
      setRooms(prevRooms => [...prevRooms, response.data]);
      setCurrentRoom(response.data);
    } catch (error) {
      console.error('Failed to create room:', error);
      console.error('Error response:', error.response?.data);
      alert(`Failed to create room: ${error.response?.data?.detail || error.message}`);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h1>Welcome to ChatApp</h1>
          <p>Connect with others in real-time</p>
          
          {showRegister ? (
            <form onSubmit={handleRegister} className="auth-form">
              <h2>Create Account</h2>
              <input
                type="text"
                placeholder="Username"
                value={registerForm.username}
                onChange={(e) => setRegisterForm({...registerForm, username: e.target.value})}
                required
                aria-label="Username"
              />
              <input
                type="email"
                placeholder="Email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                required
                aria-label="Email"
              />
              <input
                type="password"
                placeholder="Password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                required
                aria-label="Password"
              />
              <input
                type="text"
                placeholder="First Name"
                value={registerForm.firstName}
                onChange={(e) => setRegisterForm({...registerForm, firstName: e.target.value})}
                required
                aria-label="First Name"
              />
              <input
                type="text"
                placeholder="Last Name"
                value={registerForm.lastName}
                onChange={(e) => setRegisterForm({...registerForm, lastName: e.target.value})}
                required
                aria-label="Last Name"
              />
              <button type="submit" disabled={isLoading} aria-label="Sign Up">
                {isLoading ? 'Creating...' : 'Sign Up'}
              </button>
              <p>
                Already have an account?{' '}
                <button 
                  type="button" 
                  onClick={() => setShowRegister(false)}
                  aria-label="Switch to Sign In"
                >
                  Sign In
                </button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="auth-form">
              <h2>Sign In</h2>
              <input
                type="email"
                placeholder="Email"
                value={loginForm.email}
                onChange={(e) => setLoginForm({...loginForm, email: e.target.value})}
                required
                aria-label="Email"
              />
              <input
                type="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                required
                aria-label="Password"
              />
              <button type="submit" disabled={isLoading} aria-label="Sign In">
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
              <p>
                Don&apos;t have an account?{' '}
                <button 
                  type="button" 
                  onClick={() => setShowRegister(true)}
                  aria-label="Switch to Sign Up"
                >
                  Sign Up
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="chat-app">
      {/* Header */}
      <header className="chat-header">
        <div className="header-content">
          <h1>ChatApp</h1>
          <div className="user-info">
            <span>Welcome, {currentUser?.firstName || currentUser?.username}</span>
            <button 
              onClick={handleLogout} 
              className="logout-btn"
              aria-label="Logout"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="chat-container">
        {/* Sidebar - Rooms */}
        <div className="sidebar">
          <div className="sidebar-header">
            <h2>Rooms</h2>
            <button 
              onClick={createRoom} 
              className="create-room-btn"
              aria-label="Create new room"
            >
              +
            </button>
          </div>
          <div className="rooms-list">
            {rooms.map(room => (
              <div
                key={room.id}
                className={`room-item ${currentRoom?.id === room.id ? 'active' : ''}`}
                onClick={() => setCurrentRoom(room)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    setCurrentRoom(room);
                  }
                }}
                aria-label={`Select room ${room.name}`}
              >
                <div className="room-name">{room.name}</div>
                <div className="room-members">{room.member_count || 0} members</div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="main-chat">
          {currentRoom ? (
            <>
              <div className="chat-header">
                <h2>{currentRoom.name}</h2>
                <button 
                  onClick={() => joinRoom(currentRoom)}
                  aria-label={`Join room ${currentRoom.name}`}
                >
                  Join Room
                </button>
              </div>
              
              <div className="messages-container">
                {messages.length === 0 ? (
                  <div className="no-messages">No messages yet. Start the conversation!</div>
                ) : (
                  messages.map(message => (
                    <div key={message.id} className="message">
                      <div className="message-sender">{message.sender_name || 'Unknown'}</div>
                      <div className="message-content">{message.content}</div>
                      <div className="message-time">
                        {new Date(message.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
              
              <div className="message-input-container">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type your message..."
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  className="message-input"
                  aria-label="Message input"
                />
                <button 
                  onClick={sendMessage} 
                  className="send-button"
                  aria-label="Send message"
                >
                  Send
                </button>
              </div>
            </>
          ) : (
            <div className="no-room-selected">
              <h2>Select a room to start chatting</h2>
              <p>Choose a room from the sidebar or create a new one</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;