import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="card">
            <div className="card-body" style={{ textAlign: 'center', padding: '40px' }}>
              <h3>Something went wrong</h3>
              <p style={{ color: '#8e8e8e', marginTop: '8px' }}>
                Please refresh the page or try again later.
              </p>
              <button 
                className="btn btn-primary" 
                onClick={() => window.location.reload()}
                style={{ marginTop: '16px' }}
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;