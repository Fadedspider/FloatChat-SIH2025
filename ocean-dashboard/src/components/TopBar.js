import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  Box,
  IconButton,
  Avatar,
} from "@mui/material";
import NotificationsNoneOutlinedIcon from "@mui/icons-material/NotificationsNoneOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";

// Inline SVG logo for OceanScope
const oceanLogoSVG = (
  <svg width="38" height="38" viewBox="0 0 32 32" fill="none">
    <rect width="32" height="32" rx="8" fill="#3490eb"/>
    <path d="M8.8 12.5c2.6 0 2.6-2 5.3-2s2.6 2 5.2 2c2.6 0 2.6-2 5.3-2" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"/>
    <path d="M8.8 17c2.6 0 2.6-2 5.3-2s2.6 2 5.2 2c2.6 0 2.6-2 5.3-2" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"/>
    <path d="M8.8 21.5c2.6 0 2.6-2 5.3-2s2.6 2 5.2 2c2.6 0 2.6-2 5.3-2" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"/>
  </svg>
);

export default function TopBar({ activeTopTab, onTopTabChange }) {
  // Handle tab change - this is the key fix
  const handleTabChange = (event, newValue) => {
    console.log("Tab clicked:", newValue);
    if (onTopTabChange) {
      onTopTabChange(event, newValue); // Pass both event and value
    }
  };

  return (
    <AppBar
      position="fixed"
      color="inherit"
      elevation={0}
      sx={{
        borderBottom: "1px solid #eee",
        bgcolor: "#fff",
        minHeight: 68,
        zIndex: 1300,
      }}
    >
      <Toolbar
        sx={{
          justifyContent: "space-between",
          minHeight: 68,
          px: 3,
        }}
      >
        {/* Logo Section */}
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Box sx={{ mr: 1 }}>{oceanLogoSVG}</Box>
          <Typography
            variant="h5"
            sx={{
              color: "#1e2231",
              fontWeight: 700,
              letterSpacing: 0.01,
              fontSize: "1.27em",
            }}
          >
            FloatChat
          </Typography>
        </Box>

        {/* Navigation Tabs */}
        <Tabs
          value={activeTopTab || 0}
          onChange={handleTabChange}
          sx={{
            ".MuiTabs-indicator": { bgcolor: "#3490eb", height: 3 },
            ".MuiTab-root": {
              textTransform: "none",
              fontWeight: 600,
              fontSize: "1.1em",
              mx: 0.8,
              color: "#6c757d",
              "&.Mui-selected": { color: "#23263A" },
              cursor: "pointer",
              minWidth: 100,
              "&:hover": {
                color: "#23263A",
                backgroundColor: "rgba(52, 144, 235, 0.1)",
              }
            },
          }}
        >
          <Tab label="Dashboard" />
          <Tab label="Analysis" />
          <Tab label="Data Sources" />
          <Tab label="Help" />
        </Tabs>

        {/* Right Side Icons */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton>
            <NotificationsNoneOutlinedIcon fontSize="medium" sx={{ color: "#6c757d" }} />
          </IconButton>
          <IconButton>
            <SettingsOutlinedIcon fontSize="medium" sx={{ color: "#6c757d" }} />
          </IconButton>
          <Avatar sx={{ bgcolor: "#eef2f7", color: "#6c757d", width: 36, height: 36 }}>
            <PersonOutlineOutlinedIcon />
          </Avatar>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
