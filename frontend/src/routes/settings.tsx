import { createFileRoute } from '@tanstack/react-router';
import { SettingsPage } from '../components/SettingsPage/SettingsPage';

export const Route = createFileRoute('/settings')({
  component: SettingsPage,
});
