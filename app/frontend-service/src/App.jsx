import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

const API_BASE_URL = 'http://localhost:8000'; // Gateway service

function App() {
  const [services, setServices] = useState([
    { name: 'User Service', url: 'http://localhost:3001', status: 'checking' },
    { name: 'Chat Service', url: 'http://localhost:3002', status: 'checking' },
    { name: 'Message Service', url: 'http://localhost:3003', status: 'checking' },
    { name: 'Gateway Service', url: 'http://localhost:8000', status: 'checking' }
  ]);

  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  // Check service status
  useEffect(() => {
    const checkServices = async () => {
      const updatedServices = await Promise.all(
        services.map(async (service) => {
          try {
            await axios.get(service.url, { timeout: 3000 });
            return { ...service, status: 'online' };
          } catch (error) {
            return { ...service, status: 'offline' };
          }
        })
      );
      setServices(updatedServices);
    };

    checkServices();
    const interval = setInterval(checkServices, 5000);
    return () => clearInterval(interval);
  }, []);

  // Mock message sending (would connect to real APIs)
  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    
    try {
      // This would call the actual message service through gateway
      const message = {
        id: Date.now(),
        content: newMessage,
        sender: 'You',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages([...messages, message]);
      setNewMessage('');
      
      // Simulate API call to gateway
      await axios.post(`${API_BASE_URL}/messages`, {
        content: newMessage,
        sender_id: 1,
        room_id: 1
      });
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>ChatApp Microservices Dashboard</h1>
        <p>Frontend connected to backend microservices</p>
      </header>

      <div className="services-grid">
        {services.map((service, index) => (
          <div key={index} className="service-card">
            <h3>{service.name}</h3>
            <div className={`status ${service.status}`}>
              {service.status === 'online' ? '✓ Online' : '✗ Offline'}
            </div>
            <p>{service.url}</p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '40px' }}>
        <h2>Chat Interface</h2>
        <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px' }}>
          <div style={{ height: '300px', overflowY: 'auto', marginBottom: '15px', border: '1px solid #eee', padding: '10px' }}>
            {messages.map((msg, index) => (
              <div key={index} style={{ marginBottom: '10px', padding: '8px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                <strong>{msg.sender}</strong>: {msg.content}
                <small style={{ float: 'right', color: '#666' }}>{msg.timestamp}</small>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex' }}>
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              style={{ flex: 1, padding: '10px', marginRight: '10px', borderRadius: '4px', border: '1px solid #ddd' }}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button 
              onClick={sendMessage}
              style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;