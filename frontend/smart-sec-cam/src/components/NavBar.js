import { useNavigate } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2e2e2e',
    },
    secondary: {
      main: "#1976d2",
    }
  },
});

export default function ButtonAppBar(props) {
  const navigate = useNavigate();

  function goToVideosPage() {
    navigate("/videos", { state: { token: props.token } });
  }

  return (
    <Box sx={{ display: 'flex' }}> {/* Removed flexGrow: 1 */}
      <ThemeProvider theme={darkTheme}>
        <AppBar position="static" sx={{ height: '48px' }}>
          <Toolbar
            variant="dense"
            color="primary"
            sx={{ minHeight: '48px', padding: '0 12px' }}
          >
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography
              variant="h6"
              component="div"
              sx={{ flexGrow: 1, fontSize: '1rem' }}
            >
              Smart Security Camera
            </Typography>
            <Button onClick={goToVideosPage} variant="contained" color="secondary">
              Videos
            </Button>
          </Toolbar>
        </AppBar>
      </ThemeProvider>
    </Box>
  );
}