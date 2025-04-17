import React, { useState, useEffect } from 'react';
import { 
  FormControl, 
  Select, 
  MenuItem, 
  Typography, 
  Box, 
  CircularProgress, 
  Paper,
  Button,
  Chip
} from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import axiosInstance from '../../api/axiosInstance';

const BookSelector = () => {
  const [books, setBooks] = useState([]);
  const [activeBook, setActiveBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch books on component mount
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        setLoading(true);
        const response = await axiosInstance.get('/api/v1/books');
        setBooks(response.data);
        
        // Get active book
        const activeResponse = await axiosInstance.get('/api/v1/books/active');
        setActiveBook(activeResponse.data);
        
        // If no active book, create a default one
        if (!activeResponse.data || Object.keys(activeResponse.data).length === 0) {
          try {
            // Create a default book if none exists
            const createResponse = await axiosInstance.post('/api/v1/books', { 
              name: "Book 1" 
            });
            
            // Set it as active
            if (createResponse.data && createResponse.data.id) {
              await axiosInstance.post(`/api/v1/books/${createResponse.data.id}/set-active`);
              setActiveBook(createResponse.data);
            }
          } catch (createErr) {
            console.error('Error creating default book:', createErr);
          }
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching books:', err);
        setError('Failed to load books');
        setLoading(false);
      }
    };

    fetchBooks();
  }, []);

  // Handle book selection change
  const handleChange = async (event) => {
    const selectedBookId = event.target.value;
    try {
      // Find the selected book in our array
      const selectedBook = books.find(book => book.id === parseInt(selectedBookId));
      
      // Update local state immediately for visual feedback
      if (selectedBook) {
        setActiveBook(selectedBook);
      }
      
      // Make the API call
      await axiosInstance.post(`/api/v1/books/${selectedBookId}/set-active`);
      
      // Small delay and then reload the page to ensure all components reflect the change
      setTimeout(() => {
        window.location.reload();
      }, 200);
    } catch (err) {
      console.error('Error changing active book:', err);
      setError('Failed to change active book');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', p: 1 }}>
        <CircularProgress size={20} sx={{ mr: 1 }} />
        <Typography variant="body2">Loading books...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', p: 1 }}>
        <Typography variant="body2" color="error">{error}</Typography>
      </Box>
    );
  }

  // Modified this condition to create a default UI for when there are no books
  if ((!activeBook || books.length === 0) && !loading) {
    return (
      <Paper elevation={2} sx={{ 
        display: 'flex', 
        alignItems: 'center',
        py: 1,
        px: 2,
        borderRadius: 2,
        backgroundColor: 'background.paper',
        minWidth: 180
      }}>
        <MenuBookIcon sx={{ mr: 1.5, color: 'primary.main' }} />
        <Typography variant="body2" sx={{ fontWeight: 'medium' }}>Default Book</Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <FormControl fullWidth size="small">
        <Select
          value={activeBook.id}
          onChange={handleChange}
          displayEmpty
          variant="outlined"
          IconComponent={KeyboardArrowDownIcon}
          renderValue={() => (
            <Paper elevation={2} sx={{ 
              display: 'flex', 
              alignItems: 'center',
              py: 1,
              px: 2,
              borderRadius: 2,
              backgroundColor: 'background.paper',
              minWidth: 180,
              border: '1px solid',
              borderColor: 'primary.light',
              '&:hover': {
                borderColor: 'primary.main',
                boxShadow: '0 0 0 1px rgba(25, 118, 210, 0.2)'
              }
            }}>
              <MenuBookIcon sx={{ mr: 1.5, color: 'primary.main' }} />
              <Box>
                <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                  Current Book
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'medium', color: 'text.primary' }}>
                  {activeBook.name}
                </Typography>
              </Box>
            </Paper>
          )}
          sx={{
            '& .MuiOutlinedInput-notchedOutline': { 
              border: 'none' 
            },
            '&:hover .MuiOutlinedInput-notchedOutline': { 
              border: 'none' 
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': { 
              border: 'none' 
            }
          }}
        >
          {books.map((book) => (
            <MenuItem key={book.id} value={book.id} sx={{ py: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <MenuBookIcon sx={{ mr: 1.5, color: book.id === activeBook.id ? 'primary.main' : 'text.secondary' }} />
                <Typography 
                  variant="body2" 
                  sx={{ 
                    fontWeight: book.id === activeBook.id ? 'bold' : 'regular',
                    color: book.id === activeBook.id ? 'primary.main' : 'text.primary'
                  }}
                >
                  {book.name}
                  {book.id === activeBook.id && (
                    <Chip 
                      label="Active" 
                      size="small" 
                      color="primary" 
                      variant="outlined" 
                      sx={{ ml: 1, height: 20, fontSize: '0.7rem' }} 
                    />
                  )}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default BookSelector; 