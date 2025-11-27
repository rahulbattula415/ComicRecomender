<div align="center">

# 🦸 Comic Recommender

### Discover your next favorite comic with AI-powered recommendations

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)

**A modern full-stack web application that provides personalized comic book recommendations using machine learning.**

[Getting Started](#-getting-started) · [Features](#-features) · [Tech Stack](#-tech-stack) · [API Reference](#-api-reference)

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Getting Started](#-getting-started)
- [Tech Stack](#-tech-stack)
- [API Reference](#-api-reference)
- [How It Works](#-how-it-works)
- [Development](#-development)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 About

Comic Recommender is a full-stack platform that helps comic book enthusiasts discover new titles based on their reading preferences. Using content-based filtering and machine learning algorithms, the platform analyzes your ratings and suggests comics that match your taste.

### Key Highlights

- 🎨 **Modern UI** - Beautiful, responsive interface built with React and TailwindCSS
- 🤖 **Smart AI** - Content-based filtering using TF-IDF and cosine similarity
- 🔒 **Secure** - JWT authentication with encrypted password storage
- 🚀 **Fast** - Optimized performance with FastAPI and PostgreSQL
- 🐳 **Easy Setup** - One-command deployment with Docker Compose

---

## ✨ Features

### For Users
- 📚 Browse extensive Marvel and DC comic collections
- ⭐ Rate comics on a 5-star scale
- 🎯 Get personalized AI-powered recommendations
- 📊 Track your reading history and preferences
- 🔍 Search and filter comics by genre and characters

### For Developers
- 🔐 JWT-based authentication system
- 📡 RESTful API with comprehensive documentation
- 🗄️ PostgreSQL database with SQLAlchemy ORM
- 🐳 Docker containerization for easy deployment
- 📚 Interactive API docs with Swagger UI

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- [Git](https://git-scm.com/downloads)

### Quick Start (Docker - Recommended)

```bash
# Clone the repository
git clone https://github.com/rahulbattula415/ComicRecomender.git
cd ComicRecomender

# Start all services
docker-compose up --build
```

🎉 That's it! The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### First Steps

1. Open http://localhost:3000 in your browser
2. Create an account by clicking "Register"
3. Browse the comic collection
4. Rate at least 3-5 comics (give 4-5 stars to comics you like)
5. Visit the "Recommendations" page to see personalized suggestions!

---

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI library with hooks
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Router v6** - Client-side routing
- **Context API** - State management

### Backend
- **FastAPI** - High-performance Python framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **PostgreSQL** - Relational database
- **JWT** - Authentication
- **scikit-learn** - ML algorithms
- **Uvicorn** - ASGI server

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **PostgreSQL** - Database with persistent volumes

---

## 📡 API Reference

### Authentication

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/auth/register` | POST | Register new user | No |
| `/api/auth/login` | POST | Login user | No |
| `/api/auth/me` | GET | Get current user | Yes |

### Comics

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/comics` | GET | List all comics | No |
| `/api/comics/{id}` | GET | Get comic details | No |
| `/api/comics` | POST | Create new comic | Yes |

### Ratings

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/ratings` | POST | Rate a comic | Yes |
| `/api/ratings` | GET | Get user ratings | Yes |
| `/api/ratings/{comic_id}` | GET | Get specific rating | Yes |

### Recommendations

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/recommendations` | GET | Get AI recommendations | Yes |

> 📚 **Full API Documentation**: Visit http://localhost:8000/docs for interactive Swagger UI

---

## 🧠 How It Works

The recommendation engine uses **content-based filtering** to suggest comics similar to ones you've rated highly:

### Algorithm Pipeline

```
User Ratings (4-5 ⭐) → Feature Extraction → TF-IDF Vectorization → 
Cosine Similarity → Ranked Results → Top 5 Recommendations
```

### Process

1. **Data Collection** - Gathers comics you rated 4-5 stars
2. **Feature Extraction** - Combines description, characters, and genre
3. **Vectorization** - Converts text to numerical vectors using TF-IDF
4. **Similarity Calculation** - Finds similar comics using cosine similarity
5. **Ranking** - Returns top 5 most similar comics with scores

### Why Content-Based Filtering?

- ✅ Personalized to your specific tastes
- ✅ Works without large user base (no cold start problem)
- ✅ Explainable recommendations
- ✅ No bias from other users' ratings

---

## 💻 Development

### Manual Setup (Without Docker)

<details>
<summary><b>Backend Setup</b></summary>

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with:
# DATABASE_URL=postgresql://user:password@localhost/comic_recommender
# SECRET_KEY=your-secret-key-change-in-production
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30

# Create PostgreSQL database
createdb comic_recommender

# Initialize database
python -c "from app.core.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Seed database with comics
python fetch_flexible_comics.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at http://localhost:8000

</details>

<details>
<summary><b>Frontend Setup</b></summary>

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be running at http://localhost:3000

</details>

### Project Structure

```
ComicRecomender/
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── contexts/     # React contexts
│   │   └── services/     # API services
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Comics table
CREATE TABLE comics (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    characters TEXT[],
    genre VARCHAR,
    image_url VARCHAR,
    external_id VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User ratings table
CREATE TABLE user_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    comic_id INTEGER REFERENCES comics(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, comic_id)
);
```

---

## 🗺️ Roadmap

### Current Features
- ✅ User authentication and authorization
- ✅ Comic browsing and search
- ✅ Rating system
- ✅ AI-powered recommendations
- ✅ Responsive design
- ✅ Docker deployment

### Coming Soon
- [ ] Advanced search with filters
- [ ] User profiles and reading lists
- [ ] Social features (follow, share)
- [ ] Comic reading history analytics
- [ ] Dark mode
- [ ] Mobile app (React Native)
- [ ] OpenAI embeddings for better recommendations
- [ ] Redis caching for performance

### Ideas
- Community reviews and discussions
- Comic release notifications
- Reading challenges and achievements
- Integration with comic reading platforms

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write clear, descriptive commit messages
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Keep PRs focused on a single feature/fix

### Found a Bug?

[Open an issue](https://github.com/rahulbattula415/ComicRecomender/issues/new) and include:
- Clear bug description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, browser, etc.)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [ComicVine API](https://comicvine.gamespot.com/api/) for comic data
- [Marvel](https://www.marvel.com/) and [DC Comics](https://www.dc.com/) for amazing characters
- [Heroicons](https://heroicons.com/) for beautiful icons
- Open source community for inspiration

---

<div align="center">

**Made with ❤️ by [Rahul Battula](https://github.com/rahulbattula415)**

[![GitHub Stars](https://img.shields.io/github/stars/rahulbattula415/ComicRecomender?style=social)](https://github.com/rahulbattula415/ComicRecomender/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/rahulbattula415/ComicRecomender?style=social)](https://github.com/rahulbattula415/ComicRecomender/network/members)

[⭐ Star this repo](https://github.com/rahulbattula415/ComicRecomender) · [🐛 Report Bug](https://github.com/rahulbattula415/ComicRecomender/issues) · [✨ Request Feature](https://github.com/rahulbattula415/ComicRecomender/issues)

</div>
