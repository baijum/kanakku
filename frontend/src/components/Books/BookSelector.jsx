import React, { useState, useEffect } from 'react';
import { FormControl, Select, MenuItem, Typography, Box, CircularProgress } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import StarIcon from '@mui/icons-material/Star';
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
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        p: 1,
        minWidth: 150
      }}>
        <MenuBookIcon sx={{ mr: 1, color: 'text.secondary' }} />
        <Typography variant="body2">Default Book</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      display: 'flex',
      alignItems: 'center',
      minWidth: 150,
      p: 1
    }}>
      <MenuBookIcon sx={{ mr: 1, color: 'text.secondary' }} />
      <Box sx={{ 
        display: 'flex',
        flexDirection: 'column',
        flexGrow: 1
      }}>
        <Typography variant="body2" sx={{ fontWeight: 'medium', color: 'primary.main' }}>
          {activeBook.name}
        </Typography>
        <FormControl fullWidth size="small" sx={{ mt: 0.5 }}>
          <Select
            value={activeBook.id}
            onChange={handleChange}
            displayEmpty
            variant="outlined"
            size="small"
          >
            {books.map((book) => (
              <MenuItem key={book.id} value={book.id}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  {book.name}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    </Box>
  );
};

export default BookSelector; 