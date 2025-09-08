import React from 'react';
import { useQuery } from 'react-query';
import { postAPI, userAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import Post from '../components/Post';
import { Users, TrendingUp } from 'lucide-react';

const Home = () => {
  const { isAuthenticated } = useAuth();
  
  const { data: posts = [], isLoading: postsLoading, error: postsError } = useQuery(
    'posts',
    () => postAPI.getAllPosts().then(res => res.data),
    {
      retry: 1,
      enabled: isAuthenticated, // Only run when authenticated
      onError: (error) => {
        console.error('Failed to fetch posts:', error);
      }
    }
  );

  const { data: users = [], error: usersError } = useQuery(
    'allUsers',
    () => userAPI.getAllUsers().then(res => res.data),
    {
      retry: 1,
      enabled: isAuthenticated, // Only run when authenticated
      onError: (error) => {
        console.error('Failed to fetch users:', error);
      }
    }
  );

  // Safe render helper to prevent objects from being rendered
  const safeRender = (value, fallback = '') => {
    if (value === null || value === undefined) return fallback;
    if (typeof value === 'object') return fallback;
    return String(value);
  };

  if (postsLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="feed">
        {posts.length === 0 ? (
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center', padding: '40px' }}>
              <h3>No posts yet</h3>
              <p style={{ color: '#8e8e8e', marginTop: '8px' }}>
                Start following people or create your first post!
              </p>
            </div>
          </div>
        ) : (
          posts.map((post) => (
            <Post key={post.id} post={post} />
          ))
        )}
      </div>

      <div className="sidebar">
        <div className="card">
          <div className="card-header">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <Users size={20} />
              Suggested Users
            </h3>
          </div>
          <div className="card-body">
            {users.slice(0, 5).map((user) => (
              <div key={user.id} style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                {user.profile_pic ? (
                  <img 
                    src={user.profile_pic} 
                    alt={user.username} 
                    className="avatar avatar-sm"
                  />
                ) : (
                  <div className="avatar avatar-sm" style={{ backgroundColor: '#0095f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '12px' }}>
                    {user.username?.charAt(0).toUpperCase()}
                  </div>
                )}
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '600', fontSize: '14px' }}>{safeRender(user.username, 'Unknown User')}</div>
                  <div style={{ fontSize: '12px', color: '#8e8e8e' }}>{safeRender(user.Name, '')}</div>
                </div>
                <button className="btn btn-primary" style={{ fontSize: '12px', padding: '4px 12px' }}>
                  Follow
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <TrendingUp size={20} />
              Trending
            </h3>
          </div>
          <div className="card-body">
            <div style={{ color: '#8e8e8e', textAlign: 'center', padding: '20px' }}>
              No trending topics yet
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;