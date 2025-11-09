import { createFileRoute } from '@tanstack/react-router';
import { LandingPage } from '../components/LandingPage/LandingPage';

export const Route = createFileRoute('/')({
  component: LandingPage,
});
