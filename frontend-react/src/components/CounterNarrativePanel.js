import React, { useState } from 'react';
import {
  Box, Typography, Button, CircularProgress, Alert, Paper, Divider,
  Tabs, Tab, Chip,
} from '@mui/material';
import { Shield, BugReport } from '@mui/icons-material';
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

export default function CounterNarrativePanel({ clusterId, claim, apiKey }) {
  const [tab, setTab] = useState(0);
  const [prebunking, setPrebunking] = useState(null);
  const [debunking, setDebunking] = useState(null);
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

  const fetchDebunking = async () => {
    if (!claim) {
      setError('No claim to debunk. Select a node with a priming question first.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(
        `${API_BASE_URL}/counter/debunking`,
        { claim, cluster_id: clusterId },
        { headers }
      );
      setDebunking(res.data);
    } catch {
      setError('Failed to generate debunking.');
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
        van der Linden et al. (2022) · Lewandowsky et al. (2021)
      </Typography>

      {/* Cluster chip — color = data indicator for which cluster is targeted */}
      {clusterId && (
        <Chip
          label={`Cluster: ${clusterId.replace(/_/g, ' ')}`}
          size="small"
          sx={{ mb: 2, backgroundColor: clusterColor, color: 'white', fontWeight: 500 }}
        />
      )}

      <Tabs value={tab} onChange={(_, v) => setTab(v)}
        sx={{
          mb: 2, borderBottom: '1px solid #C8DFC8',
          '& .MuiTabs-indicator': { backgroundColor: '#009B55' },
          '& .Mui-selected': { color: '#009B55 !important' },
        }}>
        <Tab icon={<Shield fontSize="small" />} label="Prebunk" iconPosition="start" sx={{ fontSize: '0.75rem', minHeight: 36 }} />
        <Tab icon={<BugReport fontSize="small" />} label="Debunk" iconPosition="start" sx={{ fontSize: '0.75rem', minHeight: 36 }} />
      </Tabs>

      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}

      {tab === 0 && (
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
      )}

      {tab === 1 && (
        <Box>
          <Typography variant="caption" sx={{ color: '#4A6550', display: 'block', mb: 1.5 }}>
            <strong>Debunking (3-Step Correction):</strong> Fact → Myth flag → Fallacy explanation.
            Uses fact-first framing.
          </Typography>

          {claim && (
            <Paper elevation={0} sx={{ p: 1, mb: 1.5, backgroundColor: '#F8FAF8', border: '1px solid #C8DFC8' }}>
              <Typography variant="caption" fontWeight={600} sx={{ color: '#1A2E1A' }}>Claim to debunk:</Typography>
              <Typography variant="caption" sx={{ display: 'block', fontStyle: 'italic', color: '#4A6550' }}>
                {claim.length > 150 ? claim.slice(0, 150) + '…' : claim}
              </Typography>
            </Paper>
          )}

          {!debunking ? (
            <Button
              variant="contained"
              size="small"
              onClick={fetchDebunking}
              disabled={loading || !clusterId}
              startIcon={loading ? <CircularProgress size={14} sx={{ color: 'white' }} /> : <BugReport />}
              sx={{ backgroundColor: '#009B55', '&:hover': { backgroundColor: '#006B3C' }, textTransform: 'none' }}
            >
              Generate Debunking
            </Button>
          ) : (
            <Paper elevation={0} sx={{ p: 1.5, backgroundColor: '#F8FAF8', border: '1px solid #C8DFC8' }}>
              <Box sx={{ mb: 1 }}>
                {/* Step colors are data: green=fact (verified), amber=myth (warning), cluster=fallacy type */}
                <Chip label="Step 1: Fact" size="small" sx={{ backgroundColor: '#2E7D32', color: 'white', mb: 0.5, fontWeight: 500 }} />
                <Typography variant="body2" sx={{ color: '#1A2E1A' }}>{debunking.steps?.step1_fact}</Typography>
              </Box>
              <Divider sx={{ my: 1, borderColor: '#C8DFC8' }} />
              <Box sx={{ mb: 1 }}>
                <Chip label="Step 2: Myth Flag" size="small" sx={{ backgroundColor: '#E65100', color: 'white', mb: 0.5, fontWeight: 500 }} />
                <Typography variant="body2" sx={{ color: '#1A2E1A' }}>{debunking.steps?.step2_myth_flag}</Typography>
              </Box>
              <Divider sx={{ my: 1, borderColor: '#C8DFC8' }} />
              <Box>
                <Chip label="Step 3: Fallacy" size="small" sx={{ backgroundColor: clusterColor, color: 'white', mb: 0.5, fontWeight: 500 }} />
                <Typography variant="body2" sx={{ color: '#1A2E1A' }}>{debunking.steps?.step3_fallacy}</Typography>
              </Box>
              <Divider sx={{ my: 1, borderColor: '#C8DFC8' }} />
              <Typography variant="caption" sx={{ color: '#4A6550' }}>
                Sources: {debunking.sources?.join(' · ')}
              </Typography>
              <Button size="small" onClick={() => setDebunking(null)} sx={{ mt: 1, display: 'block', color: '#4A6550', textTransform: 'none', px: 0 }}>
                Clear
              </Button>
            </Paper>
          )}
        </Box>
      )}
    </Box>
  );
}
