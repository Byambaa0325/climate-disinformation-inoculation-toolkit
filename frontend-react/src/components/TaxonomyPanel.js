import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Accordion, AccordionSummary, AccordionDetails,
  Chip, CircularProgress, Alert, Link,
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import axios from 'axios';
import { getRef } from '../data/references';

// Maps each technique to the reference of its primary source framework
const TECH_REF = {
  // FLICC — denial
  fake_experts:                   'cook2022',
  impersonating_consensus:        'cook2022',
  // CARDS — denial
  trend_skepticism:               'coan2021',
  attribution_skepticism:         'coan2021',
  // FLICC — doubt-casting
  cherry_picking:                 'cook2022',
  impossible_expectations:        'cook2022',
  false_equivalence:              'cook2022',
  oversimplification:             'cook2022',
  // CARDS — doubt-casting
  model_attacks:                  'coan2021',
  // CARDS — deflection
  other_countries:                'coan2021',
  whataboutism:                   'coan2021',
  individual_responsibility_transfer: 'coan2021',
  fossil_fuel_necessity:          'coan2021',
  // 4D — delay
  tech_salvation:                 'lamb2020',
  economic_cost:                  'lamb2020',
  moving_goalposts:               'lamb2020',
  false_urgency_reversal:         'lamb2020',
  // FLICC — conspiracy
  nefarious_intent:               'cook2022',
  global_conspiracy:              'cook2022',
  coverup:                        'cook2022',
  persecution_narrative:          'cook2022',
};

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
        Unified 5-cluster schema ·{' '}
        {[
          { label: 'FLICC', id: 'cook2022' },
          { label: 'CARDS', id: 'coan2021' },
          { label: '4D Framework', id: 'lamb2020' },
        ].map((fw, i) => {
          const ref = getRef(fw.id);
          return (
            <React.Fragment key={fw.id}>
              {i > 0 && ' · '}
              {ref?.url
                ? <Link href={ref.url} target="_blank" rel="noopener noreferrer" underline="hover" sx={{ color: '#006B3C' }}>{fw.label}</Link>
                : fw.label}
            </React.Fragment>
          );
        })}
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
              {cluster.techniques.map((tech) => {
                const ref = getRef(TECH_REF[tech]);
                const chip = (
                  <Chip
                    key={tech}
                    label={tech.replace(/_/g, ' ')}
                    size="small"
                    variant="outlined"
                    sx={{
                      fontSize: '0.65rem',
                      borderColor: CLUSTER_COLORS[cluster.id],
                      color: CLUSTER_COLORS[cluster.id],
                      cursor: ref ? 'pointer' : 'default',
                      '&:hover': ref ? { backgroundColor: `${CLUSTER_COLORS[cluster.id]}18` } : {},
                    }}
                  />
                );
                return ref?.url ? (
                  <Link key={tech} href={ref.url} target="_blank" rel="noopener noreferrer" underline="none" title={ref.shortCite}>
                    {chip}
                  </Link>
                ) : chip;
              })}
            </Box>

            <Typography variant="caption" fontWeight={600} sx={{ display: 'block', mb: 0.5, color: '#1A2E1A' }}>
              Source frameworks
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
              {cluster.source_frameworks.map((fw) => {
                const prefix = fw.split(':')[0].trim();
                const refId = prefix.startsWith('FLICC') ? 'cook2022' : prefix.startsWith('CARDS') ? 'coan2021' : prefix.startsWith('4D') ? 'lamb2020' : null;
                const ref = refId ? getRef(refId) : null;
                return ref?.url ? (
                  <Link key={fw} href={ref.url} target="_blank" rel="noopener noreferrer" underline="none" title={ref.shortCite}>
                    <Chip label={fw} size="small"
                      sx={{ fontSize: '0.6rem', backgroundColor: '#E8F5EE', color: '#006B3C', cursor: 'pointer', '&:hover': { backgroundColor: '#D0EBD8' } }}
                    />
                  </Link>
                ) : (
                  <Chip key={fw} label={fw} size="small"
                    sx={{ fontSize: '0.6rem', backgroundColor: '#E8F5EE', color: '#006B3C' }}
                  />
                );
              })}
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
        {['cook2022', 'coan2021', 'lamb2020'].map(getRef).filter(Boolean).map((ref, i) => (
          <React.Fragment key={ref.id}>
            {i > 0 && ' · '}
            <Link href={ref.url} target="_blank" rel="noopener noreferrer" underline="hover" sx={{ color: '#006B3C' }}>
              {ref.shortCite}
            </Link>
          </React.Fragment>
        ))}
      </Typography>
    </Box>
  );
}
