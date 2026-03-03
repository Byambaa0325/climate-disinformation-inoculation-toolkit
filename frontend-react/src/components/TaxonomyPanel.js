import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Accordion, AccordionSummary, AccordionDetails,
  Chip, CircularProgress, Alert,
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
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

export default function TaxonomyPanel({ apiKey }) {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTaxonomy = async () => {
      try {
        const headers = apiKey ? { 'X-API-Key': apiKey } : {};
        const res = await axios.get(`${API_BASE_URL}/taxonomy/clusters`, { headers });
        setClusters(res.data.clusters || []);
      } catch {
        setError('Failed to load taxonomy. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    fetchTaxonomy();
  }, [apiKey]);

  if (loading) return <Box sx={{ p: 2 }}><CircularProgress size={24} sx={{ color: '#009B55' }} /></Box>;
  if (error) return <Alert severity="error" sx={{ m: 1 }}>{error}</Alert>;

  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h6" sx={{ mb: 0.5, fontWeight: 700, color: '#1A2E1A' }}>
        Disinformation Taxonomy
      </Typography>
      <Typography variant="caption" sx={{ color: '#4A6550', display: 'block', mb: 2 }}>
        Unified 5-cluster schema · FLICC · CARDS v2 · 4D Framework
      </Typography>

      {clusters.map((cluster) => (
        <Accordion key={cluster.id} disableGutters elevation={0}
          sx={{ mb: 0.5, border: '1px solid #C8DFC8', '&:before': { display: 'none' }, borderRadius: '4px !important' }}>
          <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#4A6550' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
              {/* Color dot = data indicator for cluster type */}
              <Box sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: CLUSTER_COLORS[cluster.id] || '#666', flexShrink: 0 }} />
              <Typography variant="body2" fontWeight={600} sx={{ color: '#1A2E1A' }}>
                {cluster.display_name}
              </Typography>
              <Chip
                label={`${cluster.technique_count}`}
                size="small"
                sx={{ ml: 'auto', mr: 1, fontSize: '0.65rem', backgroundColor: '#E8F5EE', color: '#006B3C', fontWeight: 600 }}
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 0, borderTop: '1px solid #E8F0EB' }}>
            <Typography variant="caption" sx={{ color: '#4A6550', display: 'block', mb: 1 }}>
              {cluster.description}
            </Typography>

            <Typography variant="caption" fontWeight={600} sx={{ display: 'block', mb: 0.5, color: '#1A2E1A' }}>
              Techniques
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
              {cluster.techniques.map((tech) => (
                <Chip
                  key={tech}
                  label={tech.replace(/_/g, ' ')}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.65rem', borderColor: CLUSTER_COLORS[cluster.id], color: CLUSTER_COLORS[cluster.id] }}
                />
              ))}
            </Box>

            <Typography variant="caption" fontWeight={600} sx={{ display: 'block', mb: 0.5, color: '#1A2E1A' }}>
              Source frameworks
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
              {cluster.source_frameworks.map((fw) => (
                <Chip key={fw} label={fw} size="small"
                  sx={{ fontSize: '0.6rem', backgroundColor: '#E8F5EE', color: '#006B3C' }}
                />
              ))}
            </Box>

            {cluster.example_claims?.length > 0 && (
              <>
                <Typography variant="caption" fontWeight={600} sx={{ display: 'block', mb: 0.5, color: '#1A2E1A' }}>
                  Example priming question
                </Typography>
                <Typography variant="caption" sx={{
                  display: 'block', fontStyle: 'italic', color: '#4A6550',
                  borderLeft: `3px solid ${CLUSTER_COLORS[cluster.id]}`, pl: 1,
                }}>
                  {cluster.example_claims[0]}
                </Typography>
              </>
            )}
          </AccordionDetails>
        </Accordion>
      ))}

      <Typography variant="caption" sx={{ color: '#4A6550', display: 'block', mt: 1.5 }}>
        Cook et al. (2022) · Touzel et al. (2023) · Stoddart & Tindall (2020)
      </Typography>
    </Box>
  );
}
