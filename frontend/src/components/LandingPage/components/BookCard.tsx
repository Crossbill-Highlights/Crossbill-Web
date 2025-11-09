import { Card, CardContent, Typography, Box } from '@mui/material';
import type { BookWithHighlightCount } from '../../../api/generated/model';

export interface BookCardProps {
  book: BookWithHighlightCount;
}

export const BookCard = ({ book }: BookCardProps) => {
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 3,
        },
      }}
    >
      <CardContent>
        <Typography variant="h6" component="h3" gutterBottom>
          {book.title}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {book.author || 'Unknown Author'}
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {book.highlight_count} {book.highlight_count === 1 ? 'highlight' : 'highlights'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
