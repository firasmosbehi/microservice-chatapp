import React, { useState, useEffect, useRef } from 'react';
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

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load rooms when logged in
  useEffect(() => {
    if (isLoggedIn && currentUser) {
      loadRooms();
    }
  }, [isLoggedIn, currentUser]);

  // Load messages when room changes
  useEffect(() => {
    if (currentRoom) {
      loadMessages(currentRoom.id);
      // Set up polling for new messages
      const interval = setInterval(() => {
        loadMessages(currentRoom.id);
      }, 2000); // Poll every 2 seconds
      
      return () => clearInterval(interval);
    }
  }, [currentRoom]);

  const loadRooms = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/chat/rooms`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setRooms(response.data);
      if (response.data.length > 0 && !currentRoom) {
        setCurrentRoom(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to load rooms:', error);
    }
  };

  const loadMessages = async (roomId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/messages/rooms/${roomId}/messages`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
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
      console.error('Failed to load messages:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, loginForm);
      console.log('Login response:', response.data);
      localStorage.setItem('token', response.data.tokens.accessToken);
      setCurrentUser(response.data.user);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed: ' + (error.response?.data?.message || 'Invalid credentials'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register`, registerForm);
      console.log('Registration response:', response.data);
      localStorage.setItem('token', response.data.tokens.accessToken);
      setCurrentUser(response.data.user);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed: ' + (error.response?.data?.message || 'Registration error'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
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
      
      await axios.post(`${API_BASE_URL}/api/messages/messages`, messageData, {
        headers: { 
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
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
      await axios.post(`${API_BASE_URL}/api/chat/rooms/${room.id}/join`, {
        user_id: currentUser.id,
        username: currentUser.username
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setCurrentRoom(room);
    } catch (error) {
      console.error('Failed to join room:', error);
    }
  };

  const createRoom = async () => {
    const roomName = prompt('Enter room name:');
    if (!roomName) return;
    
    try {
      console.log('Current user:', currentUser);
      
      // Convert user ID string to integer for chat service
      // Using a hash-based approach to convert string ID to number
      const userIdHash = currentUser.id.split('').reduce((acc, char) => {
        return acc + char.charCodeAt(0);
      }, 0);
      
      console.log('Creating room with:', {
        name: roomName,
        creator_id: userIdHash,
        description: 'Chat room'
      });
      
      const response = await axios.post(`${API_BASE_URL}/api/chat/rooms`, {
        name: roomName,
        creator_id: userIdHash,
        description: 'Chat room'
      }, {
        headers: { 
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Room creation response:', response.data);
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
              />
              <input
                type="email"
                placeholder="Email"
                value={registerForm.email}
                onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="First Name"
                value={registerForm.firstName}
                onChange={(e) => setRegisterForm({...registerForm, firstName: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Last Name"
                value={registerForm.lastName}
                onChange={(e) => setRegisterForm({...registerForm, lastName: e.target.value})}
                required
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Sign Up'}
              </button>
              <p>
                Already have an account?{' '}
                <button type="button" onClick={() => setShowRegister(false)}>
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
              />
              <input
                type="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                required
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
              <p>
                Don't have an account?{' '}
                <button type="button" onClick={() => setShowRegister(true)}>
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
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      <div className="chat-container">
        {/* Sidebar - Rooms */}
        <div className="sidebar">
          <div className="sidebar-header">
            <h2>Rooms</h2>
            <button onClick={createRoom} className="create-room-btn">+</button>
          </div>
          <div className="rooms-list">
            {rooms.map(room => (
              <div
                key={room.id}
                className={`room-item ${currentRoom?.id === room.id ? 'active' : ''}`}
                onClick={() => setCurrentRoom(room)}
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
                <button onClick={() => joinRoom(currentRoom)}>Join Room</button>
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
                />
                <button onClick={sendMessage} className="send-button">Send</button>
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