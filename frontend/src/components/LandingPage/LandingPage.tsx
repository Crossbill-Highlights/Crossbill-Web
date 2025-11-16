import { Alert, Box, Container, Typography } from '@mui/material';
import { useState } from 'react';
import { useGetBooksApiV1HighlightsBooksGet } from '../../api/generated/highlights/highlights';
import { SearchBar } from '../common/SearchBar';
import { SectionTitle } from '../common/SectionTitle';
import { Spinner } from '../common/Spinner';
import { BookList } from './components/BookList';

export const LandingPage = () => {
  const [searchText, setSearchText] = useState('');
  const { data, isLoading, isError } = useGetBooksApiV1HighlightsBooksGet({
    search: searchText || undefined,
  });

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Crossbill
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your highlights management application
        </Typography>
      </Box>

      <Box sx={{ mb: 4 }}>
        <SectionTitle showDivider>Books</SectionTitle>

        <SearchBar onSearch={setSearchText} placeholder="Search books by title or author..." />

        {isLoading && <Spinner />}

        {isError && <Alert severity="error">Failed to load books. Please try again later.</Alert>}

        {data?.books && data.books.length === 0 && (
          <Typography variant="body1" color="text.secondary">
            No books found. Upload some highlights to get started!
          </Typography>
        )}

        {data?.books && data.books.length > 0 && <BookList books={data.books} />}
      </Box>
    </Container>
  );
};
