import React, { useState, useEffect, useCallback } from 'react';
import { 
  FormControl, 
  Select, 
  MenuItem, 
  Typography, 
  Box, 
  CircularProgress, 
  Paper,
  Chip
} from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import axiosInstance from '../../api/axiosInstance';

const BookSelector = ({ isLoggedIn }) => {
  const [books, setBooks] = useState([]);
  const [activeBook, setActiveBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBooks = useCallback(async () => {
    if (!isLoggedIn) return;
    
    try {
      setLoading(true);
      console.log('BookSelector: Fetching books list');
      
      // Fetch both books and active book in parallel to reduce flickering
      const [booksResponse, activeResponse] = await Promise.all([
        axiosInstance.get('/api/v1/books'),
        axiosInstance.get('/api/v1/books/active')
      ]);
      
      const fetchedBooks = (booksResponse.data && Array.isArray(booksResponse.data)) ? booksResponse.data : [];
      setBooks(fetchedBooks);
      console.log(`BookSelector: Found ${fetchedBooks.length} books`);
      
      const fetchedActiveBook = (activeResponse.data && Object.keys(activeResponse.data).length > 0) 
        ? activeResponse.data 
        : null;
      
      if (fetchedActiveBook) {
        console.log("BookSelector: Active book found", fetchedActiveBook);
        setActiveBook(fetchedActiveBook);
        localStorage.setItem('active_book_id', fetchedActiveBook.id);
      } else if (fetchedBooks.length > 0) {
        // If no active book but books exist, use the first one visually without making API call
        console.log("BookSelector: No active book, using first book visually");
        // We're intentionally not setting activeBook state here to avoid unnecessary renders
      }
    } catch (err) {
      console.error('BookSelector: Error fetching books:', err);
      setError('Failed to load books');
    } finally {
      setLoading(false);
    }
  }, [isLoggedIn]);

  // Fetch books on component mount and when login status changes
  useEffect(() => {
    if (isLoggedIn) {
      console.log('BookSelector: isLoggedIn is true, fetching books...');
      fetchBooks();
    } else {
      // Clear state if logged out
      console.log('BookSelector: isLoggedIn is false, clearing state.');
      setBooks([]);
      setActiveBook(null);
      setLoading(false);
      setError(null);
    }
  }, [isLoggedIn, fetchBooks]);

  // Handle book selection change
  const handleChange = async (event) => {
    const selectedBookId = event.target.value;
    try {
      // Find the selected book in our array
      const selectedBook = books.find(book => book.id === parseInt(selectedBookId));
      
      // Update local state immediately for visual feedback
      if (selectedBook) {
        setActiveBook(selectedBook);
        localStorage.setItem('active_book_id', selectedBook.id);
      }
      
      // Make the API call
      await axiosInstance.post(`/api/v1/books/${selectedBookId}/set-active`);
      
      // Reload the page with a small delay to ensure components reflect the change
      setTimeout(() => {
        window.location.reload();
      }, 200);
    } catch (err) {
      console.error('Error changing active book:', err);
      setError('Failed to change active book');
    }
  };

  // Simple loading indicator
  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', p: 1, minWidth: 180 }}>
        <CircularProgress size={20} sx={{ mr: 1 }} />
        <Typography variant="body2">Loading...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', p: 1, minWidth: 180 }}>
        <Typography variant="body2" color="error">{error}</Typography>
      </Box>
    );
  }

  // Only show default book message if there are truly no books
  if (books.length === 0) {
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

  // Handle the case where we have books but no active book is set yet
  if (!activeBook && books.length > 0) {
    return (
      <Box>
        <FormControl fullWidth size="small">
          <Select
            value={books[0].id}
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
                    {books[0].name}
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
                  <MenuBookIcon sx={{ mr: 1.5, color: book.id === books[0].id ? 'primary.main' : 'text.secondary' }} />
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: book.id === books[0].id ? 'bold' : 'regular',
                      color: book.id === books[0].id ? 'primary.main' : 'text.primary'
                    }}
                  >
                    {book.name}
                    {book.id === books[0].id && (
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