import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    
    // Handle FastAPI validation errors
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        // Convert validation error array to readable string
        const errorMessages = error.response.data.detail.map(err => 
          `${err.loc?.join(' -> ') || 'Field'}: ${err.msg || 'Invalid value'}`
        ).join(', ');
        error.message = errorMessages;
      } else if (typeof error.response.data.detail === 'string') {
        error.message = error.response.data.detail;
      }
    }
    
    // Log detailed error information for debugging
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    return Promise.reject(error);
  }
);

// API Services
export const authAPI = {
  login: (email, password) => {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    return api.post('/auth/login', formData);
  },
  
  register: (userData) => {
    const formData = new FormData();
    Object.keys(userData).forEach(key => {
      formData.append(key, userData[key]);
    });
    return api.post('/auth/register', formData);
  }
};

export const userAPI = {
  getProfile: () => api.get('/users/me'),
  getUserProfile: (userId) => api.get(`/users/${userId}`),
  getAllUsers: () => api.get('/users/all'),
  updateProfile: (data) => api.put('/users/me', data),
  updatePassword: (data) => api.put('/users/password', data),
  deleteAccount: () => api.delete('/users/me')
};

export const postAPI = {
  getAllPosts: (skip = 0, limit = 20) => api.get(`/posts/?skip=${skip}&limit=${limit}`),
  getPost: (postId) => api.get(`/posts/${postId}`),
  getUserPosts: (userId, skip = 0, limit = 20) => api.get(`/posts/user/${userId}?skip=${skip}&limit=${limit}`),
  getMyPosts: (skip = 0, limit = 20) => api.get(`/posts/me?skip=${skip}&limit=${limit}`),
  createPost: (data) => api.post('/posts/', data),
  updatePost: (postId, data) => api.put(`/posts/${postId}`, data),
  deletePost: (postId) => api.delete(`/posts/${postId}`)
};

export const commentAPI = {
  getPostComments: (postId, skip = 0, limit = 50) => api.get(`/comments/post/${postId}?skip=${skip}&limit=${limit}`),
  getMyComments: (skip = 0, limit = 50) => api.get(`/comments/me?skip=${skip}&limit=${limit}`),
  createComment: (postId, data) => api.post(`/comments/post/${postId}`, data),
  updateComment: (commentId, data) => api.put(`/comments/${commentId}`, data),
  deleteComment: (commentId) => api.delete(`/comments/${commentId}`)
};

export const likeAPI = {
  toggleLike: (postId) => api.post(`/likes/post/${postId}`),
  getPostLikes: (postId, skip = 0, limit = 50) => api.get(`/likes/post/${postId}?skip=${skip}&limit=${limit}`),
  getPostLikesCount: (postId) => api.get(`/likes/post/${postId}/count`),
  getMyLikes: (skip = 0, limit = 50) => api.get(`/likes/me?skip=${skip}&limit=${limit}`)
};

export const followAPI = {
  followUser: (userId) => api.post(`/follow/${userId}`),
  unfollowUser: (userId) => api.delete(`/follow/${userId}`),
  getFollowers: (userId, skip = 0, limit = 50) => api.get(`/follow/followers/${userId}?skip=${skip}&limit=${limit}`),
  getFollowing: (userId, skip = 0, limit = 50) => api.get(`/follow/following/${userId}?skip=${skip}&limit=${limit}`),
  getMyFollowers: (skip = 0, limit = 50) => api.get(`/follow/my-followers?skip=${skip}&limit=${limit}`),
  getMyFollowing: (skip = 0, limit = 50) => api.get(`/follow/my-following?skip=${skip}&limit=${limit}`),
  getFollowStats: (userId) => api.get(`/follow/stats/${userId}`)
};

export const storyAPI = {
  getActiveStories: (skip = 0, limit = 50) => api.get(`/stories/?skip=${skip}&limit=${limit}`),
  getUserStories: (userId, skip = 0, limit = 20) => api.get(`/stories/user/${userId}?skip=${skip}&limit=${limit}`),
  getMyStories: (skip = 0, limit = 20) => api.get(`/stories/me?skip=${skip}&limit=${limit}`),
  getStory: (storyId) => api.get(`/stories/${storyId}`),
  createStory: (data) => api.post('/stories/', data),
  deleteStory: (storyId) => api.delete(`/stories/${storyId}`)
};

export const uploadAPI = {
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  uploadVideo: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  uploadProfilePicture: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/profile-picture', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};