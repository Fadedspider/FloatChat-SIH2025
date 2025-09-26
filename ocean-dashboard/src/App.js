import { useState, useEffect } from "react";
import { 
  Box, 
  CssBaseline, 
  Tabs, 
  Tab, 
  Typography, 
  Paper,
  Grid,
  Chip,
  Button
} from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import MapIcon from "@mui/icons-material/Map";
import TimelineIcon from "@mui/icons-material/Timeline";
import WavesIcon from "@mui/icons-material/Waves";
import StorageIcon from "@mui/icons-material/Storage";
import ChatIcon from "@mui/icons-material/Chat";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import FloatMap from "./components/FloatMap";
import EnhancedChatInterface from "./components/EnhancedChatInterface";
import DataSources from "./components/DataSources";
import Analysis from "./components/Analysis"; // Import Analysis component
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from "recharts";
import dayjs from "dayjs";

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#176CA0',
    },
    background: {
      default: '#f5f8fb',
    },
  },
});

function CustomTabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3, height: 'calc(100vh - 180px)' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function App() {
  // TopBar navigation state (0: Dashboard, 1: Analysis, 2: Data Sources, 3: Help)
  const [activeTopTab, setActiveTopTab] = useState(0);
  
  // Dashboard sub-navigation state (for tabs within Dashboard)
  const [activeTab, setActiveTab] = useState(0);

  // Existing states
  const [variable, setVariable] = useState("temperature");
  const [datasetTypes, setDatasetTypes] = useState(["ARGO Floats"]);
  const [startDate, setStartDate] = useState(dayjs("2020-03-01"));
  const [endDate, setEndDate] = useState(dayjs("2020-05-30"));
  const [minLat, setMinLat] = useState("");
  const [maxLat, setMaxLat] = useState("");
  const [minLon, setMinLon] = useState("");
  const [maxLon, setMaxLon] = useState("");

  // Data states
  const [tsData, setTsData] = useState([]);
  const [floatData, setFloatData] = useState([]);
  const [profileData, setProfileData] = useState([]);
  const [summaryData, setSummaryData] = useState([]);
  const [allFloatsData, setAllFloatsData] = useState([]);

  // Loading states
  const [loadingTs, setLoadingTs] = useState(false);
  const [loadingFloats, setLoadingFloats] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);

  // Chat states
  const [chatHistory, setChatHistory] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  // Fetch data function
  const fetchData = () => {
    // Time Series Data
    setLoadingTs(true);
    fetch(
      `http://localhost:8000/daily-avg?var=${variable}&start_date=${startDate.format("YYYY-MM-DD")}&end_date=${endDate.format("YYYY-MM-DD")}`
    )
      .then((res) => res.json())
      .then((json) => {
        setTsData(json.data || []);
        setLoadingTs(false);
      })
      .catch(() => setLoadingTs(false));

    // Float Map Data
    setLoadingFloats(true);
    fetch(`http://localhost:8000/floats?limit=100`)
      .then((res) => res.json())
      .then((json) => {
        setFloatData(json.floats || []);
        setLoadingFloats(false);
      })
      .catch(() => setLoadingFloats(false));

    // Profile Data
    setLoadingProfile(true);
    const floatIds = ["2902206", "2902207", "2902208", "2902209"];
    
    const fetchProfile = async () => {
      for (const floatId of floatIds) {
        try {
          const response = await fetch(`http://localhost:8000/profile?float_id=${floatId}&cycle=1`);
          const json = await response.json();
          if (json.profile && json.profile.length > 0) {
            setProfileData(json.profile);
            setLoadingProfile(false);
            return;
          }
        } catch (error) {
          console.log(`No data for float ${floatId}`);
        }
      }
      setProfileData([]);
      setLoadingProfile(false);
    };
    
    fetchProfile();

    // Summary Data
    setLoadingSummary(true);
    fetch(`http://localhost:8000/floats?limit=500`)
      .then((res) => res.json())
      .then((json) => {
        setAllFloatsData(json.floats || []);
        setSummaryData((json.floats || []).slice(0, 20));
        setLoadingSummary(false);
      })
      .catch(() => setLoadingSummary(false));
  };

  // Ask question function
  const askQuestion = async (question) => {
    setIsAsking(true);
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const result = await response.json();
      
      setChatHistory(prev => [...prev, {
        question,
        result,
        timestamp: new Date()
      }]);
    } catch (error) {
      setChatHistory(prev => [...prev, {
        question,
        result: { 
          success: false, 
          error: 'Connection error',
          natural_language_response: 'Sorry, I could not connect to the server.'
        },
        timestamp: new Date()
      }]);
    }
    setIsAsking(false);
    setCurrentQuestion("");
  };

  useEffect(() => {
    // Only fetch data when on Dashboard tab
    if (activeTopTab === 0) {
      fetchData();
    }
  }, [activeTopTab, variable, startDate, endDate]);

  const applyFilters = () => {
    fetchData();
  };

  // TopBar navigation handler
  const handleTopTabChange = (event, newValue) => {
    console.log('TopTab changed to:', newValue);
    setActiveTopTab(newValue);
  };

  // Dashboard internal tabs handler
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Render Dashboard content (when activeTopTab === 0)
  const renderDashboard = () => (
    <Box sx={{ display: "flex", pt: 9 }}>
      <Sidebar
        variable={variable}
        setVariable={setVariable}
        datasetTypes={datasetTypes}
        setDatasetTypes={setDatasetTypes}
        startDate={startDate}
        setStartDate={setStartDate}
        endDate={endDate}
        setEndDate={setEndDate}
        minLat={minLat}
        setMinLat={setMinLat}
        maxLat={maxLat}
        setMaxLat={setMaxLat}
        minLon={minLon}
        setMinLon={setMinLon}
        maxLon={maxLon}
        setMaxLon={setMaxLon}
        applyFilters={applyFilters}
      />
      
      <Box sx={{ flexGrow: 1, bgcolor: "#f5f8fb" }}>
        {/* Dashboard Header with Stats */}
        <Paper 
          elevation={0} 
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            backgroundColor: '#fff',
            px: 3,
            pt: 2
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" fontWeight={700} color="#176CA0">
              FloatChat Enhanced
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Chip label={`${allFloatsData.length} Active Floats`} color="primary" variant="outlined" />
              <Chip label={`${variable.charAt(0).toUpperCase() + variable.slice(1)} Analysis`} color="secondary" variant="outlined" />
              <Chip label="AI Powered" color="success" variant="outlined" />
            </Box>
          </Box>
          
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            sx={{
              '& .MuiTab-root': {
                minHeight: '60px',
                fontSize: '1rem',
                fontWeight: 600,
                textTransform: 'none',
              }
            }}
          >
            <Tab 
              icon={<MapIcon />} 
              iconPosition="start"
              label="Interactive Map" 
            />
            <Tab 
              icon={<WavesIcon />} 
              iconPosition="start"
              label="Depth Profile" 
            />
            <Tab 
              icon={<TimelineIcon />} 
              iconPosition="start"
              label="Time Series" 
            />
            <Tab 
              icon={<StorageIcon />} 
              iconPosition="start"
              label="Float Database" 
            />
            <Tab 
              icon={<ChatIcon />} 
              iconPosition="start"
              label="AI Assistant" 
            />
          </Tabs>
        </Paper>

        {/* Dashboard Tab Panels */}
        <CustomTabPanel value={activeTab} index={0}>
          <Paper elevation={2} sx={{ height: '100%', borderRadius: 3, overflow: 'hidden' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #e0e6ed', bgcolor: '#f8fafc' }}>
              <Typography variant="h5" fontWeight={600} color="#176CA0" gutterBottom>
                Global ARGO Float Network
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Real-time positions of {floatData.length} autonomous oceanographic floats collecting temperature, salinity, and pressure data
              </Typography>
            </Box>
            <Box sx={{ height: 'calc(100% - 100px)', p: 2 }}>
              {loadingFloats ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <Typography variant="h6">Loading float data...</Typography>
                </Box>
              ) : (
                <FloatMap floats={floatData} />
              )}
            </Box>
          </Paper>
        </CustomTabPanel>

        <CustomTabPanel value={activeTab} index={1}>
          <Paper elevation={2} sx={{ height: '100%', borderRadius: 3, overflow: 'hidden' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #e0e6ed', bgcolor: '#f8fafc' }}>
              <Typography variant="h5" fontWeight={600} color="#176CA0" gutterBottom>
                Ocean Depth Profile Analysis
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Temperature and salinity variations with ocean depth from ARGO float measurements
              </Typography>
            </Box>
            <Box sx={{ height: 'calc(100% - 100px)', p: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {loadingProfile ? (
                <Typography variant="h6">Loading profile data...</Typography>
              ) : profileData.length > 0 ? (
                <ResponsiveContainer width="95%" height="95%">
                  <ScatterChart data={profileData}>
                    <CartesianGrid stroke="#e0e6ed" strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="temperature" 
                      name="Temperature" 
                      unit="°C"
                      type="number"
                      domain={['dataMin - 1', 'dataMax + 1']}
                      fontSize={14}
                    />
                    <YAxis
                      dataKey="pressure"
                      name="Pressure"
                      unit="dbar"
                      reversed={true}
                      type="number"
                      fontSize={14}
                    />
                    <Tooltip 
                      cursor={{ strokeDasharray: "3 3" }}
                      formatter={(value, name) => [
                        `${value}${name === 'temperature' ? '°C' : name === 'pressure' ? ' dbar' : ''}`,
                        name
                      ]}
                    />
                    <Scatter name="Ocean Data" data={profileData} fill="#176CA0" />
                  </ScatterChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No profile data available
                  </Typography>
                  <Typography variant="body1">
                    Try adjusting the date range or selecting different parameters.
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </CustomTabPanel>

        <CustomTabPanel value={activeTab} index={2}>
          <Paper elevation={2} sx={{ height: '100%', borderRadius: 3, overflow: 'hidden' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #e0e6ed', bgcolor: '#f8fafc' }}>
              <Typography variant="h5" fontWeight={600} color="#176CA0" gutterBottom>
                {variable.charAt(0).toUpperCase() + variable.slice(1)} Time Series
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Daily average {variable} evolution from {startDate.format("MMM DD, YYYY")} to {endDate.format("MMM DD, YYYY")}
              </Typography>
            </Box>
            <Box sx={{ height: 'calc(100% - 100px)', p: 2 }}>
              {loadingTs ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <Typography variant="h6">Loading time series data...</Typography>
                </Box>
              ) : tsData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={tsData}>
                    <Line
                      type="monotone"
                      dataKey="avg_value"
                      stroke="#176CA0"
                      strokeWidth={3}
                      dot={{ fill: '#176CA0', strokeWidth: 2, r: 5 }}
                    />
                    <CartesianGrid stroke="#e0e6ed" strokeDasharray="3 3" />
                    <XAxis dataKey="day" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <Typography variant="h6">No data found for these filters.</Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </CustomTabPanel>

        <CustomTabPanel value={activeTab} index={3}>
          <Paper elevation={2} sx={{ height: '100%', borderRadius: 3, overflow: 'hidden' }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #e0e6ed', bgcolor: '#f8fafc' }}>
              <Typography variant="h5" fontWeight={600} color="#176CA0" gutterBottom>
                ARGO Floats Database
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {allFloatsData.length} autonomous floats collecting oceanographic data worldwide
              </Typography>
            </Box>
            <Box sx={{ 
              height: 'calc(100% - 100px)', 
              overflowY: 'auto',
              p: 2,
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: '#f1f1f1',
                borderRadius: '4px',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#176CA0',
                borderRadius: '4px',
              },
            }}>
              <Grid container spacing={2}>
                {allFloatsData.map((float, index) => (
                  <Grid item xs={12} md={6} lg={4} key={float.float_id}>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 3,
                        borderRadius: 2,
                        backgroundColor: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        '&:hover': {
                          backgroundColor: '#e1f5fe',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 8px 25px rgba(23, 108, 160, 0.15)'
                        },
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <Typography variant="h6" fontWeight={600} color="#176CA0" gutterBottom>
                        Float {float.float_id}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Position:</strong> {float.avg_lat?.toFixed(4)}°, {float.avg_lon?.toFixed(4)}°
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        <strong>Observations:</strong> {float.total_observations}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Last Update:</strong> {new Date(float.last_observation).toLocaleDateString()}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Paper>
        </CustomTabPanel>

        <CustomTabPanel value={activeTab} index={4}>
          <Paper elevation={2} sx={{ height: '100%', borderRadius: 3, overflow: 'hidden' }}>
            <EnhancedChatInterface />
          </Paper>
        </CustomTabPanel>
      </Box>
    </Box>
  );

  // Render Analysis content (when activeTopTab === 1)
  const renderAnalysis = () => (
    <Box sx={{ pt: 9, bgcolor: "#f5f8fb", minHeight: "100vh" }}>
      <Analysis />
    </Box>
  );

  // Render DataSources content (when activeTopTab === 2)
  const renderDataSources = () => (
    <Box sx={{ pt: 9, bgcolor: "#f5f8fb", minHeight: "100vh" }}>
      <DataSources />
    </Box>
  );

  // Render Help content (when activeTopTab === 3)
  const renderHelp = () => (
    <Box sx={{ pt: 9, bgcolor: "#f5f8fb", minHeight: "100vh" }}>
      <Box sx={{ p: 4 }}>
        <Paper elevation={2} sx={{ p: 4, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight={700} color="#176CA0" gutterBottom>
            Help & Documentation
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            FloatChat user guide and API documentation...
          </Typography>
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>Getting Started</Typography>
            <Typography variant="body2" color="text.secondary">
              1. Navigate through different sections using the top navigation bar<br/>
              2. Use the Dashboard for interactive data visualization<br/>
              3. Access ARGO float data files in the Data Sources section<br/>
              4. Get AI assistance for ocean data queries<br/>
              5. Use the Analysis section for advanced statistical analysis
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Box>
  );

  // Main content router based on activeTopTab
  const renderMainContent = () => {
    switch (activeTopTab) {
      case 0:
        return renderDashboard();
      case 1:
        return renderAnalysis();
      case 2:
        return renderDataSources();
      case 3:
        return renderHelp();
      default:
        return renderDashboard();
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box>
        <TopBar 
          activeTopTab={activeTopTab}
          onTopTabChange={handleTopTabChange}
        />
        {renderMainContent()}
      </Box>
    </ThemeProvider>
  );
}
