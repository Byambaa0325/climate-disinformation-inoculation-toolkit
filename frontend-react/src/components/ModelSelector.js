/**
 * Enhanced Model Selector Component
 *
 * Shows available models grouped by type (Bedrock / Ollama)
 * with indicators for live generation support
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Chip,
  Paper,
  Divider,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Cloud,
  Computer,
  PlayArrow,
  Storage,
  Info,
} from '@mui/icons-material';
import axios from 'axios';

const ModelSelector = ({ selectedModel, onModelChange, apiBaseUrl }) => {
  const [models, setModels] = useState({ bedrock_models: [], ollama_models: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${apiBaseUrl}/models/available`);
        setModels(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch models:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, [apiBaseUrl]);

  const getSelectedModelInfo = () => {
    const allModels = [
      ...models.bedrock_models,
      ...models.ollama_models,
    ];
    return allModels.find(m => m.id === selectedModel);
  };

  const selectedModelInfo = getSelectedModelInfo();

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Model Selection
        </Typography>
        <Tooltip title="Bedrock models support both live generation and dataset exploration. Ollama models only support dataset exploration.">
          <Info fontSize="small" color="action" />
        </Tooltip>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} />
        </Box>
      ) : error ? (
        <Typography color="error" variant="body2">
          Error loading models: {error}
        </Typography>
      ) : (
        <>
          <FormControl fullWidth>
            <InputLabel id="model-select-label">Select Model</InputLabel>
            <Select
              labelId="model-select-label"
              value={selectedModel}
              label="Select Model"
              onChange={(e) => onModelChange(e.target.value)}
            >
              {/* Bedrock Models Section */}
              <MenuItem disabled>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Cloud fontSize="small" color="primary" />
                  <Typography variant="subtitle2" fontWeight="bold">
                    Bedrock Models (Live + Explore)
                  </Typography>
                </Box>
              </MenuItem>

              {models.bedrock_models.map((model) => (
                <MenuItem key={model.id} value={model.id} sx={{ pl: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                    <Typography sx={{ flexGrow: 1 }}>
                      {model.name}
                    </Typography>
                    <Chip
                      icon={<PlayArrow />}
                      label="LIVE"
                      size="small"
                      color="success"
                      sx={{ fontSize: '0.7rem', height: 20 }}
                    />
                  </Box>
                </MenuItem>
              ))}

              <Divider sx={{ my: 1 }} />

              {/* Ollama Models Section */}
              <MenuItem disabled>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Computer fontSize="small" color="secondary" />
                  <Typography variant="subtitle2" fontWeight="bold">
                    Ollama Models (Explore Only)
                  </Typography>
                </Box>
              </MenuItem>

              {models.ollama_models.map((model) => (
                <MenuItem key={model.id} value={model.id} sx={{ pl: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                    <Typography sx={{ flexGrow: 1 }}>
                      {model.name}
                    </Typography>
                    <Chip
                      icon={<Storage />}
                      label="STATIC"
                      size="small"
                      color="default"
                      sx={{ fontSize: '0.7rem', height: 20 }}
                    />
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Model Info */}
          {selectedModelInfo && (
            <Box sx={{ mt: 2, p: 1.5, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary" display="block">
                <strong>Type:</strong> {selectedModelInfo.type === 'bedrock' ? 'Bedrock (Cloud)' : 'Ollama (Self-hosted)'}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                <strong>Live Generation:</strong> {selectedModelInfo.supports_live_generation ? 'Yes' : 'No (Static benchmark only)'}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                <strong>Dataset Entries:</strong> {selectedModelInfo.total_entries.toLocaleString()}
              </Typography>
            </Box>
          )}

          {/* Summary */}
          <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Tooltip title="Models that support both live generation and dataset exploration">
              <Chip
                icon={<Cloud />}
                label={`${models.bedrock_models.length} Bedrock`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Tooltip>
            <Tooltip title="Models with pre-generated results only (no live generation)">
              <Chip
                icon={<Computer />}
                label={`${models.ollama_models.length} Ollama`}
                size="small"
                color="secondary"
                variant="outlined"
              />
            </Tooltip>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default ModelSelector;
