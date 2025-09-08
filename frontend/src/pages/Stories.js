import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { storyAPI, uploadAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Plus, Clock, User } from 'lucide-react';
import toast from 'react-hot-toast';

const Stories = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [uploading, setUploading] = useState(false);

  // Fetch active stories
  const { data: stories = [], isLoading } = useQuery(
    'activeStories',
    () => storyAPI.getActiveStories().then(res => res.data),
    { enabled: !!user } // Only run when authenticated
  );

  // Fetch my stories
  const { data: myStories = [] } = useQuery(
    'myStories',
    () => storyAPI.getMyStories().then(res => res.data),
    { enabled: !!user } // Only run when authenticated
  );

  // Create story mutation
  const createStoryMutation = useMutation(
    (storyData) => storyAPI.createStory(storyData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('activeStories');
        queryClient.invalidateQueries('myStories');
        setShowCreateForm(false);
        setSelectedFile(null);
        setPreviewUrl('');
        toast.success('Story created successfully!');
      },
      onError: () => {
        toast.error('Failed to create story');
      }
    }
  );

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCreateStory = async () => {
    if (!selectedFile) {
      toast.error('Please select an image');
      return;
    }

    setUploading(true);
    try {
      // Upload image first
      const uploadResponse = await uploadAPI.uploadImage(selectedFile);
      
      // Create story with uploaded image URL
      createStoryMutation.mutate({
        content_url: uploadResponse.data.file_url
      });
    } catch (error) {
      toast.error('Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const formatTimeRemaining = (expireAt) => {
    const now = new Date();
    const expiry = new Date(expireAt);
    const diffInHours = Math.floor((expiry - now) / (1000 * 60 * 60));
    
    if (diffInHours <= 0) return 'Expired';
    if (diffInHours < 1) return 'Less than 1h';
    return `${diffInHours}h remaining`;
  };

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="stories-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1>Stories</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          <Plus size={16} />
          Create Story
        </button>
      </div>

      {showCreateForm && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <h3>Create New Story</h3>
          </div>
          <div className="card-body">
            {!selectedFile ? (
              <label className="file-upload">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                />
                <Plus size={32} color="#8e8e8e" />
                <div className="upload-text">
                  Click to upload an image for your story
                </div>
              </label>
            ) : (
              <div>
                <img 
                  src={previewUrl} 
                  alt="Story preview" 
                  style={{ width: '100%', maxWidth: '300px', borderRadius: '8px', marginBottom: '16px' }}
                />
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button 
                    className="btn btn-primary"
                    onClick={handleCreateStory}
                    disabled={uploading || createStoryMutation.isLoading}
                  >
                    {uploading ? 'Uploading...' : createStoryMutation.isLoading ? 'Creating...' : 'Share Story'}
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl('');
                      setShowCreateForm(false);
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {myStories.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <h2 style={{ marginBottom: '16px' }}>My Stories</h2>
          <div className="stories-grid">
            {myStories.map((story) => (
              <div key={story.id} className="story-card">
                <img 
                  src={story.content_url} 
                  alt="My story" 
                  className="story-image"
                />
                <div className="story-info">
                  <div className="story-user">
                    <User size={16} />
                    <span>You</span>
                  </div>
                  <div className="story-time">
                    <Clock size={12} />
                    {formatTimeRemaining(story.expire_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 style={{ marginBottom: '16px' }}>All Stories</h2>
        {stories.length === 0 ? (
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center', padding: '40px' }}>
              <h3>No active stories</h3>
              <p style={{ color: '#8e8e8e', marginTop: '8px' }}>
                Be the first to share a story!
              </p>
            </div>
          </div>
        ) : (
          <div className="stories-grid">
            {stories.map((story) => (
              <div key={story.id} className="story-card">
                <img 
                  src={story.content_url} 
                  alt={`${story.user?.username}'s story`} 
                  className="story-image"
                />
                <div className="story-info">
                  <div className="story-user">
                    {story.user?.profile_pic ? (
                      <img 
                        src={story.user.profile_pic} 
                        alt={story.user.username} 
                        className="avatar avatar-sm"
                        style={{ width: '16px', height: '16px' }}
                      />
                    ) : (
                      <User size={16} />
                    )}
                    <span>{story.user?.username}</span>
                  </div>
                  <div className="story-time">
                    <Clock size={12} />
                    {formatTimeRemaining(story.expire_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Stories;