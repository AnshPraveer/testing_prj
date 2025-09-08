import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { userAPI, postAPI, followAPI, uploadAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Settings, Camera, UserPlus, UserMinus } from 'lucide-react';
import toast from 'react-hot-toast';

const Profile = () => {
  const { userId } = useParams();
  const { user: currentUser, updateUser } = useAuth();
  const queryClient = useQueryClient();
  const [showSettings, setShowSettings] = useState(false);
  const [editData, setEditData] = useState({
    username: '',
    bio: ''
  });

  const isOwnProfile = !userId || userId === currentUser?.id?.toString();
  const profileUserId = userId || currentUser?.id;

  // Fetch user profile
  const { data: profileUser, isLoading: userLoading } = useQuery(
    ['user', profileUserId],
    () => isOwnProfile ? userAPI.getProfile().then(res => res.data) : userAPI.getUserProfile(profileUserId).then(res => res.data),
    { enabled: !!profileUserId }
  );

  // Fetch user posts
  const { data: posts = [], isLoading: postsLoading } = useQuery(
    ['userPosts', profileUserId],
    () => isOwnProfile ? postAPI.getMyPosts().then(res => res.data) : postAPI.getUserPosts(profileUserId).then(res => res.data),
    { enabled: !!profileUserId }
  );

  // Fetch follow stats
  const { data: followStats } = useQuery(
    ['followStats', profileUserId],
    () => followAPI.getFollowStats(profileUserId).then(res => res.data),
    { enabled: !!profileUserId && !isOwnProfile }
  );

  // Follow/Unfollow mutation
  const followMutation = useMutation(
    (action) => action === 'follow' ? followAPI.followUser(profileUserId) : followAPI.unfollowUser(profileUserId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['followStats', profileUserId]);
        toast.success(followStats?.is_following ? 'Unfollowed successfully' : 'Following successfully');
      },
      onError: () => {
        toast.error('Failed to update follow status');
      }
    }
  );

  // Update profile mutation
  const updateProfileMutation = useMutation(
    (data) => userAPI.updateProfile(data),
    {
      onSuccess: (response) => {
        updateUser(response.data);
        queryClient.invalidateQueries(['user', profileUserId]);
        setShowSettings(false);
        toast.success('Profile updated successfully');
      },
      onError: () => {
        toast.error('Failed to update profile');
      }
    }
  );

  // Upload profile picture mutation
  const uploadProfilePicMutation = useMutation(
    (file) => uploadAPI.uploadProfilePicture(file),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['user', profileUserId]);
        toast.success('Profile picture updated');
      },
      onError: () => {
        toast.error('Failed to upload profile picture');
      }
    }
  );

  const handleFollow = () => {
    const action = followStats?.is_following ? 'unfollow' : 'follow';
    followMutation.mutate(action);
  };

  const handleProfilePictureChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      uploadProfilePicMutation.mutate(file);
    }
  };

  const handleUpdateProfile = (e) => {
    e.preventDefault();
    updateProfileMutation.mutate(editData);
  };

  React.useEffect(() => {
    if (profileUser && showSettings) {
      setEditData({
        username: profileUser.username || '',
        bio: profileUser.bio || ''
      });
    }
  }, [profileUser, showSettings]);

  if (userLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!profileUser) {
    return (
      <div className="profile-container">
        <div className="card">
          <div className="card-body" style={{ textAlign: 'center', padding: '40px' }}>
            <h3>User not found</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div style={{ position: 'relative' }}>
          {profileUser.profile_pic ? (
            <img 
              src={profileUser.profile_pic} 
              alt={profileUser.username} 
              className="profile-avatar"
            />
          ) : (
            <div className="profile-avatar" style={{ backgroundColor: '#0095f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '48px' }}>
              {profileUser.username?.charAt(0).toUpperCase()}
            </div>
          )}
          {isOwnProfile && (
            <label style={{ position: 'absolute', bottom: '0', right: '0', background: '#0095f6', color: 'white', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
              <Camera size={16} />
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleProfilePictureChange}
                style={{ display: 'none' }}
              />
            </label>
          )}
        </div>

        <div className="profile-info">
          <div className="profile-username">{profileUser.username}</div>
          
          <div className="profile-stats">
            <div className="profile-stat">
              <span className="profile-stat-number">{posts.length}</span> posts
            </div>
            <div className="profile-stat">
              <span className="profile-stat-number">{followStats?.followers_count || 0}</span> followers
            </div>
            <div className="profile-stat">
              <span className="profile-stat-number">{followStats?.following_count || 0}</span> following
            </div>
          </div>

          {profileUser.bio && (
            <div className="profile-bio">{profileUser.bio}</div>
          )}

          <div className="profile-actions">
            {isOwnProfile ? (
              <button 
                className="btn btn-secondary"
                onClick={() => setShowSettings(!showSettings)}
              >
                <Settings size={16} />
                Edit Profile
              </button>
            ) : (
              <button 
                className={`btn ${followStats?.is_following ? 'btn-secondary' : 'btn-primary'}`}
                onClick={handleFollow}
                disabled={followMutation.isLoading}
              >
                {followStats?.is_following ? (
                  <>
                    <UserMinus size={16} />
                    Unfollow
                  </>
                ) : (
                  <>
                    <UserPlus size={16} />
                    Follow
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {showSettings && isOwnProfile && (
        <div className="card">
          <div className="card-header">
            <h3>Edit Profile</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleUpdateProfile}>
              <div className="form-group">
                <label className="form-label">Username</label>
                <input
                  type="text"
                  value={editData.username}
                  onChange={(e) => setEditData({ ...editData, username: e.target.value })}
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Bio</label>
                <textarea
                  value={editData.bio}
                  onChange={(e) => setEditData({ ...editData, bio: e.target.value })}
                  className="form-textarea"
                />
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button type="submit" className="btn btn-primary" disabled={updateProfileMutation.isLoading}>
                  Save Changes
                </button>
                <button type="button" className="btn btn-secondary" onClick={() => setShowSettings(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="profile-posts">
        {postsLoading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : posts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', gridColumn: '1 / -1' }}>
            <h3>No posts yet</h3>
            <p style={{ color: '#8e8e8e', marginTop: '8px' }}>
              {isOwnProfile ? 'Share your first post!' : 'This user hasn\'t posted anything yet.'}
            </p>
          </div>
        ) : (
          posts.map((post) => (
            <div key={post.id} className="profile-post">
              <div style={{ padding: '16px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5' }}>
                <p style={{ textAlign: 'center', color: '#262626', fontSize: '14px' }}>
                  {post.content.length > 100 ? `${post.content.substring(0, 100)}...` : post.content}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Profile;