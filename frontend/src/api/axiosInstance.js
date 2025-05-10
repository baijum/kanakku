import axios from 'axios';

// Get the API URL from environment variable, fallback to relative path for development
// Update to ensure the API path always includes the /api/v1 prefix in development
const apiBaseUrl = process.env.REACT_APP_API_URL || '/api/v1/';

// Create an Axios instance
const axiosInstance = axios.create({
  baseURL: apiBaseUrl, // Will use REACT_APP_API_URL in production, API prefix in development
  withCredentials: true, // Send cookies for CSRF
});

// Store the CSRF token
let csrfToken = null;

// Variable to track if a token refresh is in progress
let isRefreshing = false;
// Queue of requests to be retried after token refresh
let refreshQueue = [];

// Function to fetch a CSRF token
const fetchCsrfToken = async () => {
  if (csrfToken) return csrfToken;
  
  try {
    // Use direct axios here (not axiosInstance) to avoid circular dependencies
    const response = await axios.get(`${process.env.REACT_APP_API_URL || '/api/v1/'}csrf-token`, { 
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

// Function to refresh the token
const refreshAuthToken = async () => {
  if (isRefreshing) return;
  
  isRefreshing = true;
  try {
    const response = await axios.post(`${process.env.REACT_APP_API_URL || '/api/v1/'}auth/refresh`, {}, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      withCredentials: true
    });
    
    if (response.data && response.data.token) {
      // Store the new token
      localStorage.setItem('token', response.data.token);
      console.log('Token refreshed successfully');
      return response.data.token;
    }
    return null;
  } catch (error) {
    console.error('Token refresh failed:', error.response || error.message);
    return null;
  } finally {
    isRefreshing = false;
  }
};

// Function to process the queue of requests after token refresh
const processQueue = (token) => {
  refreshQueue.forEach(({ config, resolve, reject }) => {
    config.headers['Authorization'] = `Bearer ${token}`;
    resolve(axios(config));
  });
  refreshQueue = [];
};

// Add a request interceptor to include the token and CSRF token
axiosInstance.interceptors.request.use(
  async (config) => {
    // Enhanced logging to debug request URLs
    console.log(`API Request: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`);
    
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
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    // Any status code that lie within the range of 2xx cause this function to trigger
    console.log(`API Response: ${response.status} ${response.config.method.toUpperCase()} ${response.config.url}`);
    return response;
  },
  async (error) => {
    // Any status codes that falls outside the range of 2xx cause this function to trigger
    // Enhanced error logging with more details
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      status: error.response?.status,
      statusText: error.response?.statusText,
      error: error.response?.data?.error || error.message,
      fullError: error.response?.data || error.message
    });

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

    // Handle expired JWT token
    if (
      error.response && 
      error.response.status === 401 && 
      error.response.data && 
      error.response.data.code === 'token_expired' &&
      error.config && 
      !error.config.__isRetryRequest &&
      localStorage.getItem('token')
    ) {
      console.log('Token expired, attempting to refresh...');
      
      // Create a new Promise to handle the retry after token refresh
      return new Promise((resolve, reject) => {
        if (!isRefreshing) {
          refreshAuthToken().then(newToken => {
            if (newToken) {
              // Retry the original request with the new token
              const retryConfig = { ...error.config };
              retryConfig.headers['Authorization'] = `Bearer ${newToken}`;
              retryConfig.__isRetryRequest = true;
              
              // Process any pending requests in the queue
              processQueue(newToken);
              
              resolve(axios(retryConfig));
            } else {
              // If token refresh failed, reject all requests and log out
              processQueue(null);
              localStorage.removeItem('token');
              window.dispatchEvent(new Event('storage')); 
              
              // Only redirect if not already on an auth page
              const currentPath = window.location.pathname;
              if (currentPath !== '/login' && !currentPath.includes('/google-auth-callback') && !currentPath.includes('/reset-password/')) {
                window.location.href = '/login';
              }
              
              reject(error);
            }
          });
        } else {
          // Add the request to the queue to be retried after token refresh
          refreshQueue.push({ config: error.config, resolve, reject });
        }
      });
    }

    // Handle other 401 errors (not token expiration)
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

export { fetchCsrfToken, refreshAuthToken };
export default axiosInstance; 