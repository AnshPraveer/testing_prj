// Utility functions for handling errors safely

export const safeRender = (value, fallback = '') => {
  if (value === null || value === undefined) return fallback;
  if (typeof value === 'object') {
    // If it's an error object with message, return the message
    if (value.message) return String(value.message);
    // If it's a validation error array, format it
    if (Array.isArray(value)) {
      return value.map(err => 
        `${err.loc?.join(' -> ') || 'Field'}: ${err.msg || 'Invalid value'}`
      ).join(', ');
    }
    return fallback;
  }
  return String(value);
};

export const formatError = (error) => {
  if (typeof error === 'string') return error;
  if (error?.message) return error.message;
  if (error?.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map(err => 
        `${err.loc?.join(' -> ') || 'Field'}: ${err.msg || 'Invalid value'}`
      ).join(', ');
    }
  }
  return 'An unexpected error occurred';
};

export const safeStringify = (obj) => {
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
};