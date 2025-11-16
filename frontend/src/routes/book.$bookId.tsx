import { createFileRoute } from '@tanstack/react-router';
import { BookPage } from '../components/BookPage/BookPage';

type BookPageSearch = {
  search?: string;
  tagId?: number;
};
export const Route = createFileRoute('/book/$bookId')({
  component: BookPage,
  validateSearch: (search: Record<string, unknown>): BookPageSearch => {
    return {
      search: (search?.search as string) || undefined,
      tagId: (search?.tagId as number) || undefined,
    };
  },
});
