import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { Link as RouterLink } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AddIcon from '@mui/icons-material/Add';
import ListIcon from '@mui/icons-material/List';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Reports from './components/Reports';
import AccountForm from './components/Accounts/AccountForm';
import AccountsList from './components/Accounts/AccountsList';
import EditAccount from './components/Accounts/EditAccount';
import Login from './components/Auth/Login';
import Dashboard from './components/Dashboard';
import AddTransaction from './components/AddTransaction';
import ViewTransactions from './components/ViewTransactions';
import EditTransaction from './components/Transactions/EditTransaction';
import LogoutIcon from '@mui/icons-material/Logout';

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
});

// Protected route component
const ProtectedRoute = ({ children, isLoggedIn }) => {
  console.log('ProtectedRoute - isLoggedIn:', isLoggedIn);
  if (!isLoggedIn) {
    // Redirect to login page if not logged in
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const muiTheme = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('sm'));

  // Check if user is logged in
  useEffect(() => {
    const checkLoginStatus = () => {
      const token = localStorage.getItem('token');
      console.log('Auth check - Token exists:', !!token);
      setIsLoggedIn(!!token);
    };

    // Initial check
    checkLoginStatus();

    // Listen for storage events (for multi-tab logout)
    window.addEventListener('storage', checkLoginStatus);

    return () => {
      window.removeEventListener('storage', checkLoginStatus);
    };
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    // Optional: redirect to login page
    window.location.href = '/login';
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
          <ListItem button component={RouterLink} to="/reports" onClick={isMobile ? handleDrawerToggle : undefined}>
            <ListItemIcon>
              <AccountBalanceIcon />
            </ListItemIcon>
            <ListItemText primary="Reports" />
          </ListItem>
          <ListItem button component={RouterLink} to="/accounts" onClick={isMobile ? handleDrawerToggle : undefined}>
            <ListItemIcon>
              <AccountBalanceWalletIcon />
            </ListItemIcon>
            <ListItemText primary="Accounts" />
          </ListItem>
        </List>
      </Box>
    </>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar
            position="fixed"
            sx={{
              zIndex: (theme) => theme.zIndex.drawer + 1,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              ml: { sm: `${drawerWidth}px` },
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { sm: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                Kanakku
              </Typography>
              {isLoggedIn ? (
                <Button 
                  color="inherit" 
                  onClick={handleLogout}
                  startIcon={<LogoutIcon />}
                >
                  Logout
                </Button>
              ) : (
                <Button 
                  color="inherit" 
                  component={RouterLink} 
                  to="/login"
                >
                  Login
                </Button>
              )}
            </Toolbar>
          </AppBar>
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
          <Box
            component="main"
            sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
          >
            <Toolbar />
            <Routes>
              <Route 
                path="/" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/add" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <AddTransaction />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/transactions" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <ViewTransactions />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/transactions/edit/:id" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <EditTransaction />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/reports" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <Reports />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/accounts" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <AccountsList />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/accounts/new" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <AccountForm />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/accounts/edit/:id" 
                element={
                  <ProtectedRoute isLoggedIn={isLoggedIn}>
                    <EditAccount />
                  </ProtectedRoute>
                } 
              />
              <Route path="/login" element={<Login />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App; 