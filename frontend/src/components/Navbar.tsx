import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box, Avatar, Tooltip, Menu, MenuItem } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { toggleSidebar, toggleDarkMode } from '../store/slices/uiSlice';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const dispatch = useAppDispatch();
  const darkMode = useAppSelector((state) => state.ui.darkMode);
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const handleLogout = async () => {
    handleClose();
    await logoutUser();
    navigate('/login');
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton edge="start" color="inherit" onClick={() => dispatch(toggleSidebar())} sx={{ mr: 2 }}>
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" noWrap sx={{ flexGrow: 1, fontWeight: 700 }}>
          EEG Seizure Detection
        </Typography>
        <IconButton color="inherit" onClick={() => dispatch(toggleDarkMode())} sx={{ mr: 1 }}>
          {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
        </IconButton>
        {user && (
          <Box>
            <Tooltip title={user.full_name || user.username}>
              <IconButton onClick={handleMenu} size="small" sx={{ p: 0 }}>
                <Avatar sx={{ bgcolor: 'secondary.main' }}>
                  {(user.full_name || user.username).charAt(0).toUpperCase()}
                </Avatar>
              </IconButton>
            </Tooltip>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
              <MenuItem onClick={() => { handleClose(); navigate('/profile'); }}>Profile</MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
