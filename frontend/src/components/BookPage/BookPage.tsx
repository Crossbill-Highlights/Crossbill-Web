import {
  useGetBookDetailsApiV1BooksBookIdGet,
  useGetHighlightTagsApiV1BooksBookIdHighlightTagsGet,
} from '@/api/generated/books/books';
import { useSearchHighlightsApiV1HighlightsSearchGet } from '@/api/generated/highlights/highlights.ts';
import type { Highlight } from '@/api/generated/model';
import { FadeInOut } from '@/components/common/animations/FadeInOut.tsx';
import { scrollToElementWithHighlight } from '@/components/common/animations/scrollUtils';
import { SwapVert as SwapVertIcon } from '@mui/icons-material';
import { Alert, Box, Container, IconButton, Tooltip, useMediaQuery, useTheme } from '@mui/material';
import { useNavigate, useParams, useSearch } from '@tanstack/react-router';
import { keyBy } from 'lodash';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { ScrollToTopButton } from '../common/ScrollToTopButton';
import { SearchBar } from '../common/SearchBar';
import { Spinner } from '../common/Spinner';
import { BookmarkList } from './components/BookmarkList';
import { BookTitle } from './components/BookTitle';
import { ChapterList } from './components/ChapterList';
import { ChapterNav } from './components/ChapterNav';
import { HighlightTags } from './components/HighlightTags';
import { HighlightViewModal } from './components/HighlightViewModal';
import { groupSearchResultsIntoChapters } from './utils/groupSearchResults';

export const BookPage = () => {
  const { bookId } = useParams({ from: '/book/$bookId' });
  const { search, tagId, highlightId } = useSearch({ from: '/book/$bookId' });
  const { data: book, isLoading, isError } = useGetBookDetailsApiV1BooksBookIdGet(Number(bookId));

  // Fetch available tags for the book (used by the highlight modal)
  const { data: tagsResponse } = useGetHighlightTagsApiV1BooksBookIdHighlightTagsGet(
    Number(bookId)
  );

  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const navigate = useNavigate({ from: '/book/$bookId' });
  const searchText = search || '';

  const [selectedTagId, setSelectedTagId] = useState<number | undefined>(tagId);
  const [isReversed, setIsReversed] = useState(false);

  // Modal state for highlight viewing - synced with URL
  const [openHighlightId, setOpenHighlightId] = useState<number | undefined>(highlightId);

  const handleSearch = (value: string) => {
    navigate({
      search: (prev) => ({
        ...prev,
        search: value || undefined,
      }),
      replace: true,
    });
  };

  const handleTagClick = (tagId: number | null) => {
    setSelectedTagId(tagId || undefined);
    navigate({
      search: (prev) => ({
        ...prev,
        tagId: tagId || undefined,
      }),
      replace: true,
    });
  };

  const handleBookmarkClick = (highlightId: number) => {
    // Clear search to ensure the highlight is visible
    if (searchText) {
      navigate({
        search: (prev) => ({
          ...prev,
          search: undefined,
        }),
        replace: true,
      });
    }

    // Scroll to the highlight after a short delay to ensure DOM is ready
    scrollToElementWithHighlight(`highlight-${highlightId}`, { behavior: 'smooth' });
  };

  const handleChapterClick = (chapterId: number | string) => {
    // Clear search to ensure the chapter is visible
    if (searchText) {
      navigate({
        search: (prev) => ({
          ...prev,
          search: undefined,
        }),
        replace: true,
      });
    }

    // Scroll to the chapter
    scrollToElementWithHighlight(`chapter-${chapterId}`, { behavior: 'smooth', block: 'start' });
  };

  // Handler to open a highlight modal - updates URL
  const handleOpenHighlight = useCallback(
    (highlightIdToOpen: number) => {
      setOpenHighlightId(highlightIdToOpen);
      navigate({
        search: (prev) => ({
          ...prev,
          highlightId: highlightIdToOpen,
        }),
        replace: true,
      });
    },
    [navigate]
  );

  // Handler to close the highlight modal - removes highlightId from URL
  const handleCloseHighlight = useCallback(
    (lastViewedHighlightId?: number) => {
      setOpenHighlightId(undefined);
      navigate({
        search: (prev) => ({
          ...prev,
          highlightId: undefined,
        }),
        replace: true,
      });

      // Scroll to the last viewed highlight (mobile only)
      if (lastViewedHighlightId && isMobile) {
        scrollToElementWithHighlight(`highlight-${lastViewedHighlightId}`);
      }
    },
    [navigate, isMobile]
  );

  // Handler to navigate between highlights - updates URL
  const handleNavigateHighlight = useCallback(
    (newHighlightId: number) => {
      setOpenHighlightId(newHighlightId);
      navigate({
        search: (prev) => ({
          ...prev,
          highlightId: newHighlightId,
        }),
        replace: true,
      });
    },
    [navigate]
  );

  // Sync modal state when URL changes (e.g., browser back/forward)
  useEffect(() => {
    setOpenHighlightId(highlightId);
  }, [highlightId]);

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

  // Show search results or regular chapter view
  const showSearchResults = searchText.length > 0;

  // Create a map of highlight_id -> bookmark for efficient lookup
  const bookmarksByHighlightId = useMemo(
    () => keyBy(book?.bookmarks || [], 'highlight_id'),
    [book?.bookmarks]
  );

  // Filter chapters by selected tag
  const filteredChapters = useMemo(() => {
    const chaptersWithHighlights = (book?.chapters || []).filter(
      (chapter) => chapter.highlights && chapter.highlights.length > 0
    );

    if (!selectedTagId) {
      return chaptersWithHighlights;
    }

    return chaptersWithHighlights
      .map((chapter) => ({
        ...chapter,
        highlights: chapter.highlights?.filter((highlight) =>
          highlight.highlight_tags?.some((tag) => tag.id === selectedTagId)
        ),
      }))
      .filter((chapter) => chapter.highlights && chapter.highlights.length > 0);
  }, [book?.chapters, selectedTagId]);

  // Filter search results by selected tag
  const filteredSearchResults = useMemo(() => {
    if (!selectedTagId) {
      return searchResults?.highlights;
    }
    return searchResults?.highlights?.filter((highlight) =>
      highlight.highlight_tags?.some((tag) => tag.id === selectedTagId)
    );
  }, [searchResults?.highlights, selectedTagId]);

  // Unified chapter data for both search and regular views
  const chapters = useMemo(() => {
    let result;
    if (showSearchResults) {
      result = groupSearchResultsIntoChapters(filteredSearchResults);
    } else {
      result = filteredChapters.map((chapter) => ({
        id: chapter.id,
        name: chapter.name || 'Unknown Chapter',
        chapterNumber: chapter.chapter_number ?? undefined,
        highlights: (chapter.highlights || []) as Highlight[],
      }));
    }

    // Apply reverse order if enabled
    if (isReversed) {
      return [...result].reverse().map((chapter) => ({
        ...chapter,
        highlights: [...chapter.highlights].reverse(),
      }));
    }

    return result;
  }, [showSearchResults, filteredSearchResults, filteredChapters, isReversed]);

  // Flat array of all highlights for navigation
  const allHighlights = useMemo(() => {
    return chapters.flatMap((chapter) => chapter.highlights);
  }, [chapters]);

  // Find the current highlight and its index for the modal
  const currentHighlightIndex = useMemo(() => {
    if (!openHighlightId) return -1;
    return allHighlights.findIndex((h) => h.id === openHighlightId);
  }, [allHighlights, openHighlightId]);

  const currentHighlight = useMemo(() => {
    if (currentHighlightIndex === -1) return null;
    return allHighlights[currentHighlightIndex];
  }, [allHighlights, currentHighlightIndex]);

  // Handler for modal navigation - converts index to highlight ID
  const handleModalNavigate = useCallback(
    (newIndex: number) => {
      const newHighlight = allHighlights[newIndex];
      if (newHighlight) {
        handleNavigateHighlight(newHighlight.id);
      }
    },
    [allHighlights, handleNavigateHighlight]
  );

  // Compute empty message based on state
  const emptyMessage = useMemo(() => {
    if (showSearchResults) {
      return selectedTagId
        ? 'No highlights found matching your search with the selected tag.'
        : 'No highlights found matching your search.';
    }
    return selectedTagId
      ? 'No highlights found with the selected tag.'
      : 'No chapters found for this book.';
  }, [showSearchResults, selectedTagId]);

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

  return (
    <Box sx={{ minHeight: '100vh' }}>
      <ScrollToTopButton />
      <FadeInOut ekey={'book-title'}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3 }, py: 4 }}>
          {/* Mobile Layout */}
          {!isDesktop && (
            <>
              <BookTitle book={book} highlightCount={totalHighlights} />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mb: 3 }}>
                <HighlightTags
                  tags={book.highlight_tags || []}
                  tagGroups={book.highlight_tag_groups || []}
                  bookId={book.id}
                  selectedTag={selectedTagId}
                  onTagClick={handleTagClick}
                />
                <BookmarkList
                  bookmarks={book.bookmarks || []}
                  allHighlights={allHighlights}
                  onBookmarkClick={handleBookmarkClick}
                />
                <ChapterNav chapters={chapters} onChapterClick={handleChapterClick} />
              </Box>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 3 }}>
                <Box sx={{ flexGrow: 1 }}>
                  <SearchBar
                    onSearch={handleSearch}
                    placeholder="Search highlights..."
                    initialValue={searchText}
                  />
                </Box>
                <Tooltip title={isReversed ? 'Show oldest first' : 'Show newest first'}>
                  <IconButton
                    onClick={() => setIsReversed(!isReversed)}
                    sx={{
                      mt: '1px',
                      color: isReversed ? 'primary.main' : 'text.secondary',
                      '&:hover': { color: 'primary.main' },
                    }}
                  >
                    <SwapVertIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              <ChapterList
                chapters={chapters}
                bookId={book.id}
                bookmarksByHighlightId={bookmarksByHighlightId}
                allHighlights={allHighlights}
                isLoading={showSearchResults && isSearching}
                emptyMessage={emptyMessage}
                animationKey={`chapters-${showSearchResults ? 'search' : 'view'}-${selectedTagId ?? 'all'}`}
                openHighlightId={openHighlightId}
                onOpenHighlight={handleOpenHighlight}
                onCloseHighlight={handleCloseHighlight}
                onNavigateHighlight={handleNavigateHighlight}
              />
            </>
          )}

          {/* Desktop 3-Column Layout */}
          {isDesktop && (
            <>
              {/* Book Details + Search Bar - Centered with middle column */}
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: '250px 1fr 250px',
                  gap: 4,
                }}
              >
                <Box /> {/* Empty left spacer */}
                <Box>
                  <BookTitle book={book} highlightCount={totalHighlights} />
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 3 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <SearchBar
                        onSearch={handleSearch}
                        placeholder="Search highlights..."
                        initialValue={searchText}
                      />
                    </Box>
                    <Tooltip title={isReversed ? 'Show oldest first' : 'Show newest first'}>
                      <IconButton
                        onClick={() => setIsReversed(!isReversed)}
                        sx={{
                          mt: '1px',
                          color: isReversed ? 'primary.main' : 'text.secondary',
                          '&:hover': { color: 'primary.main' },
                        }}
                      >
                        <SwapVertIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
                <Box /> {/* Empty right spacer */}
              </Box>

              {/* 3-Column Content Grid */}
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: '250px 1fr 250px',
                  gap: 4,
                  alignItems: 'start',
                }}
              >
                {/* Left Column - Tags */}
                <Box sx={{ position: 'sticky', top: 80 }}>
                  <HighlightTags
                    tags={book.highlight_tags || []}
                    tagGroups={book.highlight_tag_groups || []}
                    bookId={book.id}
                    selectedTag={selectedTagId}
                    onTagClick={handleTagClick}
                  />
                </Box>

                {/* Middle Column - Chapter List */}
                <ChapterList
                  chapters={chapters}
                  bookId={book.id}
                  bookmarksByHighlightId={bookmarksByHighlightId}
                  allHighlights={allHighlights}
                  isLoading={showSearchResults && isSearching}
                  emptyMessage={emptyMessage}
                  animationKey={`chapters-${showSearchResults ? 'search' : 'view'}-${selectedTagId ?? 'all'}`}
                  openHighlightId={openHighlightId}
                  onOpenHighlight={handleOpenHighlight}
                  onCloseHighlight={handleCloseHighlight}
                  onNavigateHighlight={handleNavigateHighlight}
                />

                {/* Right Column - Bookmarks + Chapters */}
                <Box
                  sx={{
                    position: 'sticky',
                    top: 80,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 3,
                    maxHeight: 'calc(100vh - 80px - 32px)',
                    overflow: 'hidden',
                  }}
                >
                  <BookmarkList
                    bookmarks={book.bookmarks || []}
                    allHighlights={allHighlights}
                    onBookmarkClick={handleBookmarkClick}
                  />
                  <ChapterNav chapters={chapters} onChapterClick={handleChapterClick} />
                </Box>
              </Box>
            </>
          )}
        </Container>
      </FadeInOut>

      {/* Highlight Modal - rendered at page level for URL sync */}
      {currentHighlight && (
        <HighlightViewModal
          highlight={currentHighlight}
          bookId={book.id}
          open={!!openHighlightId}
          onClose={handleCloseHighlight}
          availableTags={tagsResponse?.tags || []}
          bookmarksByHighlightId={bookmarksByHighlightId}
          allHighlights={allHighlights}
          currentIndex={currentHighlightIndex}
          onNavigate={handleModalNavigate}
        />
      )}
    </Box>
  );
};
