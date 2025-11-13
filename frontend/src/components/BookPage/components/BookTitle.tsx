import { BookmarkBorder as BookmarkIcon, Edit as EditIcon } from '@mui/icons-material';
import { Box, Chip, IconButton, Typography } from '@mui/material';
import { useState } from 'react';
import type { BookDetails } from '../../../api/generated/model';
import { BookCover } from '../../common/BookCover';
import { BookEditModal } from './BookEditModal';

export interface BookTitleProps {
  book: BookDetails;
  highlightCount: number;
}

export const BookTitle = ({ book, highlightCount }: BookTitleProps) => {
  const [editModalOpen, setEditModalOpen] = useState(false);

  const handleEdit = () => {
    setEditModalOpen(true);
  };

  return (
    <>
      <Box sx={{ mb: 4, display: 'flex', gap: 3, alignItems: 'flex-start' }}>
        {/* Book Cover - Outside card, on the left */}
        <Box sx={{ flexShrink: 0 }}>
          <BookCover
            coverPath={book.cover}
            title={book.title}
            height={280}
            width={200}
            objectFit="cover"
            sx={{ boxShadow: 3, borderRadius: 1 }}
          />
        </Box>

        {/* Book Info */}
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Title with Edit Button */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="h1" component="h1" sx={{ lineHeight: 1.3 }}>
              {book.title}
            </Typography>
            <IconButton
              onClick={handleEdit}
              size="small"
              sx={{
                '&:hover': {
                  bgcolor: 'action.hover',
                },
              }}
            >
              <EditIcon />
            </IconButton>
          </Box>

          <Typography
            variant="h2"
            sx={{ color: 'primary.main', fontWeight: 500, mb: 2 }}
            gutterBottom
          >
            {book.author || 'Unknown Author'}
          </Typography>

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              mb: book.tags && book.tags.length > 0 ? 2 : 0,
            }}
          >
            <BookmarkIcon sx={{ fontSize: 18, color: 'primary.main' }} />
            <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500 }}>
              {highlightCount} {highlightCount === 1 ? 'highlight' : 'highlights'}
            </Typography>
          </Box>

          {/* Tags */}
          {book.tags && book.tags.length > 0 && (
            <Box
              sx={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 1,
              }}
            >
              {book.tags.map((tag) => (
                <Chip
                  key={tag.id}
                  label={tag.name}
                  size="small"
                  variant="outlined"
                  sx={{ fontWeight: 500 }}
                />
              ))}
            </Box>
          )}
        </Box>
      </Box>

      {/* Edit Modal */}
      <BookEditModal
        book={{
          id: book.id,
          title: book.title,
          author: book.author,
          isbn: book.isbn,
          cover: book.cover,
          highlight_count: highlightCount,
          tags: book.tags || [],
          created_at: book.created_at,
          updated_at: book.updated_at,
        }}
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
      />
    </>
  );
};
