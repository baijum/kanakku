import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, unstable_HistoryRouter as HistoryRouter } from 'react-router-dom';
import { ThemeProvider, createTheme, useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { Link as RouterLink } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AddIcon from '@mui/icons-material/Add';
import ListIcon from '@mui/icons-material/List';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import DescriptionIcon from '@mui/icons-material/Description';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import CircularProgress from '@mui/material/CircularProgress';
import AccountForm from './components/Accounts/AccountForm';
import AccountsList from './components/Accounts/AccountsList';
import EditAccount from './components/Accounts/EditAccount';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import ProfileSettings from './components/Auth/ProfileSettings';
import Dashboard from './components/Dashboard';
import AddTransaction from './components/AddTransaction';
import ViewTransactions from './components/ViewTransactions';
import EditTransaction from './components/Transactions/EditTransaction';
import PreambleList from './components/Preambles/PreambleList';
import LogoutIcon from '@mui/icons-material/Logout';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Divider from '@mui/material/Divider';
import GoogleAuthCallback from './components/Auth/GoogleAuthCallback';
import ForgotPassword from './components/Auth/ForgotPassword';
import ResetPassword from './components/Auth/ResetPassword';
import Terms from './components/Pages/Terms';
import Privacy from './components/Pages/Privacy';
import Footer from './components/Footer';
import BookSelector from './components/Books/BookSelector';
import AdminPanel from './components/Admin/AdminPanel';
import axiosInstance, { fetchCsrfToken } from './api/axiosInstance';
import { createBrowserHistory } from 'history';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  components: {
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: 16,
          paddingRight: 16,
          '@media (min-width:600px)': {
            paddingLeft: 24,
            paddingRight: 24,
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: '8px 16px',
          '@media (max-width:600px)': {
            padding: '6px 8px',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          overflow: 'hidden',
        },
      },
    },
  },
});

const history = createBrowserHistory();

// Protected route component
const ProtectedRoute = ({ children, isLoggedIn, authLoading }) => {
  console.log('ProtectedRoute - isLoggedIn:', isLoggedIn, 'authLoading:', authLoading);

  if (authLoading) {
    return null;
  }

  if (!isLoggedIn) {
    // Redirect to login page if not logged in
    return <Navigate to="/login" replace />;
  }
  return children;
};

// ProtectedRoute that also checks for admin status
const AdminRoute = ({ children, isLoggedIn, authLoading }) => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAdminStatus = async () => {
      try {
        const response = await axiosInstance.get('/api/v1/auth/me');
        if (response.data && response.data.is_admin) {
          setIsAdmin(true);
        }
      } catch (err) {
        console.error('Failed to verify admin status:', err);
      } finally {
        setLoading(false);
      }
    };

    if (isLoggedIn && !authLoading) {
      checkAdminStatus();
    }
  }, [isLoggedIn, authLoading]);

  if (authLoading || loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const muiTheme = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('sm'));
  const [userMenuAnchorEl, setUserMenuAnchorEl] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);

  // Fetch CSRF token when the app initializes
  useEffect(() => {
    const fetchInitialCsrfToken = async () => {
      try {
        console.log('Fetching initial CSRF token for application...');
        const token = await fetchCsrfToken();
        if (token) {
          console.log('Initial CSRF token fetched successfully');
        } else {
          console.warn('Failed to get valid CSRF token on app initialization');
        }
      } catch (error) {
        console.error('Error fetching initial CSRF token:', error);
      }
    };

    fetchInitialCsrfToken();
  }, []);

  // Check if user is logged in by validating token
  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem('token');
      console.log('Auth check - Token found in localStorage:', !!token);
      console.log('Auth check - Current URL:', window.location.href);
      console.log('Auth check - Current pathname:', window.location.pathname);
      
      // Check if we're on a Google callback URL that should be handled by the backend
      if (window.location.pathname.includes('/api/v1/auth/google/callback')) {
        console.log('Detected backend Google callback URL on frontend, redirecting to backend...');
        // Redirect to the absolute backend URL with the same query parameters
        const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
        // Make sure to redirect with the full path including /api/v1/auth/google/callback
        const callbackPath = '/api/v1/auth/google/callback';
        window.location.href = `${backendUrl}${callbackPath}${window.location.search}`;
        return;
      }
      
      // Skip validation if on Google auth callback page as it will handle its own authentication
      if (window.location.pathname === '/google-auth-callback') {
        console.log('On Google auth callback page, skipping token validation');
        setAuthLoading(false);
        return;
      }

      if (token) {
        try {
          console.log('Validating token with /api/v1/auth/test...');
          console.log('Token length:', token.length);
          console.log('Token first 20 chars:', token.substring(0, 20) + '...');
          
          const response = await axiosInstance.get('/api/v1/auth/test', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          console.log('Token validation successful. Response:', response.data);
          
          // Check if user is admin
          const userInfoResponse = await axiosInstance.get('/api/v1/auth/me');
          setIsAdmin(userInfoResponse.data?.is_admin || false);
          
          setIsLoggedIn(true);
        } catch (error) {
          console.error('Token validation failed:', error);
          if (error.response) {
            console.error('Error response status:', error.response.status);
            console.error('Error response data:', error.response.data);
          }
          if (error.request) {
            console.error('Error request:', error.request);
          }
          localStorage.removeItem('token');
          setIsLoggedIn(false);
        }
      } else {
        console.log('No token found in localStorage.');
        setIsLoggedIn(false);
      }
      setAuthLoading(false);
    };

    validateToken();

    // Listen for storage events (e.g., logout in another tab)
    const handleStorageChange = () => {
      console.log('Storage event detected, re-validating token...');
      setAuthLoading(true);
      validateToken();
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setAuthLoading(false);
    setUserMenuAnchorEl(null);
    window.location.href = '/login';
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchorEl(null);
  };

  const drawerContent = (
    <>
      <Toolbar />
      <Box sx={{ overflow: 'auto' }}>
        <List>
          <ListItem button component={RouterLink} to="/" onClick={isMobile ? handleDrawerToggle : undefined}>
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItem>
          <ListItem button component={RouterLink} to="/add" onClick={isMobile ? handleDrawerToggle : undefined}>
            <ListItemIcon>
              <AddIcon />
            </ListItemIcon>
            <ListItemText primary="Add Transaction" />
          </ListItem>
          <ListItem button component={RouterLink} to="/transactions" onClick={isMobile ? handleDrawerToggle : undefined}>
            <ListItemIcon>
              <ListIcon />
            </ListItemIcon>
            <ListItemText primary="Transactions" />
          </ListItem>
          <ListItem button component={RouterLink} to="/accounts" onClick={isMobile ? handleDrawerToggle : undefined}>
            <ListItemIcon>
              <AccountBalanceWalletIcon />
            </ListItemIcon>
            <ListItemText primary="Accounts" />
          </ListItem>
          <ListItem button component={RouterLink} to="/preambles" onClick={isMobile ? handleDrawerToggle : undefined}>
            <ListItemIcon>
              <DescriptionIcon />
            </ListItemIcon>
            <ListItemText primary="Preambles" />
          </ListItem>
        </List>
      </Box>
    </>
  );

  if (authLoading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh' 
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <HistoryRouter history={history} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <AppBar
            position="fixed"
            sx={{
              zIndex: (theme) => theme.zIndex.drawer + 1,
              width: isLoggedIn ? { sm: `calc(100% - ${drawerWidth}px)` } : '100%',
              ml: isLoggedIn ? { sm: `${drawerWidth}px` } : 0,
            }}
          >
            <Toolbar>
              {isLoggedIn && (
                <IconButton
                  color="inherit"
                  aria-label="open drawer"
                  edge="start"
                  onClick={handleDrawerToggle}
                  sx={{ mr: 2, display: { sm: 'none' } }}
                >
                  <MenuIcon />
                </IconButton>
              )}
              <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
                <img 
                  src="/logo.svg" 
                  alt="Kanakku Logo" 
                  style={{ height: '32px', marginRight: '10px' }} 
                />
              </Box>
              
              {isLoggedIn && (
                <>
                  <Box sx={{ 
                    mr: 1,
                    maxWidth: { xs: '120px', sm: '200px' },
                    '& .MuiSelect-select': {
                      py: { xs: 0.5 },
                      pl: { xs: 0.5 },
                      pr: { xs: 2 },
                      fontSize: { xs: '0.75rem', sm: '0.875rem' }
                    },
                    '& .MuiSvgIcon-root': {
                      width: { xs: '0.9em' },
                      right: { xs: 0 }
                    }
                  }}>
                    <BookSelector isLoggedIn={isLoggedIn} />
                  </Box>
                  <IconButton
                    color="inherit"
                    onClick={handleUserMenuOpen}
                    aria-controls="user-menu"
                    aria-haspopup="true"
                    sx={{ 
                      padding: { xs: '4px', sm: '8px' } 
                    }}
                  >
                    <AccountCircleIcon />
                  </IconButton>
                </>
              )}
              
              {isLoggedIn ? (
                <Menu
                  id="user-menu"
                  anchorEl={userMenuAnchorEl}
                  keepMounted
                  open={Boolean(userMenuAnchorEl)}
                  onClose={handleUserMenuClose}
                >
                  <MenuItem component={RouterLink} to="/profile" onClick={handleUserMenuClose}>
                    <ListItemIcon>
                      <SettingsIcon fontSize="small" />
                    </ListItemIcon>
                    Profile Settings
                  </MenuItem>
                  
                  {isAdmin && (
                    <MenuItem component={RouterLink} to="/admin" onClick={handleUserMenuClose}>
                      <ListItemIcon>
                        <AdminPanelSettingsIcon fontSize="small" />
                      </ListItemIcon>
                      Admin Panel
                    </MenuItem>
                  )}
                  
                  <Divider />
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    Logout
                  </MenuItem>
                </Menu>
              ) : (
                <Button color="inherit" component={RouterLink} to="/login">
                  Login
                </Button>
              )}
            </Toolbar>
          </AppBar>
          {isLoggedIn && (
            <Box
              component="nav"
              sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
              aria-label="mailbox folders"
            >
              <Drawer
                variant="temporary"
                open={mobileOpen}
                onClose={handleDrawerToggle}
                ModalProps={{
                  keepMounted: true,
                }}
                sx={{
                  display: { xs: 'block', sm: 'none' },
                  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
              >
                {drawerContent}
              </Drawer>
              <Drawer
                variant="permanent"
                sx={{
                  display: { xs: 'none', sm: 'block' },
                  '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
                open
              >
                {drawerContent}
              </Drawer>
            </Box>
          )}
          <Box
            component="main"
            sx={{ 
              flexGrow: 1,
              p: { xs: 2, sm: 3 },
              width: isLoggedIn ? { sm: `calc(100% - ${drawerWidth}px)` } : '100%',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
          >
            <Toolbar />
            <Box sx={{ flexGrow: 1, maxWidth: '100%', overflowX: 'hidden' }}>
              <Routes>
                <Route 
                  path="/" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <Dashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/add" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <AddTransaction />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/transactions" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <ViewTransactions />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/transactions/edit/:id" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <EditTransaction />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/accounts" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <AccountsList />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/accounts/new" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <AccountForm />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/accounts/edit/:id" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <EditAccount />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/preambles" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <PreambleList />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/profile" 
                  element={
                    <ProtectedRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <ProfileSettings />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/admin" 
                  element={
                    <AdminRoute isLoggedIn={isLoggedIn} authLoading={authLoading}>
                      <AdminPanel />
                    </AdminRoute>
                  } 
                />
                <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
                <Route path="/register" element={<Register setIsLoggedIn={setIsLoggedIn} />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/reset-password/:token" element={<ResetPassword />} />
                <Route path="/google-auth-callback" element={<GoogleAuthCallback setIsLoggedIn={setIsLoggedIn} />} />
                <Route path="/terms" element={<Terms />} />
                <Route path="/privacy" element={<Privacy />} />
                <Route 
                  path="*" 
                  element={
                    isLoggedIn ? <Navigate to="/" replace /> : <Navigate to="/login" replace />
                  } 
                />
              </Routes>
            </Box>
            <Footer />
          </Box>
        </Box>
      </HistoryRouter>
    </ThemeProvider>
  );
}

export default App; 