import { Box, TextField } from '@mui/material';
import { debounce } from 'lodash';
import { useEffect, useMemo, useState } from 'react';

interface SearchBarProps {
  onSearch: (searchText: string) => void;
  placeholder?: string;
}

export const SearchBar = ({ onSearch, placeholder = 'Search...' }: SearchBarProps) => {
  const [searchInput, setSearchInput] = useState('');

  const debouncedSearch = useMemo(
    () =>
      debounce((value: string) => {
        onSearch(value);
      }, 300),
    [onSearch]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchInput(value);
    debouncedSearch(value);
  };

  const handleClear = () => {
    debouncedSearch.cancel();
    setSearchInput('');
    onSearch('');
  };

  return (
    <Box sx={{ mb: 3 }}>
      <TextField
        fullWidth
        placeholder={placeholder}
        value={searchInput}
        onChange={handleChange}
        onKeyDown={(e) => {
          if (e.key === 'Escape') {
            handleClear();
          }
        }}
        slotProps={{
          input: {
            endAdornment: searchInput && (
              <Box
                component="span"
                onClick={handleClear}
                sx={{
                  cursor: 'pointer',
                  color: 'text.secondary',
                  '&:hover': { color: 'text.primary' },
                }}
              >
                ✕
              </Box>
            ),
          },
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: 'divider',
            },
          },
        }}
      />
    </Box>
  );
};
