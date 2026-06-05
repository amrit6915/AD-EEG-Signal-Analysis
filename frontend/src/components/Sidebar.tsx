import React from 'react';
import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Toolbar } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import UploadIcon from '@mui/icons-material/Upload';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import BarChartIcon from '@mui/icons-material/BarChart';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Detection', icon: <SearchIcon />, path: '/detection' },
  { text: 'Files', icon: <UploadIcon />, path: '/files' },
  { text: 'Results', icon: <HistoryIcon />, path: '/results' },
  { text: 'Analytics', icon: <BarChartIcon />, path: '/analytics' },
  { text: 'Profile', icon: <PersonIcon />, path: '/profile' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const open = useAppSelector((state) => state.ui.sidebarOpen);

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <List sx={{ mt: 1 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            selected={location.pathname === item.path || location.pathname.startsWith(item.path + '/')}
            onClick={() => navigate(item.path)}
            sx={{
              mx: 1,
              borderRadius: 2,
              mb: 0.5,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
                '& .MuiListItemIcon-root': { color: 'white' },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}
