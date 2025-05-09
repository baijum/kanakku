import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Divider,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import axiosInstance from '../../api/axiosInstance';

const BookManagement = () => {
  const [books, setBooks] = useState([]);
  const [activeBook, setActiveBook] = useState(null);
  const [newBookName, setNewBookName] = useState('');
  const [editBook, setEditBook] = useState(null);
  const [editBookName, setEditBookName] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [bookToDelete, setBookToDelete] = useState(null);
  const [confirmDeleteName, setConfirmDeleteName] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/v1/books');
      setBooks(response.data);
      
      // Get active book
      const activeResponse = await axiosInstance.get('/api/v1/books/active');
      setActiveBook(activeResponse.data);
      
      // Save the active book ID to localStorage if it exists
      if (activeResponse.data && activeResponse.data.id) {
        localStorage.setItem('active_book_id', activeResponse.data.id);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching books:', err);
      setError('Failed to load books. Please try again later.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleCreateBook = async (e) => {
    e.preventDefault();
    
    if (!newBookName.trim()) {
      setError('Book name cannot be empty');
      return;
    }
    
    try {
      await axiosInstance.post('/api/v1/books', { 
        name: newBookName.trim()
      });
      
      setSuccessMessage('Book created successfully!');
      setNewBookName('');
      fetchBooks();
      
      // Add a page reload to refresh the BookSelector in the header
      window.location.reload();
      
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      console.error('Error creating book:', err);
      setError(err.response?.data?.error || 'Failed to create book');
    }
  };

  const handleEditClick = (book) => {
    setEditBook(book);
    setEditBookName(book.name);
    setIsDialogOpen(true);
  };

  const handleDeleteClick = (book) => {
    // Check if this is the active book 
    if (activeBook && book.id === activeBook.id) {
      setError("Cannot delete the active book. Please set another book as active first.");
      return;
    }
    
    setBookToDelete(book);
    setConfirmDeleteName('');
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteBook = async () => {
    // Check if the user entered the exact book name for confirmation
    if (confirmDeleteName !== bookToDelete.name) {
      setError("Book name doesn't match. Please enter the exact name to confirm deletion.");
      return;
    }
    
    try {
      await axiosInstance.delete(`/api/v1/books/${bookToDelete.id}`);
      
      setSuccessMessage('Book deleted successfully!');
      setIsDeleteDialogOpen(false);
      setConfirmDeleteName('');
      fetchBooks();
      
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      console.error('Error deleting book:', err);
      setError(err.response?.data?.error || 'Failed to delete book');
      setIsDeleteDialogOpen(false);
    }
  };

  const handleEditSave = async () => {
    if (!editBookName.trim()) {
      setError('Book name cannot be empty');
      return;
    }
    
    try {
      await axiosInstance.put(`/api/v1/books/${editBook.id}`, { name: editBookName.trim() });
      
      setSuccessMessage('Book updated successfully!');
      setIsDialogOpen(false);
      fetchBooks();
      
      // Check if we're editing the active book
      if (activeBook && editBook && activeBook.id === editBook.id) {
        // Reload the page to update the BookSelector in the header
        setTimeout(() => {
          window.location.reload();
        }, 500); // Small delay to ensure the API call completes
      }
      
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      console.error('Error updating book:', err);
      setError(err.response?.data?.error || 'Failed to update book');
    }
  };

  const handleSetActiveBook = async (bookId) => {
    try {
      await axiosInstance.post(`/api/v1/books/${bookId}/set-active`);
      setSuccessMessage('Active book changed successfully!');
      
      // Refresh book list and active book
      fetchBooks();
      
      // Reload the page to update the BookSelector in the header
      setTimeout(() => {
        window.location.reload();
      }, 500);
      
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      console.error('Error setting active book:', err);
      setError(err.response?.data?.error || 'Failed to set active book');
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Book Management
      </Typography>
      <Divider sx={{ mb: 3 }} />
      
      {/* Error and success messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      )}
      
      {/* Create new book form */}
      <Box component="form" onSubmit={handleCreateBook} sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Create New Book
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Book Name"
            variant="outlined"
            value={newBookName}
            onChange={(e) => setNewBookName(e.target.value)}
            fullWidth
            size="small"
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading}
          >
            Create
          </Button>
        </Box>
      </Box>
      
      {/* Books list */}
      <Typography variant="h6" sx={{ mb: 2 }}>
        Your Books
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
          <CircularProgress />
        </Box>
      ) : books.length === 0 ? (
        <Typography variant="body1" color="text.secondary">
          No books found. Create your first book above.
        </Typography>
      ) : (
        <List>
          {books.map(book => (
            <ListItem
              key={book.id}
              secondaryAction={
                <Box>
                  {activeBook && activeBook.id !== book.id && (
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleSetActiveBook(book.id)}
                      sx={{ mr: 1 }}
                    >
                      Set as Active
                    </Button>
                  )}
                  <IconButton
                    edge="end"
                    onClick={() => handleEditClick(book)}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    onClick={() => handleDeleteClick(book)}
                    color="error"
                    disabled={activeBook && activeBook.id === book.id}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              }
            >
              <ListItemText 
                primary={book.name}
                // Visually highlight the active book
                primaryTypographyProps={{
                  fontWeight: activeBook && activeBook.id === book.id ? 'bold' : 'normal',
                  color: activeBook && activeBook.id === book.id ? 'primary.main' : 'inherit'
                }}
              />
            </ListItem>
          ))}
        </List>
      )}
      
      {/* Edit dialog */}
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)}>
        <DialogTitle>Edit Book</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Book Name"
            fullWidth
            variant="outlined"
            value={editBookName}
            onChange={(e) => setEditBookName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleEditSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete confirmation dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete Book</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Are you sure you want to delete the book "{bookToDelete?.name}"?
            <br /><br />
            <strong>Warning:</strong> This will permanently delete all accounts and transactions associated with this book.
            This action cannot be undone.
            <br /><br />
            <strong>Note:</strong> The currently active book cannot be deleted. You must set another book as active first.
          </DialogContentText>
          <DialogContentText sx={{ mb: 2, color: 'error.main' }}>
            To confirm deletion, please type the exact name of the book below:
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Type book name to confirm"
            fullWidth
            variant="outlined"
            value={confirmDeleteName}
            onChange={(e) => setConfirmDeleteName(e.target.value)}
            error={confirmDeleteName.length > 0 && confirmDeleteName !== bookToDelete?.name}
            helperText={
              confirmDeleteName.length > 0 && confirmDeleteName !== bookToDelete?.name
                ? "Name doesn't match"
                : ""
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleDeleteBook} 
            variant="contained" 
            color="error"
            disabled={confirmDeleteName !== bookToDelete?.name}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default BookManagement; 