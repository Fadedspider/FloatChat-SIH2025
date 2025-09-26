import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import {
  Download as DownloadIcon,
  Preview as PreviewIcon,
  Search as SearchIcon,
  TableChart as TableChartIcon,
} from "@mui/icons-material";
import Papa from "papaparse";

// List of all your CSV files from the public/csv folder
const csvFiles = [
  "1902669_prof.csv", "1902672_prof.csv", "1902674_prof.csv", "1902675_prof.csv", "1902767_prof.csv",
  "2902203_prof.csv", "2902206_prof.csv", "2902219_prof.csv", "2902222_prof.csv", "2902223_prof.csv",
  "2902272_prof.csv", "2902273_prof.csv", "2903892_prof.csv", "2903893_prof.csv", "2903954_prof.csv",
  "2903989_prof.csv", "3902573_prof.csv", "3902581_prof.csv", "3902630_prof.csv", "3902668_prof.csv",
  "3902669_prof.csv", "4903775_prof.csv", "4903776_prof.csv", "4903783_prof.csv", "4903838_prof.csv",
  "4903874_prof.csv", "5907082_prof.csv", "5907083_prof.csv", "5907084_prof.csv", "5907092_prof.csv",
  "5907138_prof.csv", "5907139_prof.csv", "5907179_prof.csv", "6990611_prof.csv", "6990613_prof.csv",
  "6990615_prof.csv", "6990705_prof.csv", "6990715_prof.csv", "7901130_prof.csv", "7901136_prof.csv",
  "7902170_prof.csv", "7902190_prof.csv", "7902243_prof.csv", "7902251_prof.csv"
];

export default function DataSources() {
  const [searchTerm, setSearchTerm] = useState("");
  const [previewData, setPreviewData] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Filter files based on search term
  const filteredFiles = csvFiles.filter(file => 
    file.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Extract float ID from filename
  const getFloatId = (filename) => {
    return filename.replace('_prof.csv', '');
  };

  // Get file size estimate (placeholder - you could implement actual file size fetching)
  const getFileSize = (filename) => {
    return "~2.5 MB"; // Placeholder
  };

  // Download CSV file
  const handleDownload = (filename) => {
    const link = document.createElement('a');
    link.href = `/csv/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Preview CSV file (first 10 rows)
  const handlePreview = (filename) => {
    setLoading(true);
    Papa.parse(`/csv/${filename}`, {
      download: true,
      header: true,
      complete: (result) => {
        setPreviewData({
          filename,
          columns: result.meta.fields || [],
          rows: result.data.slice(0, 10),
          totalRows: result.data.length
        });
        setPreviewOpen(true);
        setLoading(false);
      },
      error: (error) => {
        console.error('Error parsing CSV:', error);
        setLoading(false);
      }
    });
  };

  return (
    <Box sx={{ p: 4 }}>
      {/* Header */}
      <Paper elevation={2} sx={{ p: 4, mb: 4, borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TableChartIcon sx={{ fontSize: 40, color: '#176CA0', mr: 2 }} />
          <Box>
            <Typography variant="h4" fontWeight={700} color="#176CA0">
              ARGO Float Data Sources
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Browse and download {csvFiles.length} ARGO float profile datasets (CSV format)
            </Typography>
          </Box>
        </Box>
        
        {/* Search */}
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by Float ID (e.g., 1902669, 2902206...)"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          sx={{ mt: 2, maxWidth: 400 }}
        />
      </Paper>

      {/* Statistics */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <Chip 
          label={`${filteredFiles.length} Files Available`} 
          color="primary" 
          variant="outlined" 
          size="large"
        />
        <Chip 
          label="CSV Format" 
          color="secondary" 
          variant="outlined" 
          size="large"
        />
        <Chip 
          label="ARGO Profile Data" 
          color="success" 
          variant="outlined" 
          size="large"
        />
      </Box>

      {/* Data Table */}
      <Paper elevation={2} sx={{ borderRadius: 3 }}>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600, bgcolor: '#f8fafc' }}>
                  Float ID
                </TableCell>
                <TableCell sx={{ fontWeight: 600, bgcolor: '#f8fafc' }}>
                  Filename
                </TableCell>
                <TableCell sx={{ fontWeight: 600, bgcolor: '#f8fafc' }}>
                  File Size
                </TableCell>
                <TableCell sx={{ fontWeight: 600, bgcolor: '#f8fafc' }}>
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredFiles.map((filename, index) => (
                <TableRow 
                  key={filename} 
                  sx={{ 
                    '&:hover': { 
                      bgcolor: 'rgba(23, 108, 160, 0.04)' 
                    } 
                  }}
                >
                  <TableCell>
                    <Typography variant="h6" color="#176CA0" fontWeight={600}>
                      {getFloatId(filename)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {filename}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {getFileSize(filename)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Preview Data">
                        <IconButton 
                          size="small" 
                          onClick={() => handlePreview(filename)}
                          sx={{ color: '#176CA0' }}
                        >
                          <PreviewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download CSV">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDownload(filename)}
                          sx={{ color: '#28a745' }}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {filteredFiles.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              No files found matching "{searchTerm}"
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try searching with a different Float ID
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Preview Dialog */}
      <Dialog 
        open={previewOpen} 
        onClose={() => setPreviewOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6" color="#176CA0">
            Preview: {previewData?.filename}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Showing first 10 rows of {previewData?.totalRows} total records
          </Typography>
        </DialogTitle>
        <DialogContent>
          {previewData && (
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {previewData.columns.map((col) => (
                      <TableCell key={col} sx={{ fontWeight: 600, bgcolor: '#f8fafc' }}>
                        {col}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {previewData.rows.map((row, index) => (
                    <TableRow key={index}>
                      {previewData.columns.map((col) => (
                        <TableCell key={col}>
                          {row[col] || '-'}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>
            Close
          </Button>
          <Button 
            variant="contained" 
            onClick={() => handleDownload(previewData?.filename)}
            startIcon={<DownloadIcon />}
          >
            Download Full Dataset
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
