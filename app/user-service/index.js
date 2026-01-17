const app = require('./server');

const PORT = process.env.PORT || 3001;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/chatapp-users';

app.listen(PORT, () => {
  console.log(`User Service running on port ${PORT}`);
  console.log(`MongoDB URI: ${MONGODB_URI}`);
});
