import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box, Typography, TextField, Select, MenuItem, FormControl,
  CircularProgress, Alert, Chip, Button, InputAdornment, Divider,
} from '@mui/material';
import { PlayArrow, Search, Refresh, CalendarToday, Close } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const PAGE_SIZE = 15;

const UN = {
  primary:  '#009B55',
  primaryDk:'#006B3C',
  bg:       '#F2F7F4',
  border:   '#C8DFC8',
  textMain: '#1A2E1A',
  textMuted:'#4A6550',
};

export default function ClaimExplorer({ apiKey, onSelectEntry }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [sources, setSources] = useState([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);

  const [filterSource, setFilterSource] = useState('');
  const [searchQ, setSearchQ] = useState('');
  const [debouncedQ, setDebouncedQ] = useState('');
  const [dateFilter, setDateFilter] = useState('');   // single date YYYY-MM-DD

  const sentinelRef = useRef(null);
  const headers = apiKey ? { 'X-API-Key': apiKey } : {};

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(searchQ), 350);
    return () => clearTimeout(t);
  }, [searchQ]);

  // Build params shared by all fetches
  const buildParams = useCallback((pg) => {
    const params = { page: pg, page_size: PAGE_SIZE };
    if (filterSource) params.source = filterSource;
    if (debouncedQ)   params.q = debouncedQ;
    if (dateFilter) {
      params.date_from = dateFilter;
      params.date_to   = dateFilter;
    }
    return params;
  }, [filterSource, debouncedQ, dateFilter]);

  // Initial / filter-reset fetch
  const fetchFresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    setItems([]);
    setPage(0);
    setHasMore(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/news/headlines`, {
        headers, params: buildParams(0),
      });
      const data = res.data.headlines || [];
      setItems(data);
      setTotal(res.data.total || 0);
      setHasMore(data.length === PAGE_SIZE);
      if (res.data.sources?.length) setSources(res.data.sources);
    } catch {
      setError('Failed to load news headlines.');
    } finally {
      setLoading(false);
    }
  }, [buildParams, apiKey]); // eslint-disable-line

  // Append next page
  const fetchMore = useCallback(async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    try {
      const nextPage = page + 1;
      const res = await axios.get(`${API_BASE_URL}/news/headlines`, {
        headers, params: buildParams(nextPage),
      });
      const data = res.data.headlines || [];
      setItems((prev) => [...prev, ...data]);
      setPage(nextPage);
      setHasMore(data.length === PAGE_SIZE);
    } catch {
      // silently fail — user can scroll again
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, page, buildParams, apiKey]); // eslint-disable-line

  // Re-fetch when filters change
  useEffect(() => { fetchFresh(); }, [fetchFresh]);

  // IntersectionObserver for infinite scroll
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) fetchMore(); },
      { threshold: 0.1 },
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [fetchMore]);

  const clearDate = () => setDateFilter('');

  return (
    <Box sx={{ p: 1 }}>

      {/* Header */}
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
          <Button size="small" onClick={fetchFresh} sx={{ minWidth: 0, p: 0.25, color: UN.textMuted }}>
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
          startAdornment: (
            <InputAdornment position="start">
              <Search sx={{ fontSize: 16, color: UN.textMuted }} />
            </InputAdornment>
          ),
        }}
        sx={{
          mb: 1,
          '& .MuiOutlinedInput-root': {
            fontSize: '0.75rem',
            '&.Mui-focused fieldset': { borderColor: UN.primary },
          },
        }}
      />

      {/* Source + Date row */}
      <Box sx={{ display: 'flex', gap: 0.75, mb: 1.5 }}>
        {sources.length > 0 && (
          <FormControl size="small" sx={{ flex: 1, minWidth: 0 }}>
            <Select
              value={filterSource}
              displayEmpty
              onChange={(e) => setFilterSource(e.target.value)}
              sx={{ fontSize: '0.72rem', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: UN.primary } }}
            >
              <MenuItem value="" sx={{ fontSize: '0.72rem', color: UN.textMuted }}>All sources</MenuItem>
              {sources.map((s) => (
                <MenuItem key={s} value={s} sx={{ fontSize: '0.72rem' }}>{s}</MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {/* Single date picker */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.25 }}>
          <TextField
            size="small"
            type="date"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            InputLabelProps={{ shrink: true }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <CalendarToday sx={{ fontSize: 13, color: UN.textMuted }} />
                </InputAdornment>
              ),
            }}
            sx={{
              width: 148,
              '& .MuiOutlinedInput-root': {
                fontSize: '0.72rem',
                '&.Mui-focused fieldset': { borderColor: UN.primary },
              },
            }}
          />
          {dateFilter && (
            <Button
              size="small"
              onClick={clearDate}
              sx={{ minWidth: 0, p: 0.25, color: UN.textMuted }}
            >
              <Close sx={{ fontSize: 14 }} />
            </Button>
          )}
        </Box>
      </Box>

      <Divider sx={{ mb: 1.5, borderColor: UN.border }} />

      {error && (
        <Alert severity="info" sx={{ mb: 1, fontSize: '0.75rem', py: 0 }}>{error}</Alert>
      )}

      {/* Initial load spinner */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress size={24} sx={{ color: UN.primary }} />
        </Box>
      )}

      {/* Feed */}
      {!loading && items.length === 0 && !error && (
        <Typography variant="body2" sx={{ color: UN.textMuted, textAlign: 'center', py: 2 }}>
          No headlines match your filters.
        </Typography>
      )}

      {!loading && items.map((h) => (
        <Box
          key={`${h.index}-${h.title}`}
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

      {/* Sentinel — triggers fetchMore when scrolled into view */}
      <Box ref={sentinelRef} sx={{ py: 1, display: 'flex', justifyContent: 'center' }}>
        {loadingMore && <CircularProgress size={18} sx={{ color: UN.primary }} />}
        {!loadingMore && !hasMore && items.length > 0 && (
          <Typography variant="caption" sx={{ color: UN.textMuted }}>
            All {total} articles loaded
          </Typography>
        )}
      </Box>

    </Box>
  );
}
