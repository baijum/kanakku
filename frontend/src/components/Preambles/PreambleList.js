import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';

// Function to get the token from localStorage
const getToken = () => localStorage.getItem('token');

function PreambleList() {
  const [preambles, setPreambles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [currentPreamble, setCurrentPreamble] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    content: '',
    is_default: false,
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // Fetch preambles when component mounts
  useEffect(() => {
    fetchPreambles();
  }, []);

  const fetchPreambles = async () => {
    setLoading(true);
    try {
      const token = getToken();
      const response = await axios.get('/api/v1/preambles', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setPreambles(response.data.preambles || []);
    } catch (error) {
      console.error('Error fetching preambles:', error);
      showSnackbar('Failed to load preambles', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (preamble = null) => {
    if (preamble) {
      setFormData({
        name: preamble.name,
        content: preamble.content,
        is_default: preamble.is_default,
      });
      setCurrentPreamble(preamble);
    } else {
      setFormData({
        name: '',
        content: '',
        is_default: false,
      });
      setCurrentPreamble(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleOpenDeleteDialog = (preamble) => {
    setCurrentPreamble(preamble);
    setOpenDeleteDialog(true);
  };

  const handleCloseDeleteDialog = () => {
    setOpenDeleteDialog(false);
  };

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'is_default' ? checked : value,
    });
  };

  const handleSubmit = async () => {
    if (!formData.name || !formData.content) {
      showSnackbar('Name and content are required', 'error');
      return;
    }

    setLoading(true);
    const token = getToken();
    try {
      if (currentPreamble) {
        // Update existing preamble
        await axios.put(`/api/v1/preambles/${currentPreamble.id}`, formData, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        showSnackbar('Preamble updated successfully', 'success');
      } else {
        // Create new preamble
        await axios.post('/api/v1/preambles', formData, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        showSnackbar('Preamble created successfully', 'success');
      }
      handleCloseDialog();
      fetchPreambles();
    } catch (error) {
      console.error('Error saving preamble:', error);
      showSnackbar('Failed to save preamble', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!currentPreamble) return;

    setLoading(true);
    const token = getToken();
    try {
      await axios.delete(`/api/v1/preambles/${currentPreamble.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      showSnackbar('Preamble deleted successfully', 'success');
      handleCloseDeleteDialog();
      fetchPreambles();
    } catch (error) {
      console.error('Error deleting preamble:', error);
      showSnackbar('Failed to delete preamble', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Typography variant="h4" gutterBottom>
        Preambles
      </Typography>
      <Typography variant="body1" paragraph>
        Preambles are text that will appear at the beginning of exported transaction data.
      </Typography>

      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Preamble
        </Button>
      </Box>

      {loading && preambles.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : preambles.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1">
            No preambles found. Create one to add text to the beginning of your exported transaction data.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Content Preview</TableCell>
                <TableCell>Default</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {preambles.map((preamble) => (
                <TableRow key={preamble.id}>
                  <TableCell>{preamble.name}</TableCell>
                  <TableCell>
                    {preamble.content.length > 50
                      ? `${preamble.content.substring(0, 50)}...`
                      : preamble.content}
                  </TableCell>
                  <TableCell>{preamble.is_default ? 'Yes' : 'No'}</TableCell>
                  <TableCell>
                    <IconButton
                      aria-label="edit"
                      onClick={() => handleOpenDialog(preamble)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      aria-label="delete"
                      onClick={() => handleOpenDeleteDialog(preamble)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Dialog for adding/editing preamble */}
      <Dialog open={openDialog} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>
          {currentPreamble ? 'Edit Preamble' : 'Add New Preamble'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="name"
            label="Name"
            fullWidth
            value={formData.name}
            onChange={handleInputChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="content"
            label="Content"
            fullWidth
            multiline
            rows={10}
            value={formData.content}
            onChange={handleInputChange}
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={formData.is_default}
                onChange={handleInputChange}
                name="is_default"
              />
            }
            label="Set as default preamble for exports"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog for confirming deletion */}
      <Dialog open={openDeleteDialog} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the preamble "{currentPreamble?.name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default PreambleList; 