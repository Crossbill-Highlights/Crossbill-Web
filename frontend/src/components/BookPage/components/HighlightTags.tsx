import { HighlightTagGroupInBook, HighlightTagInBook } from '@/api/generated/model';
import {
  Close as CloseIcon,
  LocalOffer as TagIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { Box, Chip, IconButton, Typography } from '@mui/material';
import { useState } from 'react';
import { HighlightTagsModal } from './HighlightTagsModal';

interface HighlightTagsProps {
  tags: HighlightTagInBook[];
  tagGroups: HighlightTagGroupInBook[];
  bookId: number;
  selectedTag?: number | null;
  onTagClick: (tagId: number | null) => void;
}

const HighlightTagsHeading = ({
  selectedTag,
  onTagClick,
  onManageClick,
}: {
  onTagClick: HighlightTagsProps['onTagClick'];
  selectedTag: HighlightTagsProps['selectedTag'];
  onManageClick: () => void;
}) => (
  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <TagIcon sx={{ fontSize: 20, color: 'primary.main' }} />
      <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
        Tags
      </Typography>
    </Box>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <IconButton
        size="small"
        onClick={onManageClick}
        title="Manage tag groups"
        sx={{ color: 'text.secondary' }}
      >
        <SettingsIcon fontSize="small" />
      </IconButton>
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
  </Box>
);

export const HighlightTags = ({
  tags,
  tagGroups,
  bookId,
  selectedTag,
  onTagClick,
}: HighlightTagsProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Sort tags alphabetically
  const sortedTags = [...tags].sort((a, b) => a.name.localeCompare(b.name));

  // Group tags by tag_group_id
  const ungroupedTags = sortedTags.filter((tag) => !tag.tag_group_id);
  const groupedTags = tagGroups.map((group) => ({
    group,
    tags: sortedTags.filter((tag) => tag.tag_group_id === group.id),
  }));

  const renderTag = (tag: HighlightTagInBook) => (
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
  );

  return (
    <>
      <Box
        sx={{
          position: 'sticky',
          top: 24,
        }}
      >
        <HighlightTagsHeading
          selectedTag={selectedTag}
          onTagClick={onTagClick}
          onManageClick={() => setIsModalOpen(true)}
        />

        {tags && tags.length > 0 ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Ungrouped tags */}
            {ungroupedTags.length > 0 && (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {ungroupedTags.map(renderTag)}
              </Box>
            )}

            {/* Grouped tags */}
            {groupedTags.map(
              ({ group, tags: groupTags }) =>
                groupTags.length > 0 && (
                  <Box key={group.id}>
                    <Typography
                      variant="subtitle2"
                      sx={{
                        fontSize: '0.875rem',
                        fontWeight: 600,
                        color: 'text.secondary',
                        mb: 1,
                      }}
                    >
                      {group.name}
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {groupTags.map(renderTag)}
                    </Box>
                  </Box>
                )
            )}
          </Box>
        ) : (
          <Typography variant="body1" color="text.secondary">
            No tagged highlights.
          </Typography>
        )}
      </Box>

      <HighlightTagsModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        bookId={bookId}
        tagGroups={tagGroups}
      />
    </>
  );
};
