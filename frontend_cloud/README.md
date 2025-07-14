# SmartSecurity Cloud - Customer Portal

A modern Vue 3 customer portal for SmartSecurity Solutions, allowing end-users to monitor their IoT devices, view live and historical sensor data, and manage their profiles.

## Features

- **Dashboard Overview**: KPI tiles showing online devices, alerts, and recent activity
- **Device Management**: List, search, and filter devices with real-time status
- **Live Monitoring**: Real-time WebSocket data streaming with interactive charts
- **Historical Data**: Date-range picker for historical sensor data analysis
- **User Profile**: Account management and password changes
- **Support Portal**: Documentation links and ticket submission

## Tech Stack

- **Frontend**: Vue 3 with Composition API
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **Styling**: Tailwind CSS
- **Charts**: ApexCharts with Vue 3 wrapper
- **HTTP Client**: Axios
- **Build Tool**: Vite

## Project Structure

```
frontend_cloud/
├── src/
│   ├── components/          # Reusable Vue components
│   ├── views/              # Page components
│   │   ├── LoginView.vue
│   │   ├── Overview.vue
│   │   ├── Devices.vue
│   │   ├── Live.vue
│   │   ├── History.vue
│   │   ├── Profile.vue
│   │   └── Support.vue
│   ├── stores/             # Pinia stores
│   │   ├── auth.js         # Authentication state
│   │   ├── devices.js      # Device management
│   │   └── sensor.js       # Sensor data handling
│   ├── router/             # Vue Router configuration
│   ├── App.vue             # Root component
│   ├── main.js             # Application entry point
│   └── style.css           # Global styles
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
├── Dockerfile              # Docker build configuration
└── nginx.conf              # Nginx server configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## API Integration

The frontend integrates with the SmartSecurity API backend:

### Authentication
- JWT-based authentication
- Token storage in localStorage
- Automatic token refresh

### Endpoints Used
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/users/me` - Get user profile
- `PUT /api/v1/users/me/password` - Change password
- `GET /api/v1/devices/` - List user's devices
- `GET /api/v1/devices/{id}/sensor-data` - Get sensor history
- `WS /ws/live/{device_id}` - Live sensor data stream

### Tenant Isolation
All API calls are automatically filtered by the user's tenant ID, ensuring data isolation between customers.

## WebSocket Integration

Real-time data is handled through WebSocket connections:

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/live/${deviceId}?token=${token}`)

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  sensorStore.pushLiveData(data)
}
```

## State Management

### Auth Store
- User authentication state
- Token management
- Login/logout functions

### Device Store
- Device list management
- Device filtering and search
- Current device selection

### Sensor Store
- Historical sensor data
- Live data streaming
- Chart data formatting

## Styling

The application uses Tailwind CSS for styling with custom components:

```css
.btn-primary {
  @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors;
}

.card {
  @apply bg-white rounded-lg shadow-md p-6;
}
```

## Deployment

### Docker

Build and run with Docker:

```bash
docker build -t frontend-cloud .
docker run -p 80:80 frontend-cloud
```

### Nginx Configuration

The included `nginx.conf` handles:
- Static file serving
- API proxy to backend
- WebSocket proxy
- Client-side routing
- Security headers

## Development

### Code Style
- Use Vue 3 Composition API
- Follow Vue 3 best practices
- Use TypeScript for better type safety (optional)

### Testing
- Unit tests with Vitest
- Component testing with Vue Test Utils
- E2E testing with Playwright (planned)

## Security

- JWT token authentication
- HTTPS enforcement in production
- CORS configuration
- XSS protection headers
- Content Security Policy

## Performance

- Lazy-loaded route components
- Optimized bundle splitting
- Gzip compression
- CDN-ready static assets

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary to SmartSecurity Solutions. 