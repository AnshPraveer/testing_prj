import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Heart, MessageCircle, Share, MoreHorizontal } from 'lucide-react';
import { likeAPI, commentAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const Post = ({ post }) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showComments, setShowComments] = useState(false);
  const [commentText, setCommentText] = useState('');

  // Fetch like status and count
  const { data: likeData, error: likeError } = useQuery(
    ['postLikes', post.id],
    () => likeAPI.getPostLikesCount(post.id).then(res => res.data),
    { 
      enabled: !!post.id && !!user, // Only run when authenticated and post exists
      retry: 1,
      onError: (error) => {
        console.error('Failed to fetch likes:', error);
      }
    }
  );

  // Fetch comments
  const { data: comments = [] } = useQuery(
    ['postComments', post.id],
    () => commentAPI.getPostComments(post.id).then(res => res.data),
    { enabled: showComments && !!user } // Only run when authenticated and comments are shown
  );

  // Like mutation
  const likeMutation = useMutation(
    () => likeAPI.toggleLike(post.id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['postLikes', post.id]);
      },
      onError: () => {
        toast.error('Failed to update like');
      }
    }
  );

  // Comment mutation
  const commentMutation = useMutation(
    (content) => commentAPI.createComment(post.id, { content }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['postComments', post.id]);
        setCommentText('');
        toast.success('Comment added');
      },
      onError: () => {
        toast.error('Failed to add comment');
      }
    }
  );

  const handleLike = () => {
    likeMutation.mutate();
  };

  const handleComment = (e) => {
    e.preventDefault();
    if (commentText.trim()) {
      commentMutation.mutate(commentText.trim());
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
      
      if (diffInHours < 1) return 'Just now';
      if (diffInHours < 24) return `${diffInHours}h ago`;
      if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
      return date.toLocaleDateString();
    } catch (error) {
      return 'Unknown';
    }
  };

  // Safe render helper to prevent objects from being rendered
  const safeRender = (value, fallback = '') => {
    if (value === null || value === undefined) return fallback;
    if (typeof value === 'object') return fallback;
    return String(value);
  };

  return (
    <div className="post">
      <div className="post-header">
        {post.creator?.profile_pic ? (
          <img 
            src={post.creator.profile_pic} 
            alt={post.creator.username} 
            className="avatar"
          />
        ) : (
          <div className="avatar" style={{ backgroundColor: '#0095f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
            {post.creator?.username?.charAt(0).toUpperCase()}
          </div>
        )}
        <div className="post-user-info">
          <Link to={`/profile/${post.creator?.id}`} className="post-username">
            {safeRender(post.creator?.username, 'Unknown User')}
          </Link>
          <div className="post-time">{formatDate(post.created_at)}</div>
        </div>
        <button className="post-action">
          <MoreHorizontal size={20} />
        </button>
      </div>

      <div className="post-content">
        {safeRender(post.content, 'No content')}
      </div>

      <div className="post-actions">
        <button 
          className={`post-action ${likeData?.user_liked ? 'liked' : ''}`}
          onClick={handleLike}
          disabled={likeMutation.isLoading}
        >
          <Heart size={20} fill={likeData?.user_liked ? 'currentColor' : 'none'} />
          <span>{likeData?.likes_count || 0}</span>
        </button>
        
        <button 
          className="post-action"
          onClick={() => setShowComments(!showComments)}
        >
          <MessageCircle size={20} />
          <span>{comments.length}</span>
        </button>
        
        <button className="post-action">
          <Share size={20} />
        </button>
      </div>

      {showComments && (
        <div className="comments-section">
          {comments.map((comment) => (
            <div key={comment.id} className="comment">
              {comment.user?.profile_pic ? (
                <img 
                  src={comment.user.profile_pic} 
                  alt={comment.user.username} 
                  className="avatar avatar-sm"
                />
              ) : (
                <div className="avatar avatar-sm" style={{ backgroundColor: '#0095f6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '12px' }}>
                  {comment.user?.username?.charAt(0).toUpperCase()}
                </div>
              )}
              <div className="comment-content">
                <div>
                  <span className="comment-username">{safeRender(comment.user?.username, 'Unknown User')}</span>
                  <span className="comment-text">{safeRender(comment.content, '')}</span>
                </div>
                <div className="comment-time">{formatDate(comment.created_at)}</div>
              </div>
            </div>
          ))}
          
          <form onSubmit={handleComment} className="comment-form">
            <input
              type="text"
              placeholder="Add a comment..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              className="comment-input"
            />
            <button 
              type="submit" 
              className="comment-submit"
              disabled={!commentText.trim() || commentMutation.isLoading}
            >
              Post
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Post;