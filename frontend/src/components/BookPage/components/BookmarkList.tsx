import type { Bookmark, Highlight } from '@/api/generated/model';
import { SectionTitle } from '@/components/common/SectionTitle';
import { Bookmark as BookmarkIcon } from '@mui/icons-material';
import { Box, Typography } from '@mui/material';

interface BookmarkListProps {
  bookmarks: Bookmark[];
  allHighlights: Highlight[];
  onBookmarkClick: (highlightId: number) => void;
}

export const BookmarkList = ({ bookmarks, allHighlights, onBookmarkClick }: BookmarkListProps) => {
  // If no bookmarks, don't render anything
  if (!bookmarks || bookmarks.length === 0) {
    return null;
  }

  // Create a map of highlight IDs to highlights for quick lookup
  const highlightMap = new Map(allHighlights.map((h) => [h.id, h]));

  // Get highlights for bookmarks and sort by bookmark creation date (newest first)
  const bookmarkedHighlights = bookmarks
    .map((bookmark) => ({
      bookmark,
      highlight: highlightMap.get(bookmark.highlight_id),
    }))
    .filter((item) => item.highlight !== undefined)
    .sort((a, b) => new Date(b.bookmark.created_at).getTime() - new Date(a.bookmark.created_at).getTime());

  // Truncate highlight text to first few words
  const truncateText = (text: string, wordCount: number = 5): string => {
    const words = text.split(/\s+/);
    if (words.length <= wordCount) {
      return text;
    }
    return words.slice(0, wordCount).join(' ') + '...';
  };

  return (
    <Box>
      <SectionTitle>Bookmarks</SectionTitle>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
        {bookmarkedHighlights.map(({ bookmark, highlight }) => {
          if (!highlight) return null;

          const startsWithLowercase =
            highlight.text.length > 0 &&
            highlight.text[0] === highlight.text[0].toLowerCase() &&
            highlight.text[0] !== highlight.text[0].toUpperCase();

          const prefix = startsWithLowercase ? '...' : '';
          const truncatedText = prefix + truncateText(highlight.text);

          return (
            <Box
              key={bookmark.id}
              onClick={() => onBookmarkClick(highlight.id)}
              sx={{
                display: 'flex',
                alignItems: 'start',
                gap: 1,
                p: 1.5,
                borderRadius: 1,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                bgcolor: 'background.paper',
                border: 1,
                borderColor: 'divider',
                '@media (hover: hover)': {
                  '&:hover': {
                    bgcolor: 'action.hover',
                    borderColor: 'primary.main',
                  },
                },
              }}
            >
              <BookmarkIcon
                sx={{
                  fontSize: 16,
                  color: 'primary.main',
                  flexShrink: 0,
                  mt: 0.25,
                }}
              />
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.primary',
                    lineHeight: 1.5,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {truncatedText}
                </Typography>
                {highlight.page && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 0.5, display: 'block' }}
                  >
                    Page {highlight.page}
                  </Typography>
                )}
              </Box>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};
