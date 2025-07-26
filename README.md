# 🌟 AURA JOURNAL

**Your Mindful Companion for Digital Journaling with AI-Powered Insights**

AURA Journal is a full-stack journaling application that combines the simplicity of personal reflection with the power of AI-driven sentiment analysis and topic extraction. Built with React Native (Expo) for cross-platform mobile experience and a robust Python FastAPI microservices backend.

## 🎯 Project Vision

Transform personal journaling into an insightful, data-driven experience that helps users understand their emotional patterns, track personal growth, and gain deeper self-awareness through intelligent text analysis.

## ✨ Key Features

### 📱 **Mobile Application (React Native + Expo)**
- **Cross-Platform**: iOS, Android, and Web support
- **Intuitive Interface**: Clean, mindful design focused on writing experience
- **Real-Time Insights**: Instant sentiment analysis and topic extraction
- **Entry History**: Browse and reflect on past journal entries
- **Offline-First**: Write entries even without internet connection

### 🧠 **AI-Powered Analysis**
- **Sentiment Analysis**: Understand emotional tone of your entries
- **Topic Extraction**: Automatically identify key themes and subjects
- **Trend Tracking**: Monitor emotional patterns over time
- **Google Cloud NLP**: Enterprise-grade natural language processing

### 🏗️ **Microservices Architecture**
- **Entry Ingestor**: Handles journal creation and storage
- **NLP Agent**: Provides intelligent text analysis
- **Dual Database**: PostgreSQL for structured data, MongoDB for analytics
- **Containerized**: Docker-ready for easy deployment

## 🛠️ Technology Stack

### **Frontend**
- **React Native** 0.79.5 with **Expo** ~53.0.20
- **Expo Router** for file-based navigation
- **TypeScript** for type safety
- **Lucide React Native** for beautiful icons
- **React Native Reanimated** for smooth animations

### **Backend**
- **FastAPI** for high-performance APIs
- **Python 3.11+** with modern async/await patterns
- **SQLAlchemy** for database ORM
- **Pydantic** for data validation
- **Google Cloud Natural Language API**

### **Databases**
- **PostgreSQL** for journal entries and user data
- **MongoDB** for analytics and insights storage

### **DevOps & Tools**
- **Docker & Docker Compose** for containerization
- **uv** for Python package management
- **pytest** for comprehensive testing
- **ruff** for code linting and formatting
- **GitHub Actions** for CI/CD

## 📁 Project Architecture

```
AURA-JOURNAL/
├── aura-journal-app/          # React Native mobile application
│   ├── app/                   # Expo Router pages
│   │   ├── (tabs)/           # Tab-based navigation
│   │   └── _layout.tsx       # Root layout
│   ├── src/                  # Application source code
│   │   ├── components/       # Reusable UI components
│   │   ├── screens/          # Screen components
│   │   └── services/         # API integration
│   ├── assets/               # Images, fonts, and static files
│   └── components/           # Expo-generated components
│
└── backend/                   # Python FastAPI microservices
    ├── services/
    │   ├── entry_ingestor/   # Journal entry management service
    │   └── nlp_agent/        # Text analysis service
    ├── shared/               # Common utilities and schemas
    ├── tests/                # Integration tests
    └── scripts/              # Development utilities
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.11+
- **Docker** and **Docker Compose**
- **Expo CLI**: `npm install -g @expo/cli`
- **Google Cloud Account** (for NLP features)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd AURA-JOURNAL
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
uv sync --extra dev --extra gcp

# Configure environment
cp .env.example .env
# Edit .env with your database URLs and GCP credentials

# Start services with Docker
docker-compose up --build
```

### 3. Mobile App Setup
```bash
cd aura-journal-app

# Install dependencies
npm install

# Start development server
npx expo start
```

### 4. Access the Application
- **Mobile App**: Scan QR code with Expo Go app
- **Backend APIs**: 
  - Entry Ingestor: http://localhost:8000
  - NLP Agent: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs

## 🔧 Development Workflow

### **Backend Development**
```bash
# Run tests
python scripts/run_tests.py

# Start individual services
python scripts/run_service.py entry-ingestor
python scripts/run_service.py nlp-agent

# Code quality
ruff check --fix .
ruff format .
mypy shared/ services/
```

### **Frontend Development**
```bash
# Development server
npx expo start

# Platform-specific builds
npx expo start --ios
npx expo start --android
npx expo start --web

# Code quality
npm run lint
```

## 📊 API Endpoints

### **Entry Ingestor Service** (Port 8000)

#### Create Journal Entry
```http
POST /entries
Content-Type: application/json

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "Today was a wonderful day filled with gratitude and joy!"
}
```

**Response:**
```json
{
  "entry_id": "456e7890-e89b-12d3-a456-426614174001",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-01-25T10:30:00Z",
  "content": "Today was a wonderful day filled with gratitude and joy!",
  "analysis": {
    "sentiment": {
      "label": "POSITIVE",
      "score": 0.92
    },
    "topics": ["gratitude", "joy", "wellbeing"]
  }
}
```

### **NLP Agent Service** (Port 8001)

#### Analyze Text
```http
POST /analyze
Content-Type: application/json

{
  "text": "I'm feeling anxious about tomorrow's presentation."
}
```

**Response:**
```json
{
  "sentiment": {
    "label": "NEGATIVE",
    "score": 0.73
  },
  "topics": ["anxiety", "presentation", "work"]
}
```

## 🧪 Testing Strategy

### **Comprehensive Test Coverage**
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint validation
- **Contract Tests**: Service communication verification
- **Mocked External Services**: Isolated testing environment

### **Running Tests**
```bash
# All tests
python scripts/run_tests.py

# Specific test types
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --service entry-ingestor

# With coverage
python scripts/run_tests.py --coverage
```

## 🔒 Security & Privacy

### **Data Protection**
- **Local Storage**: Sensitive data encrypted at rest
- **API Security**: JWT authentication (planned)
- **Database Security**: Connection encryption and access controls
- **Privacy First**: User data never shared with third parties

### **Environment Configuration**
```bash
# Required environment variables
DATABASE_URL=postgresql://user:password@localhost:5432/aura_journal
MONGODB_URL=mongodb://localhost:27017
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json
NLP_AGENT_URL=http://localhost:8001/analyze
```

## 📈 Performance & Scalability

### **Backend Optimizations**
- **Async/Await**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Microservices**: Independent scaling of components
- **Caching**: Redis integration (planned)

### **Frontend Optimizations**
- **Lazy Loading**: Components loaded on demand
- **Offline Support**: Local data persistence
- **Optimistic Updates**: Immediate UI feedback
- **Image Optimization**: Compressed assets

## 🚢 Deployment

### **Docker Deployment**
```bash
# Production build
docker-compose -f docker-compose.prod.yml up --build

# Individual services
docker build -t aura-entry-ingestor backend/services/entry_ingestor/
docker build -t aura-nlp-agent backend/services/nlp_agent/
```

### **Mobile App Deployment**
```bash
# Build for production
npx expo build:ios
npx expo build:android

# Publish to Expo
npx expo publish
```

## 🔮 Roadmap

### **Phase 1: Core Features** ✅
- [x] Basic journaling functionality
- [x] Sentiment analysis integration
- [x] Topic extraction
- [x] Entry history

### **Phase 2: Enhanced Analytics** 🚧
- [ ] Mood tracking over time
- [ ] Weekly/monthly insights
- [ ] Export functionality
- [ ] Search and filtering

### **Phase 3: Social Features** 📋
- [ ] Shared insights (anonymous)
- [ ] Community challenges
- [ ] Therapist integration
- [ ] Goal tracking

### **Phase 4: Advanced AI** 🔮
- [ ] Personalized recommendations
- [ ] Predictive mood analysis
- [ ] Custom AI models
- [ ] Voice-to-text journaling

## 🤝 Contributing

### **Development Guidelines**
1. **Code Style**: Follow existing patterns and linting rules
2. **Testing**: Write tests for all new functionality
3. **Documentation**: Update README for significant changes
4. **Architecture**: Use dependency injection and clean patterns

### **Getting Started**
```bash
# Fork the repository
git fork <repository-url>

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
python scripts/run_tests.py
npm run lint

# Submit pull request
git push origin feature/amazing-feature
```

## 📚 Resources & Documentation

### **Technical Documentation**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [Google Cloud NLP API](https://cloud.google.com/natural-language/docs)

### **Architecture Patterns**
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Microservices Patterns](https://microservices.io/)
- [API Design Best Practices](https://restfulapi.net/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud Platform** for powerful NLP capabilities
- **Expo Team** for excellent React Native tooling
- **FastAPI Community** for the amazing web framework
- **Open Source Contributors** who make projects like this possible

---

**Built with ❤️ for mindful journaling and personal growth**

*AURA Journal - Where technology meets mindfulness*