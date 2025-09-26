import React from "react";
import { Card, CardContent, Typography, Box } from "@mui/material";

export default function CardSection({ title, subtitle, children, onClick }) {
  return (
    <Card
      elevation={0}
      sx={{
        borderRadius: 3,
        boxShadow: "0 4px 12px rgba(70,115,192,0.08)",
        bgcolor: "#fff",
        cursor: "pointer",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        mb: 2,
        "&:hover": {
          boxShadow: "0 12px 40px rgba(70,115,192,0.15)",
          transform: "translateY(-4px) scale(1.02)",
        },
      }}
      onClick={onClick}
    >
      <CardContent sx={{ pb: 2.5 }}>
        <Typography
          variant="h5"
          fontWeight={700}
          sx={{ 
            color: "#1a1a1a", 
            mb: 0.5, 
            fontSize: "1.4em",
            letterSpacing: "-0.02em"
          }}
        >
          {title}
        </Typography>
        <Typography
          variant="body1"
          sx={{ 
            color: "#6b7280", 
            fontWeight: 500, 
            fontSize: "1.05em",
            mb: 2
          }}
        >
          {subtitle}
        </Typography>
        {children}
      </CardContent>
    </Card>
  );
}
