import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Avatar,
  Fade,
  Tooltip,
  Switch,
  FormControlLabel,
  Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import PsychologyIcon from '@mui/icons-material/Psychology';
import DatabaseIcon from '@mui/icons-material/Storage';
import { keyframes } from '@mui/system';

// Typing animation
const typing = keyframes`
  0%, 60%, 100% {
    transform: initial;
  }
  30% {
    transform: translateY(-10px);
  }
`;

const TypingIndicator = ({ useAdvancedAI }) => (
  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2 }}>
    <Avatar sx={{ 
      width: 32, 
      height: 32, 
      bgcolor: useAdvancedAI ? '#176CA0' : '#4caf50'
    }}>
      {useAdvancedAI ? <PsychologyIcon fontSize="small" /> : <DatabaseIcon fontSize="small" />}
    </Avatar>
    <Box sx={{ display: 'flex', gap: 0.5, ml: 1 }}>
      {[0, 1, 2].map((i) => (
        <Box
          key={i}
          sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            bgcolor: useAdvancedAI ? '#176CA0' : '#4caf50',
            animation: `${typing} 1.4s infinite ease-in-out`,
            animationDelay: `${i * 0.16}s`,
          }}
        />
      ))}
    </Box>
    <Typography variant="body2" color="text.secondary">
      {useAdvancedAI ? 'AI is thinking...' : 'Querying database...'}
    </Typography>
  </Box>
);

export default function EnhancedChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      text: "Hello! I'm your enhanced FloatChat assistant with both database queries and advanced AI. Toggle between modes and ask me anything about ocean data!",
      timestamp: new Date(),
      source: 'system'
    }
  ]);
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useAdvancedAI, setUseAdvancedAI] = useState(false);
  const [aiStatus, setAiStatus] = useState('checking');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkAIStatus();
    const interval = setInterval(checkAIStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkAIStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/ai-status');
      const data = await response.json();
      setAiStatus(data.status);
      
      // Auto-enable AI if it becomes available
      if (data.status === 'loaded' && !useAdvancedAI) {
        console.log("AI model is now available!");
      }
    } catch (error) {
      setAiStatus('error');
      setUseAdvancedAI(false); // Force to database mode if AI is unavailable
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput('');
    setIsLoading(true);

    try {
      let response, data;
      
      if (useAdvancedAI && aiStatus === 'loaded') {
        // Use advanced AI
        response = await fetch('http://localhost:8000/ai-chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: currentInput })
        });
        
        data = await response.json();
        
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          text: data.ai_answer || data.error || "No response",
          timestamp: new Date(),
          source: 'advanced_ai',
          model: data.model_type,
          confidence: data.confidence,
          success: data.success
        };
        
        setMessages(prev => [...prev, aiMessage]);
        
      } else {
        // Fall back to database query system
        response = await fetch('http://localhost:8000/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: currentInput })
        });
        
        data = await response.json();
        
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          text: data.natural_language_response || "I processed your query using the database.",
          timestamp: new Date(),
          source: 'database',
          sql: data.sql,
          dataCount: data.row_count,
          success: data.success
        };
        
        setMessages(prev => [...prev, aiMessage]);
      }

    } catch (error) {
      console.error('Error:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        text: `Sorry, I encountered an error: ${error.message}. Please make sure the API server is running.`,
        timestamp: new Date(),
        source: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const quickQuestions = [
    "What is the average ocean temperature?",
    "How many ARGO floats are active?", 
    "Show me recent observations",
    "What is the salinity data?",
    "Ocean conditions in Bay of Bengal",
    "Show me float positions",
    "What is the pressure at depth?"
  ];

  const handleQuickQuestion = (question) => {
    setInput(question);
  };

  return (
    <Paper elevation={3} sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column', 
      borderRadius: 3, 
      overflow: 'hidden',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    }}>
      
      {/* Header with AI Toggle */}
      <Box sx={{ 
        p: 3, 
        borderBottom: '1px solid #e0e6ed', 
        background: 'linear-gradient(135deg, #176CA0 0%, #1976d2 100%)', 
        color: 'white' 
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ 
              bgcolor: 'rgba(255,255,255,0.2)',
              width: 45,
              height: 45
            }}>
              {useAdvancedAI ? <PsychologyIcon /> : <DatabaseIcon />}
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                FloatChat Enhanced
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {useAdvancedAI ? 'Advanced AI Mode' : 'Database Query Mode'}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label={
                aiStatus === 'loaded' ? 'AI Ready' : 
                aiStatus === 'checking' ? 'Checking AI' : 
                aiStatus === 'not_loaded' ? 'AI Loading' : 
                'Database Only'
              }
              size="small"
              color={aiStatus === 'loaded' ? 'success' : 'warning'}
              variant="outlined"
              sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={useAdvancedAI}
                  onChange={(e) => setUseAdvancedAI(e.target.checked)}
                  disabled={aiStatus !== 'loaded'}
                  sx={{ 
                    '& .MuiSwitch-thumb': { bgcolor: 'white' },
                    '& .MuiSwitch-track': { opacity: 0.5 }
                  }}
                />
              }
              label="Advanced AI"
              sx={{ color: 'white', m: 0 }}
            />
          </Box>
        </Box>
      </Box>

      {/* Quick Questions */}
      <Box sx={{ p: 2, borderBottom: '1px solid #e0e6ed', bgcolor: '#f8fafc' }}>
        <Typography variant="body2" color="text.secondary" gutterBottom fontWeight={600}>
          Quick Questions:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {quickQuestions.map((question, index) => (
            <Chip
              key={index}
              label={question}
              variant="outlined"
              size="small"
              clickable
              onClick={() => handleQuickQuestion(question)}
              sx={{ 
                '&:hover': { 
                  bgcolor: useAdvancedAI ? '#e3f2fd' : '#e8f5e8',
                  borderColor: useAdvancedAI ? '#176CA0' : '#4caf50'
                },
                mb: 0.5
              }}
            />
          ))}
        </Box>
      </Box>

      {/* Messages */}
      <Box sx={{ 
        flexGrow: 1, 
        overflowY: 'auto', 
        p: 2,
        bgcolor: '#fafbfc',
        '&::-webkit-scrollbar': { width: '8px' },
        '&::-webkit-scrollbar-track': { background: '#f1f1f1', borderRadius: '4px' },
        '&::-webkit-scrollbar-thumb': { 
          background: useAdvancedAI ? '#176CA0' : '#4caf50', 
          borderRadius: '4px' 
        },
      }}>
        {messages.map((message) => (
          <Fade in={true} key={message.id} timeout={500}>
            <Box sx={{ 
              display: 'flex', 
              mb: 3,
              justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start'
            }}>
              {message.type === 'ai' && (
                <Avatar sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: 
                    message.source === 'advanced_ai' ? '#176CA0' : 
                    message.source === 'database' ? '#4caf50' : 
                    message.source === 'error' ? '#f44336' : '#607d8b',
                  mr: 2,
                  mt: 0.5,
                  boxShadow: 2
                }}>
                  {message.source === 'advanced_ai' ? (
                    <PsychologyIcon fontSize="small" />
                  ) : message.source === 'database' ? (
                    <DatabaseIcon fontSize="small" />
                  ) : (
                    <SmartToyIcon fontSize="small" />
                  )}
                </Avatar>
              )}
              
              <Box sx={{ maxWidth: '75%' }}>
                <Paper
                  elevation={message.type === 'user' ? 3 : 2}
                  sx={{
                    p: 2.5,
                    borderRadius: 3,
                    bgcolor: message.type === 'user' 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : '#ffffff',
                    color: message.type === 'user' ? 'white' : 'inherit',
                    border: message.type === 'ai' ? '1px solid #e0e6ed' : 'none',
                    boxShadow: message.type === 'user' 
                      ? '0 4px 20px rgba(102, 126, 234, 0.25)'
                      : '0 2px 10px rgba(0,0,0,0.1)'
                  }}
                >
                  <Typography variant="body1" sx={{ 
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                    fontSize: '0.95rem'
                  }}>
                    {message.text}
                  </Typography>
                  
                  {message.type === 'ai' && (
                    <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                      <Chip 
                        label={
                          message.source === 'advanced_ai' ? 'Advanced AI' : 
                          message.source === 'database' ? 'Database Query' :
                          message.source === 'error' ? 'Error' : 'System'
                        } 
                        size="small" 
                        variant="outlined"
                        color={
                          message.source === 'advanced_ai' ? 'primary' : 
                          message.source === 'database' ? 'success' : 
                          'default'
                        }
                        sx={{ fontSize: '0.75rem', height: 24 }}
                      />
                      
                      {message.confidence && (
                        <Chip 
                          label={`${message.confidence} confidence`} 
                          size="small" 
                          color={message.confidence === 'high' ? 'success' : 'warning'}
                          variant="outlined"
                          sx={{ fontSize: '0.75rem', height: 24 }}
                        />
                      )}
                      
                      {message.dataCount !== undefined && (
                        <Chip 
                          label={`${message.dataCount} records`} 
                          size="small" 
                          variant="outlined"
                          sx={{ fontSize: '0.75rem', height: 24 }}
                        />
                      )}

                      {message.success !== undefined && (
                        <Chip 
                          label={message.success ? 'Success' : 'Failed'} 
                          size="small" 
                          color={message.success ? 'success' : 'error'}
                          variant="outlined"
                          sx={{ fontSize: '0.75rem', height: 24 }}
                        />
                      )}
                    </Box>
                  )}
                </Paper>
                
                <Typography 
                  variant="caption" 
                  color="text.secondary" 
                  sx={{ 
                    display: 'block', 
                    mt: 1,
                    textAlign: message.type === 'user' ? 'right' : 'left',
                    fontSize: '0.75rem'
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Box>
              
              {message.type === 'user' && (
                <Avatar sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: '#ff9800', 
                  ml: 2, 
                  mt: 0.5,
                  boxShadow: 2
                }}>
                  <PersonIcon fontSize="small" />
                </Avatar>
              )}
            </Box>
          </Fade>
        ))}
        
        {isLoading && <TypingIndicator useAdvancedAI={useAdvancedAI} />}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Section */}
      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid #e0e6ed', 
        bgcolor: '#fff',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.05)'
      }}>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              useAdvancedAI ? 
              "Ask me anything with advanced AI..." : 
              "Query ocean database..."
            }
            variant="outlined"
            size="small"
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                bgcolor: '#f8f9fa',
                '&:hover': {
                  bgcolor: '#f1f3f4'
                },
                '&.Mui-focused': {
                  bgcolor: '#fff'
                }
              },
              '& .MuiOutlinedInput-input': {
                fontSize: '0.95rem'
              }
            }}
          />
          <Tooltip title={useAdvancedAI ? "Send to AI" : "Query Database"}>
            <IconButton
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              sx={{ 
                bgcolor: useAdvancedAI ? '#176CA0' : '#4caf50',
                color: 'white',
                width: 48,
                height: 48,
                '&:hover': { 
                  bgcolor: useAdvancedAI ? '#1565c0' : '#388e3c',
                  transform: 'scale(1.05)'
                },
                '&:disabled': { 
                  bgcolor: '#e0e0e0',
                  transform: 'none'
                },
                transition: 'all 0.2s'
              }}
            >
              {isLoading ? (
                <CircularProgress size={20} sx={{ color: 'white' }} />
              ) : (
                <SendIcon />
              )}
            </IconButton>
          </Tooltip>
        </Box>
        
        {/* Status indicator */}
        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            {useAdvancedAI && aiStatus === 'loaded' ? 
              "🤖 Advanced AI Active" : 
              "🗄️ Database Query Mode"
            }
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}
