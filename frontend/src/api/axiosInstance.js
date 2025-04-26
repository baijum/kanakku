import axios from 'axios';

// Get the API URL from environment variable, fallback to relative path for development
const apiBaseUrl = process.env.REACT_APP_API_URL || '/';

// Create an Axios instance
const axiosInstance = axios.create({
  baseURL: apiBaseUrl, // Will use REACT_APP_API_URL in production, relative path in development
  withCredentials: true, // Send cookies for CSRF
});

// Store the CSRF token
let csrfToken = null;

// Function to fetch a CSRF token
const fetchCsrfToken = async () => {
  if (csrfToken) return csrfToken;
  
  try {
    // Use direct axios here (not axiosInstance) to avoid circular dependencies
    const response = await axios.get(`${apiBaseUrl}api/v1/csrf-token`, { 
      withCredentials: true,
      headers: {
        // Add Authorization header if token exists - we need this even for CSRF token fetching
        ...(localStorage.getItem('token') ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {})
      }
    });
    
    // Check for token in response body
    if (response.data && response.data.csrf_token) {
      csrfToken = response.data.csrf_token;
      console.log('CSRF token fetched from response JSON');
      return csrfToken;
    } 
    // Check response headers for token
    else if (response.headers && response.headers['x-csrftoken']) {
      csrfToken = response.headers['x-csrftoken'];
      console.log('CSRF token fetched from response headers');
      return csrfToken;
    }
    // Check cookies for token
    else {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrf_token=')) {
          csrfToken = cookie.substring('csrf_token='.length, cookie.length);
          console.log('CSRF token fetched from cookies');
          return csrfToken;
        }
      }
      console.error('No CSRF token found in response or cookies');
      return null;
    }
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error.response || error.message);
    return null;
  }
};

// Add a request interceptor to include the token and CSRF token
axiosInstance.interceptors.request.use(
  async (config) => {
    // Add JWT token if it exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add CSRF token for non-GET methods if not already in an exempt route
    if (
      ['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method.toUpperCase()) && 
      !config.url.includes('/api/v1/auth/login') && 
      !config.url.includes('/api/v1/auth/register') && 
      !config.url.includes('/api/v1/auth/google') &&
      !config.url.includes('/api/v1/auth/forgot-password') &&
      !config.url.includes('/api/v1/auth/reset-password')
    ) {
      if (!csrfToken) {
        csrfToken = await fetchCsrfToken();
      }
      
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
        console.log('Setting CSRF token in request header:', csrfToken);
        // Debug cookie info
        console.log('All cookies:', document.cookie);
      } else {
        console.error('No CSRF token available for request!');
      }
    }
    
    return config;
  },
  (error) => {
    // Do something with request error
    return Promise.reject(error);
  }
);

// Add a response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    // Any status code that lie within the range of 2xx cause this function to trigger
    // Do nothing, just return the response
    return response;
  },
  async (error) => {
    // Any status codes that falls outside the range of 2xx cause this function to trigger
    console.error('API Error:', error.response || error.message); // Log the error

    // If we get a 400 with CSRF error, try to refresh the token and retry
    if (
      error.response && 
      error.response.status === 400 && 
      error.response.data && 
      error.response.data.error && 
      error.response.data.error.includes('CSRF')
    ) {
      console.log('CSRF validation failed, attempting to refresh token and retry');
      
      // Clear the token and fetch a new one
      csrfToken = null;
      await fetchCsrfToken();
      
      // Retry the original request if we have a config
      if (error.config) {
        // Add the new CSRF token
        if (csrfToken) {
          error.config.headers['X-CSRFToken'] = csrfToken;
        }
        
        // Retry the request with axiosInstance to maintain consistency
        // Use a new instance of axios without interceptors to avoid infinite loops
        const retryConfig = {...error.config};
        delete retryConfig.headers['X-CSRFToken']; // Remove old token
        
        // Add the fresh token
        if (csrfToken) {
          retryConfig.headers['X-CSRFToken'] = csrfToken;
        }
        
        console.log('Retrying request with new CSRF token');
        return axios(retryConfig);
      }
    }

    if (error.response && error.response.status === 401) {
      console.log('Received 401 Unauthorized. Checking current route...');
      
      // Don't redirect to login if already on login page or on Google callback page
      const currentPath = window.location.pathname;
      if (currentPath === '/login' || currentPath === '/google-auth-callback' || currentPath.includes('/reset-password/')) {
        console.log('On authentication page, not redirecting');
        return Promise.reject(error);
      }
      
      console.log('Unauthorized access detected. Logging out.');
      // 1. Remove the token from local storage
      localStorage.removeItem('token');
      
      // 2. Dispatch storage event to potentially update other tabs (though App.js handles this on load)
      window.dispatchEvent(new Event('storage')); 

      // 3. Redirect to the login page
      // We use window.location.href to force a full page reload, 
      // which ensures the App component re-evaluates the login state.
      window.location.href = '/login';
    }

    // Pass the error along to the calling code if needed
    return Promise.reject(error);
  }
);

export { fetchCsrfToken };
export default axiosInstance; 