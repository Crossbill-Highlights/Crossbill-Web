import { Box, Container, Typography } from '@mui/material';

function App() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Crossbill
        </Typography>
        <Typography variant="body1">Your highlights management application</Typography>
      </Box>
    </Container>
  );
}

export default App;
