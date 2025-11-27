import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (email, password) => 
    api.post('/auth/register', { email, password }),
  
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  getProfile: () => 
    api.get('/auth/me'),
};

export const comicsAPI = {
  getComics: (skip = 0, limit = 100) => 
    api.get(`/comics?skip=${skip}&limit=${limit}`),
  
  getComic: (id) => 
    api.get(`/comics/${id}`),
  
  createComic: (comic) => 
    api.post('/comics', comic),
};

export const ratingsAPI = {
  createRating: (comicId, rating) => 
    api.post('/ratings', { comic_id: comicId, rating }),
  
  getUserRatings: () => 
    api.get('/ratings'),
  
  getUserRatingForComic: (comicId) => 
    api.get(`/ratings/${comicId}`),
};

export const recommendationsAPI = {
  getRecommendations: (limit = 5) => 
    api.get(`/recommendations?limit=${limit}`),
};

export default api;