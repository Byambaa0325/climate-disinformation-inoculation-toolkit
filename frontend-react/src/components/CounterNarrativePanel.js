import React, { useState } from 'react';
import {
  Box, Typography, Button, CircularProgress, Alert, Paper, Divider, Chip,
} from '@mui/material';
import { Shield } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Cluster colors — data indication only
const CLUSTER_COLORS = {
  denial:        '#C62828',
  doubt_casting: '#E65100',
  deflection:    '#6A1B9A',
  delay:         '#0277BD',
  conspiracy:    '#4E342E',
};

export default function CounterNarrativePanel({ clusterId, apiKey }) {
  const [prebunking, setPrebunking] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const headers = apiKey ? { 'X-API-Key': apiKey } : {};
  const clusterColor = CLUSTER_COLORS[clusterId] || '#546E7A';

  const fetchPrebunking = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE_URL}/counter/prebunking/${clusterId}`, { headers });
      setPrebunking(res.data);
    } catch {
      setError('Failed to generate prebunking. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h6" sx={{ mb: 0.5, fontWeight: 700, color: '#1A2E1A' }}>
        Counter-Messaging
      </Typography>
      <Typography variant="caption" sx={{ color: '#4A6550', display: 'block', mb: 1.5 }}>
        van der Linden et al. (2022)
      </Typography>

      {/* Cluster chip — color = data indicator for which cluster is targeted */}
      {clusterId && (
        <Chip
          label={`Cluster: ${clusterId.replace(/_/g, ' ')}`}
          size="small"
          sx={{ mb: 2, backgroundColor: clusterColor, color: 'white', fontWeight: 500 }}
        />
      )}

      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}

      <Box>
        <Typography variant="caption" sx={{ color: '#4A6550', display: 'block', mb: 1.5 }}>
          <strong>Prebunking (Inoculation):</strong> Warn about the manipulation technique
          before encountering the disinformation. Most effective for novel claims.
        </Typography>

        {!prebunking ? (
          <Button
            variant="contained"
            size="small"
            onClick={fetchPrebunking}
            disabled={loading || !clusterId}
            startIcon={loading ? <CircularProgress size={14} sx={{ color: 'white' }} /> : <Shield />}
            sx={{ backgroundColor: '#009B55', '&:hover': { backgroundColor: '#006B3C' }, textTransform: 'none' }}
          >
            Generate Prebunking
          </Button>
        ) : (
          <Paper elevation={0} sx={{ p: 1.5, backgroundColor: '#F2F7F4', border: '1px solid #C8DFC8', borderLeft: `4px solid ${clusterColor}` }}>
            <Typography variant="caption" fontWeight={700} sx={{ display: 'block', mb: 0.5, color: '#1A2E1A' }}>
              Inoculation Warning — {prebunking.cluster_display_name}
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-line', mb: 1, color: '#1A2E1A' }}>
              {prebunking.message}
            </Typography>
            <Divider sx={{ my: 1, borderColor: '#C8DFC8' }} />
            <Typography variant="caption" sx={{ color: '#4A6550' }}>
              Sources: {prebunking.sources?.join(' · ')}
            </Typography>
            <Button size="small" onClick={() => setPrebunking(null)} sx={{ mt: 1, display: 'block', color: '#4A6550', textTransform: 'none', px: 0 }}>
              Clear
            </Button>
          </Paper>
        )}
      </Box>
    </Box>
  );
}
