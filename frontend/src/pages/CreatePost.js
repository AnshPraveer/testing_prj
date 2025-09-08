import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from 'react-query';
import { postAPI, uploadAPI } from '../services/api';
import { Upload, Image, X } from 'lucide-react';
import toast from 'react-hot-toast';

const CreatePost = () => {
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const createPostMutation = useMutation(
    (postData) => postAPI.createPost(postData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('posts');
        toast.success('Post created successfully!');
        navigate('/');
      },
      onError: () => {
        toast.error('Failed to create post');
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

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setPreviewUrl('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!content.trim()) {
      toast.error('Please enter some content');
      return;
    }

    let postContent = content;

    // Upload file if selected
    if (selectedFile) {
      setUploading(true);
      try {
        const uploadResponse = await uploadAPI.uploadImage(selectedFile);
        postContent += `\n\nImage: ${uploadResponse.data.file_url}`;
      } catch (error) {
        toast.error('Failed to upload image');
        setUploading(false);
        return;
      }
      setUploading(false);
    }

    createPostMutation.mutate({ content: postContent });
  };

  return (
    <div className="create-post-container">
      <div className="create-post-form">
        <h1 className="create-post-title">Create New Post</h1>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">What's on your mind?</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="form-textarea"
              placeholder="Share your thoughts..."
              rows="4"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Add Image (Optional)</label>
            {!selectedFile ? (
              <label className="file-upload">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                />
                <Upload size={32} color="#8e8e8e" />
                <div className="upload-text">
                  Click to upload an image
                </div>
              </label>
            ) : (
              <div style={{ position: 'relative' }}>
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="image-preview"
                />
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  style={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    background: 'rgba(0, 0, 0, 0.5)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer'
                  }}
                >
                  <X size={16} />
                </button>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={() => navigate('/')}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={createPostMutation.isLoading || uploading}
            >
              {uploading ? 'Uploading...' : createPostMutation.isLoading ? 'Creating...' : 'Create Post'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePost;