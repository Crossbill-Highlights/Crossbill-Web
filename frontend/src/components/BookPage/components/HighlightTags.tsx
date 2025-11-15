import { HighlightTagInBook } from '@/api/generated/model';
import { LocalOffer as TagIcon } from '@mui/icons-material';
import { Box, Chip, Typography } from '@mui/material';

interface HighlightTagsProps {
  tags: HighlightTagInBook[];
}

export const HighlightTags = ({ tags }: HighlightTagsProps) => {
  if (!tags || tags.length === 0) {
    return null;
  }

  // Sort tags by count (descending)
  const sortedTags = [...tags].sort((a, b) => b.count - a.count);

  return (
    <Box
      sx={{
        position: 'sticky',
        top: 24,
        p: 3,
        bgcolor: 'background.paper',
        borderRadius: 2,
        border: 1,
        borderColor: 'divider',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <TagIcon sx={{ fontSize: 20, color: 'primary.main' }} />
        <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
          Tags
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {sortedTags.map((tag) => (
          <Chip
            key={tag.id}
            label={`${tag.name} (${tag.count})`}
            size="small"
            variant="outlined"
            sx={{
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          />
        ))}
      </Box>
    </Box>
  );
};
