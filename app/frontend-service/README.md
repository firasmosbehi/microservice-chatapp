# Frontend Service

React-based frontend for the ChatApp microservices platform.

## Features

- Real-time chat interface
- User authentication (login/registration)
- Room management (create, join, leave)
- Message sending and receiving
- Responsive design with modern UI

## Technology Stack

- **Framework**: React 18
- **Build Tool**: Vite 4
- **Styling**: CSS Modules
- **HTTP Client**: Axios
- **Testing**: Vitest + Testing Library

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd app/frontend-service
npm install
```

### Development

```bash
# Start development server
npm start

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend-service/
├── src/
│   ├── components/          # React components
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   │   └── validation.js   # Form validation and logging utilities
│   ├── App.jsx             # Main application component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── .eslintrc.json          # ESLint configuration
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies and scripts
└── SECURITY_ADVISORY.md    # Security information
```

## Development Guidelines

### Code Quality

- ESLint is configured with React and Hooks plugins
- Console statements are categorized (debug, info, warn, error)
- React Hooks dependencies are properly managed
- Accessibility attributes are included for screen readers

### Security

- All API calls use proper authentication headers
- Input validation implemented for forms
- Development server vulnerabilities documented in SECURITY_ADVISORY.md
- Token management follows security best practices

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- src/components/Component.test.jsx

# Run tests with coverage
npm run test:coverage
```

## Environment Variables

Create a `.env` file in the project root:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_NODE_ENV=development
```

## API Integration

The frontend communicates with the Gateway Service through:

- **Authentication**: `/api/auth/login`, `/api/auth/register`
- **Chat Rooms**: `/api/chat/rooms`
- **Messages**: `/api/messages/rooms/{room_id}/messages`

All requests include JWT tokens for authentication.

## Deployment

### Production Build

```bash
npm run build
```

The build output will be in the `dist/` directory.

### Docker Deployment

```bash
# Build Docker image
docker build -t frontend-service .

# Run container
docker run -p 3000:80 frontend-service
```

## Troubleshooting

### Common Issues

1. **Port already in use**: The development server will automatically try alternative ports
2. **API connection errors**: Ensure the Gateway Service is running on port 8000
3. **Token expiration**: Tokens expire after 24 hours - users will need to re-login

### Development Tips

- Use React DevTools for component debugging
- Enable Redux DevTools if using state management
- Check browser console for detailed error messages
- Use the Network tab to monitor API requests

## Contributing

1. Fork the repository
2. Create your feature branch
3. Ensure all tests pass
4. Follow the code style guidelines
5. Submit a pull request

## License

This project is licensed under the MIT License.