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

const BookSelector = ({ isLoggedIn }) => {
  const [books, setBooks] = useState([]);
  const [activeBook, setActiveBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBooks = async (retryAttempt = 0) => {
    try {
      // Only set loading true on the first attempt
      if (retryAttempt === 0) {
        setLoading(true);
      }
      console.log(`BookSelector: Fetching books list (Attempt ${retryAttempt + 1})`);
      const response = await axiosInstance.get('/api/v1/books');
      const fetchedBooks = (response.data && Array.isArray(response.data)) ? response.data : [];
      // Update books state only on the first attempt or if they change
      if (retryAttempt === 0 || JSON.stringify(fetchedBooks) !== JSON.stringify(books)) {
          setBooks(fetchedBooks);
      }
      console.log(`BookSelector: Found ${fetchedBooks.length} books`);

      console.log("BookSelector: Fetching active book");
      const activeResponse = await axiosInstance.get('/api/v1/books/active');
      let fetchedActiveBook = (activeResponse.data && Object.keys(activeResponse.data).length > 0) ? activeResponse.data : null;

      if (fetchedActiveBook) {
        console.log("BookSelector: Active book found", fetchedActiveBook);
        setActiveBook(fetchedActiveBook);
        setLoading(false); // Success, stop loading
      } else {
         console.log("BookSelector: No active book returned by API.");
         // If books exist (or potentially were just created) but no active one is set yet,
         // maybe wait briefly and try fetching active book again. Check length based on latest fetch.
         if (fetchedBooks.length > 0 && retryAttempt < 2) {
            console.log(`BookSelector: Books found, but no active book. Retrying fetch (Attempt ${retryAttempt + 2})...`);
            setTimeout(() => fetchBooks(retryAttempt + 1), 500); // Retry after 500ms
            // Keep loading true until retry completes or fails
            return;
         }

         // If still no active book after retries, or no books exist at all
         console.log("BookSelector: Retries exhausted or no books found. Checking fallback conditions.");
         if (fetchedBooks.length > 0) {
            // If an active book wasn't found via API after retries, but we have books,
            // Let's check if the user *has* an active_book_id set (maybe fetch /auth/me?)
            // For now, we will just use the first book as a visual fallback in the render logic below.
            // We won't try to set it active from here anymore, as the backend should handle it.
            console.log("BookSelector: No active book found after retries, will rely on render fallback using first book.");
            setActiveBook(null); // Explicitly set to null if API failed
         } else {
            // If no books exist after fetches
            console.log("BookSelector: No books found and no active book set.");
            setActiveBook(null);
            // The backend should create a default book on registration.
            // If we reach here after login, it implies an issue with that process or the API.
            // Removing client-side creation attempt:
            /*
            console.log("BookSelector: Creating default book");
            try {
              const createResponse = await axiosInstance.post('/api/v1/books', { name: "Book 1" });
              if (createResponse.data && createResponse.data.id) {
                console.log("BookSelector: Setting new book as active", createResponse.data);
                await axiosInstance.post(`/api/v1/books/${createResponse.data.id}/set-active`);
                setActiveBook(createResponse.data);
                setBooks([createResponse.data]);
              }
            } catch (createErr) {
              console.error('BookSelector: Error creating default book:', createErr);
            }
            */
         }
         setLoading(false); // Stop loading after retries/fallbacks
      }

    } catch (err) {
      console.error('BookSelector: Error fetching books:', err);
      setError('Failed to load books');
      setLoading(false);
    }
  };

  // Fetch books on component mount and when login status changes
  useEffect(() => {
    // Only fetch if logged in
    if (isLoggedIn) {
      console.log('BookSelector: isLoggedIn is true, fetching books...');
      fetchBooks();
    } else {
      // Clear state if logged out
      console.log('BookSelector: isLoggedIn is false, clearing state.');
      setBooks([]);
      setActiveBook(null);
      setLoading(false); // Not loading if not logged in
      setError(null);
    }
  }, [isLoggedIn]); // Add isLoggedIn to dependency array

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

  // Only show default book message if there are truly no books
  if (books.length === 0 && !loading) {
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
  if (!activeBook && books.length > 0 && !loading) {
    // Use the first book as a fallback
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