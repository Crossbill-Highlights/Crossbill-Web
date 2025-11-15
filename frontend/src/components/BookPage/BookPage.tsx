import { useGetBookDetailsApiV1BookBookIdGet } from '@/api/generated/books/books.ts';
import { useSearchHighlightsApiV1HighlightsSearchGet } from '@/api/generated/highlights/highlights.ts';
import { Alert, Box, Container, Typography } from '@mui/material';
import { useParams } from '@tanstack/react-router';
import { useState } from 'react';
import { SectionTitle } from '../common/SectionTitle';
import { Spinner } from '../common/Spinner';
import { BookTitle } from './components/BookTitle';
import { HighlightCard } from './components/HighlightCard';
import { HighlightTags } from './components/HighlightTags';
import { SearchBar } from './components/SearchBar';
import { SearchResults } from './components/SearchResults';

export const BookPage = () => {
  const { bookId } = useParams({ from: '/book/$bookId' });
  const { data: book, isLoading, isError } = useGetBookDetailsApiV1BookBookIdGet(Number(bookId));

  const [searchText, setSearchText] = useState('');

  // Search query - only enabled when there's search text
  const { data: searchResults, isLoading: isSearching } =
    useSearchHighlightsApiV1HighlightsSearchGet(
      {
        searchText: searchText || 'placeholder',
        bookId: Number(bookId),
      },
      {
        query: {
          enabled: searchText.length > 0,
        },
      }
    );

  const totalHighlights =
    book?.chapters?.reduce((sum, chapter) => sum + (chapter.highlights?.length || 0), 0) || 0;

  if (isLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
        }}
      >
        <Container maxWidth="lg">
          <Spinner />
        </Container>
      </Box>
    );
  }

  if (isError || !book) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ pt: 4 }}>
            <Alert severity="error">Failed to load book details. Please try again later.</Alert>
          </Box>
        </Container>
      </Box>
    );
  }

  const chapters = (book?.chapters || []).filter(
    (chapter) => chapter.highlights && chapter.highlights.length > 0
  );

  // Show search results or regular chapter view
  const showSearchResults = searchText.length > 0;

  return (
    <Box
      sx={{
        minHeight: '100vh',
      }}
    >
      <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3 }, py: 4 }}>
        {/* Book Info Card */}
        <BookTitle book={book} highlightCount={totalHighlights} />

        {/* Search Bar */}
        <SearchBar onSearch={setSearchText} />

        {/* Search Results */}
        {showSearchResults && (
          <SearchResults
            isSearching={isSearching}
            highlights={searchResults?.highlights}
            searchText={searchText}
            bookId={book.id}
          />
        )}

        {/* Regular Chapter View (when not searching) */}
        {!showSearchResults && (
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', lg: '1fr 300px' },
              gap: 4,
              alignItems: 'start',
            }}
          >
            {/* Main content - Highlights */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {chapters && chapters.length === 0 && (
                <Typography variant="body1" color="text.secondary">
                  No chapters found for this book.
                </Typography>
              )}

              {chapters.map((chapter) => (
                <Box key={chapter.id}>
                  {/* Chapter Header */}
                  <SectionTitle showDivider>{chapter.name}</SectionTitle>

                  {/* Highlights in this chapter */}
                  {chapter.highlights && chapter.highlights.length > 0 ? (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {chapter.highlights.map((highlight) => (
                        <HighlightCard key={highlight.id} highlight={highlight} bookId={book.id} />
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ pl: 0.5 }}>
                      No highlights found in this chapter.
                    </Typography>
                  )}
                </Box>
              ))}
            </Box>

            {/* Sidebar - Tags (Desktop only) */}
            <Box sx={{ display: { xs: 'none', lg: 'block' } }}>
              <HighlightTags tags={book.highlight_tags || []} />
            </Box>
          </Box>
        )}
      </Container>
    </Box>
  );
};
