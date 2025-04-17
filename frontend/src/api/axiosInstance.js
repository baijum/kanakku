import axios from 'axios';

// Create an Axios instance
const axiosInstance = axios.create({
  baseURL: '/', // Use relative paths, assuming proxy is set up in package.json or server handles it
});

// Add a request interceptor to include the token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
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
  (error) => {
    // Any status codes that falls outside the range of 2xx cause this function to trigger
    console.error('API Error:', error.response || error.message); // Log the error

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

export default axiosInstance; 