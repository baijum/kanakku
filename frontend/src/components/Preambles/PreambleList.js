import React, { useState, useEffect, useCallback, useRef } from 'react';
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
import axiosInstance from '../../api/axiosInstance';

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
  const addButtonRef = useRef(null);
  const editButtonsRef = useRef({});

  const fetchPreambles = useCallback(async () => {
    setLoading(true);
    try {
      const token = getToken();
      const response = await axiosInstance.get('/api/v1/preambles', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setPreambles(response.data.preambles || []);
    } catch (error) {
      console.error('Error fetching preambles:', error);
      showSnackbar('Failed to load preambles', 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch preambles when component mounts
  useEffect(() => {
    fetchPreambles();
  }, [fetchPreambles]);

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
    // Focus will be managed by Dialog's internals now
  };

  const handleOpenDeleteDialog = (preamble) => {
    setCurrentPreamble(preamble);
    setOpenDeleteDialog(true);
  };

  const handleCloseDeleteDialog = () => {
    setOpenDeleteDialog(false);
    // Focus will be managed by Dialog's internals now
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
    const apiUrl = currentPreamble
      ? `/api/v1/preambles/${currentPreamble.id}`
      : '/api/v1/preambles';
    const method = currentPreamble ? 'put' : 'post';

    try {
      await axiosInstance[method](apiUrl, formData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      showSnackbar(
        `Preamble ${currentPreamble ? 'updated' : 'created'} successfully`,
        'success'
      );
      handleCloseDialog();
      fetchPreambles(); // Refresh the list
    } catch (error) {
      console.error('Error saving preamble:', error);
      let errorMessage = 'Failed to save preamble'; // Default message

      // Check for specific backend error structure
      if (error.response && error.response.status === 400 && error.response.data?.message) {
        // Check if the message indicates a duplicate name error
        if (error.response.data.message.includes('already exists for this user')) {
          errorMessage = 'A preamble with this name already exists. Please use a different name.';
        } else {
          // Use the specific message from the backend if it's not the duplicate error
          errorMessage = error.response.data.message;
        }
      } else if (error.response && error.response.data?.error) {
        // Handle cases where the backend might still use the 'error' key (legacy or other routes)
        errorMessage = error.response.data.error;
      }
      // Further checks for network errors, etc., could be added here

      showSnackbar(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!currentPreamble) return;

    setLoading(true);
    const token = getToken();
    try {
      await axiosInstance.delete(`/api/v1/preambles/${currentPreamble.id}`, {
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
          ref={addButtonRef}
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          aria-label="add preamble"
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
                      ref={(el) => { editButtonsRef.current[preamble.id] = el; }}
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
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog} 
        fullWidth 
        maxWidth="md"
        disableEnforceFocus
        keepMounted={false}
        aria-labelledby="preamble-dialog-title"
        container={() => document.body}
        BackdropProps={{ 
          invisible: false,
          sx: { backdropFilter: 'none' }
        }}
        style={{ position: 'fixed' }}
        TransitionProps={{
          role: 'dialog',
          onExit: () => {
            // Focus the button that opened the dialog when it starts closing
            setTimeout(() => {
              if (currentPreamble && currentPreamble.id && editButtonsRef.current[currentPreamble.id]) {
                editButtonsRef.current[currentPreamble.id].focus();
              } else if (addButtonRef.current) {
                addButtonRef.current.focus();
              }
            }, 0);
          }
        }}
      >
        <DialogTitle id="preamble-dialog-title">
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
          <Button 
            onClick={handleCloseDialog}
            aria-label="cancel"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading}
            aria-label="save preamble"
          >
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog for confirming deletion */}
      <Dialog 
        open={openDeleteDialog} 
        onClose={handleCloseDeleteDialog}
        disableEnforceFocus
        aria-labelledby="delete-dialog-title"
        container={() => document.body}
        BackdropProps={{ 
          invisible: false,
          sx: { backdropFilter: 'none' }
        }}
        style={{ position: 'fixed' }}
        TransitionProps={{
          role: 'dialog',
          onExit: () => {
            // Focus the edit button for the preamble when deletion dialog starts closing
            setTimeout(() => {
              if (currentPreamble && currentPreamble.id && editButtonsRef.current[currentPreamble.id]) {
                editButtonsRef.current[currentPreamble.id].focus();
              }
            }, 0);
          }
        }}
      >
        <DialogTitle id="delete-dialog-title">Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the preamble "{currentPreamble?.name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handleCloseDeleteDialog}
            aria-label="cancel deletion"
          >
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={loading}
            aria-label="confirm deletion"
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