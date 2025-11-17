import { HighlightTagInBook } from '@/api/generated/model';
import { Close as CloseIcon, LocalOffer as TagIcon } from '@mui/icons-material';
import { Box, Chip, IconButton, Typography } from '@mui/material';

interface HighlightTagsProps {
  tags: HighlightTagInBook[];
  selectedTag?: number | null;
  onTagClick: (tagId: number | null) => void;
}

const HighlightTagsHeading = ({
  selectedTag,
  onTagClick,
}: {
  onTagClick: HighlightTagsProps['onTagClick'];
  selectedTag: HighlightTagsProps['selectedTag'];
}) => (
  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <TagIcon sx={{ fontSize: 20, color: 'primary.main' }} />
      <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
        Tags
      </Typography>
    </Box>
    <IconButton
      size="small"
      onClick={() => onTagClick(null)}
      title="Clear filter"
      sx={{
        visibility: selectedTag ? 'visible' : 'hidden',
      }}
    >
      <CloseIcon fontSize="small" />
    </IconButton>
  </Box>
);

export const HighlightTags = ({ tags, selectedTag, onTagClick }: HighlightTagsProps) => {
  // Sort tags alphabetically
  const sortedTags = [...tags].sort((a, b) => a.name.localeCompare(b.name));

  return (
    <Box
      sx={{
        position: 'sticky',
        top: 24,
      }}
    >
      <HighlightTagsHeading selectedTag={selectedTag} onTagClick={onTagClick} />
      {tags && tags.length > 0 ? (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {sortedTags.map((tag) => (
            <Chip
              key={tag.id}
              label={tag.name}
              size="small"
              variant={selectedTag === tag.id ? 'filled' : 'outlined'}
              color={selectedTag === tag.id ? 'primary' : 'default'}
              onClick={() => onTagClick(selectedTag === tag.id ? null : tag.id)}
              sx={{
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                py: 0.25,
                px: 0.5,
                borderColor: selectedTag === tag.id ? undefined : 'divider',
                '&:hover': {
                  bgcolor: selectedTag === tag.id ? 'primary.dark' : 'action.hover',
                  borderColor: selectedTag === tag.id ? undefined : 'secondary.light',
                  transform: 'translateY(-1px)',
                },
              }}
            />
          ))}
        </Box>
      ) : (
        <Typography variant="body1" color="text.secondary">
          No tagged highlights.
        </Typography>
      )}
    </Box>
  );
};
