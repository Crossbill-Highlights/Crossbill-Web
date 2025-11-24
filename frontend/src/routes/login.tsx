import { createFileRoute } from '@tanstack/react-router';
import { LoginPage } from '../components/LoginPage/LoginPage';

export const Route = createFileRoute('/login')({
  component: LoginPage,
});
