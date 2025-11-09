import { Box } from '@mui/material';
import type { BookWithHighlightCount } from '../../../api/generated/model';
import { BookCard } from './BookCard';

export interface BookListProps {
  books: BookWithHighlightCount[];
}

export const BookList = ({ books }: BookListProps) => {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          md: 'repeat(3, 1fr)',
          lg: 'repeat(4, 1fr)',
        },
        gap: 3,
      }}
    >
      {books.map((book) => (
        <BookCard key={book.id} book={book} />
      ))}
    </Box>
  );
};
