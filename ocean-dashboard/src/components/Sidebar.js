import React from "react";
import {
  Box,
  Typography,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Select,
  MenuItem,
  Button,
  Divider,
  TextField,
} from "@mui/material";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider, DatePicker } from "@mui/x-date-pickers";
import dayjs from "dayjs";

export default function Sidebar({
  variable,
  setVariable,
  datasetTypes,
  setDatasetTypes,
  startDate,
  setStartDate,
  endDate,
  setEndDate,
  minLat,
  setMinLat,
  maxLat,
  setMaxLat,
  minLon,
  setMinLon,
  maxLon,
  setMaxLon,
  applyFilters,
}) {
  return (
    <Box
      sx={{
        width: 300,
        p: 3,
        bgcolor: "#fff",
        borderRight: "1px solid #eef1f6",
        height: "100vh",
      }}
    >
      <Typography variant="h6" fontWeight={700} sx={{ mb: 3, letterSpacing: 0.02 }}>
        Query Filters
      </Typography>

      <Typography fontWeight={600} mb={1} sx={{ fontSize: "1.13em" }}>
        Time Range
      </Typography>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <DatePicker
          label="Start Date"
          value={startDate}
          onChange={(v) => setStartDate(v)}
          format="DD-MM-YYYY"
          sx={{ mb: 2, width: "100%" }}
          slotProps={{ textField: { variant: "outlined", fullWidth: true } }}
        />
        <DatePicker
          label="End Date"
          value={endDate}
          onChange={(v) => setEndDate(v)}
          format="DD-MM-YYYY"
          sx={{ mb: 3, width: "100%" }}
          slotProps={{ textField: { variant: "outlined", fullWidth: true } }}
        />
      </LocalizationProvider>

      <Typography fontWeight={600} mb={1} sx={{ fontSize: "1.13em" }}>
        Geographic Region
      </Typography>
      <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
        <TextField
          label="Min Lat"
          value={minLat}
          onChange={e => setMinLat(e.target.value)}
          size="small"
          sx={{ width: "50%" }}
        />
        <TextField
          label="Max Lat"
          value={maxLat}
          onChange={e => setMaxLat(e.target.value)}
          size="small"
          sx={{ width: "50%" }}
        />
      </Box>
      <Box sx={{ display: "flex", gap: 1, mb: 3 }}>
        <TextField
          label="Min Lon"
          value={minLon}
          onChange={e => setMinLon(e.target.value)}
          size="small"
          sx={{ width: "50%" }}
        />
        <TextField
          label="Max Lon"
          value={maxLon}
          onChange={e => setMaxLon(e.target.value)}
          size="small"
          sx={{ width: "50%" }}
        />
      </Box>

      <Typography fontWeight={600} mb={1} sx={{ fontSize: "1.13em" }}>
        Dataset Type
      </Typography>
      <FormGroup sx={{ mb: 3 }}>
        {["ARGO Floats", "BGC Parameters", "Satellite Data"].map((name) => (
          <FormControlLabel
            key={name}
            control={
              <Checkbox
                checked={datasetTypes.includes(name)}
                onChange={() => {
                  if (datasetTypes.includes(name)) {
                    setDatasetTypes(datasetTypes.filter((d) => d !== name));
                  } else {
                    setDatasetTypes([...datasetTypes, name]);
                  }
                }}
              />
            }
            label={name}
            sx={{ fontWeight: 500 }}
          />
        ))}
      </FormGroup>

      <Typography fontWeight={600} mb={1} sx={{ fontSize: "1.13em" }}>
        Parameters
      </Typography>
      <Select
        fullWidth
        value={variable}
        onChange={(e) => setVariable(e.target.value)}
        sx={{ mb: 3 }}
      >
        {["Temperature", "Salinity", "Pressure", "Oxygen"].map((item) => (
          <MenuItem key={item} value={item.toLowerCase()}>
            {item}
          </MenuItem>
        ))}
      </Select>

      <Button
        size="large"
        variant="contained"
        sx={{
          mt: 2,
          height: 48,
          bgcolor: "#176CA0",
          fontWeight: 700,
          fontSize: "1.1em",
          "&:hover": { bgcolor: "#215f97" }
        }}
        fullWidth
        onClick={applyFilters}
      >
        Apply Filters
      </Button>
    </Box>
  );
}
