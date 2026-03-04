import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, TextField, Select, MenuItem, FormControl,
  CircularProgress, Alert, Chip, Button, InputAdornment,
  TablePagination, Divider,
} from '@mui/material';
import { PlayArrow, Search, Refresh } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const UN = {
  primary:  '#009B55',
  primaryDk:'#006B3C',
  bg:       '#F2F7F4',
  border:   '#C8DFC8',
  textMain: '#1A2E1A',
  textMuted:'#4A6550',
};

export default function ClaimExplorer({ apiKey, onSelectEntry }) {
  const [headlines, setHeadlines] = useState([]);
  const [total, setTotal] = useState(0);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [filterSource, setFilterSource] = useState('');
  const [searchQ, setSearchQ] = useState('');
  const [debouncedQ, setDebouncedQ] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const headers = apiKey ? { 'X-API-Key': apiKey } : {};

  // Debounce search input
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(searchQ), 350);
    return () => clearTimeout(t);
  }, [searchQ]);

  const fetchHeadlines = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page, page_size: pageSize };
      if (filterSource) params.source = filterSource;
      if (debouncedQ) params.q = debouncedQ;
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      const res = await axios.get(`${API_BASE_URL}/news/headlines`, { headers, params });
      setHeadlines(res.data.headlines || []);
      setTotal(res.data.total || 0);
      if (res.data.sources?.length) setSources(res.data.sources);
    } catch (err) {
      if (err.response?.status === 404 || err.response?.data?.total === 0) {
        setError('No headlines found. Run: python scripts/fetch_news.py');
      } else {
        setError('Failed to load news headlines.');
      }
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, filterSource, debouncedQ, dateFrom, dateTo, apiKey]); // eslint-disable-line

  useEffect(() => { fetchHeadlines(); }, [fetchHeadlines]);

  // Reset page when filters change
  useEffect(() => { setPage(0); }, [filterSource, debouncedQ, dateFrom, dateTo]);

  return (
    <Box sx={{ p: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
        <Typography variant="body2" fontWeight={700} sx={{ color: UN.textMain }}>
          News Headlines
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Chip
            label={`${total} articles`}
            size="small"
            sx={{ fontSize: '0.65rem', backgroundColor: UN.bg, color: UN.textMuted, border: `1px solid ${UN.border}` }}
          />
          <Button size="small" onClick={fetchHeadlines} sx={{ minWidth: 0, p: 0.25, color: UN.textMuted }}>
            <Refresh fontSize="small" />
          </Button>
        </Box>
      </Box>

      {/* Search */}
      <TextField
        size="small"
        fullWidth
        placeholder="Search headlines..."
        value={searchQ}
        onChange={(e) => setSearchQ(e.target.value)}
        InputProps={{
          startAdornment: <InputAdornment position="start"><Search sx={{ fontSize: 16, color: UN.textMuted }} /></InputAdornment>,
        }}
        sx={{
          mb: 1,
          '& .MuiOutlinedInput-root': {
            fontSize: '0.75rem',
            '&.Mui-focused fieldset': { borderColor: UN.primary },
          },
        }}
      />

      {/* Source filter */}
      {sources.length > 0 && (
        <FormControl fullWidth size="small" sx={{ mb: 1 }}>
          <Select
            value={filterSource}
            displayEmpty
            onChange={(e) => setFilterSource(e.target.value)}
            sx={{ fontSize: '0.75rem', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: UN.primary } }}
          >
            <MenuItem value="" sx={{ fontSize: '0.75rem', color: UN.textMuted }}>All sources</MenuItem>
            {sources.map((s) => (
              <MenuItem key={s} value={s} sx={{ fontSize: '0.75rem' }}>{s}</MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Date range filter */}
      <Box sx={{ display: 'flex', gap: 0.75, mb: 1.5 }}>
        <TextField
          size="small"
          type="date"
          label="From"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          InputLabelProps={{ shrink: true }}
          inputProps={{ max: dateTo || undefined }}
          sx={{
            flex: 1,
            '& .MuiOutlinedInput-root': { fontSize: '0.72rem', '&.Mui-focused fieldset': { borderColor: UN.primary } },
            '& .MuiInputLabel-root': { fontSize: '0.72rem', '&.Mui-focused': { color: UN.primary } },
          }}
        />
        <TextField
          size="small"
          type="date"
          label="To"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          InputLabelProps={{ shrink: true }}
          inputProps={{ min: dateFrom || undefined }}
          sx={{
            flex: 1,
            '& .MuiOutlinedInput-root': { fontSize: '0.72rem', '&.Mui-focused fieldset': { borderColor: UN.primary } },
            '& .MuiInputLabel-root': { fontSize: '0.72rem', '&.Mui-focused': { color: UN.primary } },
          }}
        />
        {(dateFrom || dateTo) && (
          <Button
            size="small"
            onClick={() => { setDateFrom(''); setDateTo(''); }}
            sx={{ minWidth: 0, px: 0.75, color: UN.textMuted, fontSize: '0.65rem', textTransform: 'none' }}
          >
            Clear
          </Button>
        )}
      </Box>

      <Divider sx={{ mb: 1.5, borderColor: UN.border }} />

      {error && (
        <Alert severity="info" sx={{ mb: 1, fontSize: '0.75rem', py: 0 }}>{error}</Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} sx={{ color: UN.primary }} />
        </Box>
      ) : headlines.length === 0 && !error ? (
        <Typography variant="body2" sx={{ color: UN.textMuted, textAlign: 'center', py: 2 }}>
          No headlines match your search.
        </Typography>
      ) : (
        <>
          {headlines.map((h) => (
            <Box
              key={h.index}
              sx={{
                mb: 1,
                p: 1,
                borderRadius: 1,
                border: `1px solid ${UN.border}`,
                backgroundColor: '#FAFCFA',
                '&:hover': { backgroundColor: UN.bg },
              }}
            >
              <Typography
                variant="caption"
                sx={{ display: 'block', fontWeight: 600, color: UN.textMain, lineHeight: 1.35, mb: 0.5 }}
              >
                {h.title}
              </Typography>

              {h.description && (
                <Typography
                  variant="caption"
                  sx={{ display: 'block', color: UN.textMuted, lineHeight: 1.3, mb: 0.5, fontSize: '0.65rem' }}
                >
                  {h.description.slice(0, 120)}{h.description.length > 120 ? '…' : ''}
                </Typography>
              )}

              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 0.25 }}>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  <Chip
                    label={h.source}
                    size="small"
                    sx={{ fontSize: '0.6rem', height: 16, backgroundColor: '#E8F5EE', color: UN.primaryDk }}
                  />
                  {h.published && (
                    <Chip
                      label={h.published.slice(0, 10)}
                      size="small"
                      sx={{ fontSize: '0.6rem', height: 16, backgroundColor: UN.bg, color: UN.textMuted }}
                    />
                  )}
                </Box>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => onSelectEntry?.(h)}
                  startIcon={<PlayArrow sx={{ fontSize: '0.75rem !important' }} />}
                  sx={{
                    fontSize: '0.65rem',
                    py: 0,
                    px: 0.75,
                    minHeight: 22,
                    borderColor: UN.primary,
                    color: UN.primary,
                    textTransform: 'none',
                    '&:hover': { borderColor: UN.primaryDk, color: UN.primaryDk, backgroundColor: '#E8F5EE' },
                  }}
                >
                  Use
                </Button>
              </Box>
            </Box>
          ))}

          <TablePagination
            component="div"
            count={total}
            page={page}
            rowsPerPage={pageSize}
            rowsPerPageOptions={[5, 10, 20]}
            onPageChange={(_, p) => setPage(p)}
            onRowsPerPageChange={(e) => { setPageSize(parseInt(e.target.value)); setPage(0); }}
            sx={{ color: UN.textMuted, fontSize: '0.7rem', '& .MuiTablePagination-selectIcon': { color: UN.textMuted } }}
          />
        </>
      )}
    </Box>
  );
}
