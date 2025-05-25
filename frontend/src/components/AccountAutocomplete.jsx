import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  TextField,
  Autocomplete,
  CircularProgress,
} from '@mui/material';
import axiosInstance from '../api/axiosInstance';

// Simple debounce implementation
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

/**
 * AccountAutocomplete Component
 * 
 * Provides auto-completion for Ledger CLI-style account names.
 * Auto-completion activates when the user types at least one colon (:).
 * Supports hierarchical account name suggestions.
 */
function AccountAutocomplete({
  value,
  onChange,
  label = "Search transactions...",
  placeholder = "Search by description, payee, amount, status, or account",
  helperText = "Try: 'starbucks 50 cleared' or 'groceries checking unmarked'",
  fullWidth = true,
  ...otherProps
}) {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState(value || '');

  // Function to fetch suggestions
  const fetchSuggestionsBase = useCallback(async (searchValue) => {
    if (!searchValue || !searchValue.includes(':')) {
      setSuggestions([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await axiosInstance.get('/api/v1/accounts/autocomplete', {
        params: {
          prefix: searchValue,
          limit: 10
        }
      });

      if (response.data && response.data.suggestions) {
        setSuggestions(response.data.suggestions);
      } else {
        setSuggestions([]);
      }
    } catch (error) {
      console.error('Error fetching account suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced function to fetch suggestions
  const fetchSuggestions = useMemo(
    () => debounce(fetchSuggestionsBase, 300),
    [fetchSuggestionsBase]
  );

  // Effect to fetch suggestions when input value changes
  useEffect(() => {
    if (inputValue && inputValue.includes(':')) {
      fetchSuggestions(inputValue);
    } else {
      setSuggestions([]);
      setLoading(false);
    }
  }, [inputValue, fetchSuggestions]);

  // Handle input value change
  const handleInputChange = (event, newInputValue) => {
    setInputValue(newInputValue);
    onChange(newInputValue);
  };

  // Handle option selection
  const handleChange = (event, newValue) => {
    if (newValue) {
      setInputValue(newValue);
      onChange(newValue);
    }
  };

  // Custom filter function - don't filter options since we're doing server-side filtering
  const filterOptions = (options) => options;

  return (
    <Autocomplete
      freeSolo
      options={suggestions}
      value={value}
      inputValue={inputValue}
      onInputChange={handleInputChange}
      onChange={handleChange}
      filterOptions={filterOptions}
      loading={loading}
      disabled={otherProps.disabled}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder={placeholder}
          helperText={helperText}
          fullWidth={fullWidth}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
          {...otherProps}
        />
      )}
      renderOption={(props, option) => (
        <li {...props} key={option}>
          {option}
        </li>
      )}
      // Only show suggestions when there's at least one colon in the input
      open={inputValue.includes(':') && suggestions.length > 0 && !otherProps.disabled}
      noOptionsText="No matching accounts found"
    />
  );
}

export default AccountAutocomplete; 