import express from 'express';
import cors from 'cors';

const app = express();
const PORT = 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Mock data - reset for each request to make tests stateless
let users = [];
let rooms = [];
let messages = [];

// Reset mock data periodically to avoid state conflicts
const resetMockData = () => {
  users = [];
  rooms = [];
  messages = [];
};

// Reset every 30 seconds to ensure clean state
setInterval(resetMockData, 30000);

// Helper function to generate IDs
const generateId = () => Math.random().toString(36).substr(2, 9);

// Auth endpoints
app.post('/api/auth/register', (req, res) => {
  const { username, email, password, firstName, lastName } = req.body;
  
  // Always allow registration (stateless for testing)
  const userId = generateId();
  const token = `mock-jwt-token-${userId}`;
  
  const newUser = {
    id: userId,
    username: username || 'testuser',
    email: email || 'test@example.com',
    firstName: firstName || 'Test',
    lastName: lastName || 'User',
    createdAt: new Date().toISOString()
  };
  
  res.status(201).json({
    token: token,
    user: {
      id: newUser.id,
      username: newUser.username,
      email: newUser.email,
      firstName: newUser.firstName,
      lastName: newUser.lastName
    }
  });
});

app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  // Always succeed for testing
  const userId = generateId();
  const token = `mock-jwt-token-${userId}`;
  
  res.json({
    token: token,
    user: {
      id: userId,
      username: 'testuser',
      email: email || 'test@example.com',
      firstName: 'Test',
      lastName: 'User'
    }
  });
});

// User endpoints
app.get('/api/users/profile', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  const userId = authHeader.split(' ')[1].split('-')[3];
  const user = users.find(u => u.id === userId);
  
  if (!user) {
    return res.status(401).json({ error: 'Invalid token' });
  }
  
  res.json({
    id: user.id,
    username: user.username,
    email: user.email,
    createdAt: user.createdAt
  });
});

app.delete('/api/users/me', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  const userId = authHeader.split(' ')[1].split('-')[3];
  users = users.filter(u => u.id !== userId);
  
  res.json({ message: 'User deleted successfully' });
});

// Chat room endpoints
app.post('/api/chat/rooms', (req, res) => {
  const { name, description, isPrivate } = req.body;
  const roomId = generateId();
  
  res.status(201).json({
    id: roomId,
    name: name || 'Test Room',
    description: description || 'Test room description',
    isPrivate: isPrivate || false,
    createdAt: new Date().toISOString()
  });
});

app.get('/api/chat/rooms', (req, res) => {
  res.json(rooms.map(room => ({
    id: room.id,
    name: room.name,
    description: room.description,
    isPrivate: room.isPrivate,
    createdAt: room.createdAt
  })));
});

app.get('/api/chat/rooms/:roomId', (req, res) => {
  const room = rooms.find(r => r.id === req.params.roomId);
  if (!room) {
    return res.status(404).json({ error: 'Room not found' });
  }
  
  res.json({
    id: room.id,
    name: room.name,
    description: room.description,
    isPrivate: room.isPrivate,
    createdAt: room.createdAt,
    memberCount: room.members.length
  });
});

app.post('/api/chat/rooms/:roomId/join', (req, res) => {
  const room = rooms.find(r => r.id === req.params.roomId);
  if (!room) {
    return res.status(404).json({ error: 'Room not found' });
  }
  
  // In a real app, we'd verify auth here
  if (!room.members.includes('mock-user')) {
    room.members.push('mock-user');
  }
  
  res.json({ message: 'Joined room successfully' });
});

app.post('/api/chat/rooms/:roomId/leave', (req, res) => {
  const room = rooms.find(r => r.id === req.params.roomId);
  if (!room) {
    return res.status(404).json({ error: 'Room not found' });
  }
  
  room.members = room.members.filter(m => m !== 'mock-user');
  
  res.json({ message: 'Left room successfully' });
});

// Message endpoints
app.post('/api/chat/rooms/:roomId/messages', (req, res) => {
  const { content, messageType } = req.body;
  const messageId = generateId();
  
  res.status(201).json({
    id: messageId,
    content: content || 'Test message',
    messageType: messageType || 'text',
    roomId: req.params.roomId,
    userId: 'mock-user',
    username: 'testuser',
    createdAt: new Date().toISOString()
  });
});

app.get('/api/messages/room/:roomId', (req, res) => {
  const roomMessages = messages.filter(m => m.roomId === req.params.roomId);
  
  res.json(roomMessages.map(msg => ({
    id: msg.id,
    content: msg.content,
    messageType: msg.messageType,
    userId: msg.userId,
    username: msg.username,
    createdAt: msg.createdAt
  })));
});

app.put('/api/messages/:messageId/read', (req, res) => {
  const message = messages.find(m => m.id === req.params.messageId);
  if (!message) {
    return res.status(404).json({ error: 'Message not found' });
  }
  
  res.json({ message: 'Message marked as read' });
});

app.get('/api/messages/unread/:userId', (req, res) => {
  // Mock unread count
  res.json({ count: 0 });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', services: ['auth', 'chat', 'messages'] });
});

app.get('/', (req, res) => {
  res.json({ message: 'Mock Gateway Service for Frontend Integration Tests' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Mock Gateway Service running on port ${PORT}`);
  console.log(`📋 Available endpoints:`);
  console.log(`   POST /api/auth/register`);
  console.log(`   POST /api/auth/login`);
  console.log(`   GET  /api/users/profile`);
  console.log(`   POST /api/chat/rooms`);
  console.log(`   GET  /api/chat/rooms`);
  console.log(`   POST /api/chat/rooms/:id/messages`);
});