import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box, TextField, Button, Paper, Typography, Chip, Dialog,
  DialogTitle, DialogContent, DialogActions, CircularProgress,
  IconButton, ToggleButtonGroup, ToggleButton, Tabs, Tab, Divider,
  FormControl, Select, MenuItem, Collapse,
} from '@mui/material';
import { Close, Create, Search, Shield, TouchApp } from '@mui/icons-material';
import axios from 'axios';
import './App.css';
import DescriptionPanel from './components/DescriptionPanel';
import TaxonomyPanel from './components/TaxonomyPanel';
import ClaimExplorer from './components/ClaimExplorer';
import CounterNarrativePanel from './components/CounterNarrativePanel';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const DEFAULT_API_KEY = process.env.REACT_APP_API_KEY || '';

const UN = {
  headerBg:  '#006B3C',
  primary:   '#009B55',
  primaryDk: '#006B3C',
  bg:        '#F2F7F4',
  panelBg:   '#FFFFFF',
  border:    '#C8DFC8',
  textMain:  '#1A2E1A',
  textMuted: '#4A6550',
};

const CLUSTER_COLORS = {
  denial:        '#C62828',
  doubt_casting: '#E65100',
  deflection:    '#6A1B9A',
  delay:         '#0277BD',
  conspiracy:    '#4E342E',
  root:          '#2E7D32',
};

// Sub-techniques per cluster used for potential expansion nodes
const CLUSTER_TECHNIQUES = {
  denial:        ['fake_experts', 'trend_skepticism', 'attribution_skepticism'],
  doubt_casting: ['cherry_picking', 'impossible_expectations', 'model_attacks'],
  deflection:    ['other_countries', 'whataboutism', 'individual_responsibility_transfer'],
  delay:         ['tech_salvation', 'economic_cost', 'moving_goalposts'],
  conspiracy:    ['nefarious_intent', 'global_conspiracy', 'coverup'],
};

const getAxiosConfig = (apiKey) =>
  apiKey ? { headers: { 'X-API-Key': apiKey } } : {};

const EXAMPLE_STATEMENTS = [
  'Global temperatures have risen approximately 1.2°C since pre-industrial times.',
  'Sea levels are rising at an accelerating rate due to ice sheet melt and thermal expansion.',
  'Human CO2 emissions are the dominant driver of observed warming since the mid-20th century.',
];

// ── Custom ReactFlow node types ──────────────────────────────────────────────

const RootNode = ({ data }) => (
  <>
    <Handle type="source" position={Position.Bottom} style={{ background: 'rgba(255,255,255,0.4)' }} />
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '0.58rem', fontWeight: 700, opacity: 0.75, marginBottom: 3, textTransform: 'uppercase', letterSpacing: 1 }}>
        Original Statement
      </div>
      <div style={{ fontSize: '0.68rem', fontWeight: 600, lineHeight: 1.35 }}>
        {(data.statement || data.label || '').slice(0, 90)}
        {(data.statement || data.label || '').length > 90 ? '…' : ''}
      </div>
    </div>
  </>
);

const DisinfoNode = ({ data }) => {
  if (data.isPotential) {
    return (
      <>
        <Handle type="target" position={Position.Top} style={{ background: 'rgba(255,255,255,0.3)' }} />
        <div style={{ textAlign: 'center', opacity: 0.9 }}>
          <div style={{ fontSize: '0.58rem', fontWeight: 700, opacity: 0.8, marginBottom: 3, textTransform: 'uppercase', letterSpacing: 0.8 }}>
            {data.technique_label || data.display_name}
          </div>
          <div style={{ fontSize: '0.6rem', opacity: 0.75, fontStyle: 'italic' }}>
            click to expand
          </div>
        </div>
      </>
    );
  }
  return (
    <>
      <Handle type="target" position={Position.Top} style={{ background: 'rgba(255,255,255,0.4)' }} />
      <Handle type="source" position={Position.Bottom} style={{ background: 'rgba(255,255,255,0.4)' }} />
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '0.58rem', fontWeight: 700, opacity: 0.75, marginBottom: 3, textTransform: 'uppercase', letterSpacing: 0.8 }}>
          {data.display_name || data.label}
          {data.node_type === 'persona' && data.persona_label ? ` · ${data.persona_label.split(' · ')[2] || ''}` : ''}
        </div>
        <div style={{ fontSize: '0.65rem', fontStyle: 'italic', lineHeight: 1.35, opacity: 0.95 }}>
          {(data.transformed_statement || '').slice(0, 100)}
          {(data.transformed_statement || '').length > 100 ? '…' : ''}
        </div>
      </div>
    </>
  );
};

// ── Main App ─────────────────────────────────────────────────────────────────

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [statement, setStatement] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [expandingNodeId, setExpandingNodeId] = useState(null);
  const [apiKey, setApiKey] = useState(DEFAULT_API_KEY);
  const [inputMode, setInputMode] = useState('custom');
  const [rightTab, setRightTab] = useState(0);
  const [viewMode, setViewMode] = useState('input');
  const [mainPage, setMainPage] = useState('lab'); // 'lab' | 'methodology'
  const [promptOpen, setPromptOpen] = useState(false);
  const [howToOpen, setHowToOpen] = useState(false);

  // Model selection
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('us.amazon.nova-pro-v1:0');

  // Content format
  const [contentFormats, setContentFormats] = useState(null);
  const [selectedFormat, setSelectedFormat] = useState('headline');

  // Persona chips
  const [personaOptions, setPersonaOptions] = useState(null);
  const [selectedPersona, setSelectedPersona] = useState({
    country: null, generation: null, political_orientation: null,
  });
  // Track which node is being hovered during drag
  const [dragOverNodeId, setDragOverNodeId] = useState(null);

  // ReactFlow instance (for screenToFlowPosition)
  const [rfInstance, setRfInstance] = useState(null);

  const nodesRef = useRef(nodes);
  useEffect(() => { nodesRef.current = nodes; }, [nodes]);

  const edgesRef = useRef(edges);
  useEffect(() => { edgesRef.current = edges; }, [edges]);

  // Positions of all nodes at the moment a drag begins
  const dragStartPositions = useRef({});

  // BFS: return all descendant node IDs of a given node via directed edges
  const getDescendants = useCallback((nodeId) => {
    const result = [];
    const queue = [nodeId];
    const visited = new Set([nodeId]);
    while (queue.length) {
      const cur = queue.shift();
      for (const e of edgesRef.current) {
        if (e.source === cur && !visited.has(e.target)) {
          visited.add(e.target);
          result.push(e.target);
          queue.push(e.target);
        }
      }
    }
    return result;
  }, []);

  const handleNodeDragStart = useCallback((_, node) => {
    const positions = {};
    nodesRef.current.forEach((n) => { positions[n.id] = { ...n.position }; });
    dragStartPositions.current = positions;
  }, []);

  const handleNodeDrag = useCallback((_, node) => {
    const start = dragStartPositions.current[node.id];
    if (!start) return;
    const dx = node.position.x - start.x;
    const dy = node.position.y - start.y;
    if (dx === 0 && dy === 0) return;

    const descendants = getDescendants(node.id);
    if (!descendants.length) return;

    setNodes((nds) =>
      nds.map((n) => {
        if (!descendants.includes(n.id)) return n;
        const orig = dragStartPositions.current[n.id];
        if (!orig) return n;
        return { ...n, position: { x: orig.x + dx, y: orig.y + dy } };
      })
    );
  }, [getDescendants]); // eslint-disable-line

  // Custom node types (stable reference)
  const nodeTypes = useMemo(() => ({
    root: RootNode,
    disinformed: DisinfoNode,
    persona: DisinfoNode,
    potential: DisinfoNode,
  }), []);

  // Fetch persona options, available models, and content formats
  useEffect(() => {
    const headers = apiKey ? { 'X-API-Key': apiKey } : {};
    const fetchAll = async () => {
      try {
        const [pRes, mRes, fRes] = await Promise.all([
          fetch(`${API_BASE_URL}/personas`, { headers }),
          fetch(`${API_BASE_URL}/models`, { headers }),
          fetch(`${API_BASE_URL}/content-formats`, { headers }),
        ]);
        if (pRes.ok) {
          const d = await pRes.json();
          setPersonaOptions(d.persona_attributes);
        }
        if (mRes.ok) {
          const d = await mRes.json();
          if (d.generation_models?.length) setAvailableModels(d.generation_models);
        }
        if (fRes.ok) {
          const d = await fRes.json();
          if (d.formats) setContentFormats(d.formats);
        }
      } catch {}
    };
    fetchAll();
  }, [apiKey]);

  // ── Graph expand (initial 5 cluster nodes) ─────────────────────────────────

  const handleExpandGraph = async () => {
    if (!statement.trim()) return;
    setLoading(true);
    setViewMode('graph');

    try {
      const res = await axios.post(
        `${API_BASE_URL}/graph/expand`,
        { statement: statement.trim(), use_llm: true, generator_model_id: selectedModel, content_format: selectedFormat },
        getAxiosConfig(apiKey)
      );

      const { nodes: newNodes, edges: newEdges } = res.data;

      const rfNodes = newNodes.map((n, i) => ({
        id: n.id,
        type: n.data?.node_type === 'root' ? 'root' : 'disinformed',
        position: n.position || { x: i * 200, y: 0 },
        data: { label: n.label, ...n.data },
        style: nodeStyle(n.style?.background || n.style?.backgroundColor, false),
      }));

      const rfEdges = newEdges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { strokeWidth: 2, stroke: '#5A9E78' },
        labelStyle: { fontSize: 10, fill: UN.textMuted },
      }));

      // Spawn potential technique child nodes for every initial cluster node
      const potentialNodes = [];
      const potentialEdges = [];
      const POT_STEP = 220;
      const POT_SPREAD = 200;

      rfNodes.forEach((n) => {
        if (n.data?.node_type !== 'disinformed') return;
        const { cluster_id } = n.data;
        const color = CLUSTER_COLORS[cluster_id] || '#555';
        const techniques = (CLUSTER_TECHNIQUES[cluster_id] || []).slice(0, 3);

        // Radial direction: from root (0,0) to this node
        const dist = Math.sqrt(n.position.x ** 2 + n.position.y ** 2) || 1;
        const nx = n.position.x / dist;
        const ny = n.position.y / dist;

        techniques.forEach((tech, i) => {
          const spread = (i - 1) * POT_SPREAD;
          const potId = `pot_${n.id}_${tech}`;
          potentialNodes.push({
            id: potId,
            type: 'potential',
            position: {
              x: Math.round(n.position.x + nx * POT_STEP + (-ny) * spread),
              y: Math.round(n.position.y + ny * POT_STEP + nx * spread),
            },
            data: {
              label: tech.replace(/_/g, ' '),
              technique_label: tech.replace(/_/g, ' '),
              display_name: n.data.display_name,
              cluster_id,
              technique: tech,
              original_statement: n.data.original_statement,
              parent_transformed: n.data.transformed_statement,
              persona: null,
              counter_points: n.data.counter_points,
              node_type: 'potential',
              isPotential: true,
            },
            style: nodeStyle(color, true),
          });
          potentialEdges.push({
            id: `edge_${n.id}_${potId}`,
            source: n.id,
            target: potId,
            markerEnd: { type: MarkerType.ArrowClosed },
            style: { strokeWidth: 1, stroke: color, strokeDasharray: '4,3', opacity: 0.6 },
          });
        });
      });

      setNodes([...rfNodes, ...potentialNodes]);
      setEdges([...rfEdges, ...potentialEdges]);
    } catch (err) {
      console.error('Graph expansion failed:', err);
      alert(`Failed to generate transformations: ${err.response?.data?.error || err.message}`);
      setViewMode('input');
    } finally {
      setLoading(false);
    }
  };

  // ── Node style helper ───────────────────────────────────────────────────────

  const nodeStyle = (bg, isPotential, isDropTarget = false) => ({
    background: bg,
    color: 'white',
    border: isPotential
      ? '2px dashed rgba(255,255,255,0.55)'
      : isDropTarget
      ? '3px solid rgba(255,255,0,0.9)'
      : '2px solid rgba(255,255,255,0.22)',
    borderRadius: '8px',
    padding: '10px 12px',
    cursor: isPotential ? 'pointer' : 'default',
    minWidth: 140,
    maxWidth: 200,
    opacity: isPotential ? 0.8 : 1,
  });

  // ── Persona chip interactions ───────────────────────────────────────────────

  const togglePersonaChip = (category, key) => {
    setSelectedPersona((prev) => ({
      ...prev,
      [category]: prev[category] === key ? null : key,
    }));
  };

  // Drag start from a single category chip — carry only that attribute (singular persona)
  const handleChipDragStart = (e, category, key) => {
    const singularPersona = { country: null, generation: null, political_orientation: null, [category]: key };
    e.dataTransfer.setData('persona_chip', JSON.stringify(singularPersona));
    e.dataTransfer.effectAllowed = 'copy';
  };

  // Drag start from format chip — carry the format key
  const handleFormatChipDragStart = (e, formatKey) => {
    e.dataTransfer.setData('format_chip', formatKey);
    e.dataTransfer.effectAllowed = 'copy';
  };

  // ── ReactFlow drag-over / drop ──────────────────────────────────────────────

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    if (!rfInstance) return;
    const pos = rfInstance.screenToFlowPosition({ x: e.clientX, y: e.clientY });
    const hit = nodesRef.current.find(
      (n) => n.data?.cluster_id && !n.data?.isPotential &&
        pos.x >= n.position.x - 10 && pos.x <= n.position.x + 210 &&
        pos.y >= n.position.y - 10 && pos.y <= n.position.y + 130
    );
    setDragOverNodeId(hit?.id || null);
  }, [rfInstance]);

  const handleDragLeave = useCallback(() => setDragOverNodeId(null), []);

  const handleDrop = useCallback(async (e) => {
    e.preventDefault();
    setDragOverNodeId(null);
    if (!rfInstance) return;

    const personaRaw = e.dataTransfer.getData('persona_chip');
    const formatKey  = e.dataTransfer.getData('format_chip');
    if (!personaRaw && !formatKey) return;

    const pos = rfInstance.screenToFlowPosition({ x: e.clientX, y: e.clientY });
    const targetNode = nodesRef.current.find(
      (n) => n.data?.cluster_id && !n.data?.isPotential &&
        pos.x >= n.position.x - 10 && pos.x <= n.position.x + 210 &&
        pos.y >= n.position.y - 10 && pos.y <= n.position.y + 130
    );
    if (!targetNode) return;

    if (personaRaw) {
      const persona = JSON.parse(personaRaw);
      if (persona.country || persona.generation || persona.political_orientation) {
        await handlePersonaDropExpand(targetNode, persona);
      }
    } else if (formatKey) {
      await handleFormatDropExpand(targetNode, formatKey);
    }
  }, [rfInstance]); // eslint-disable-line

  // ── Persona drop expansion: creates persona node + 3 potential technique children ──

  const handlePersonaDropExpand = async (targetNode, persona) => {
    const { cluster_id, original_statement, transformed_statement: parentTransformed, counter_points, description } = targetNode.data;
    if (!cluster_id || !original_statement) return;

    const parentId = targetNode.id;
    const parentPos = targetNode.position;
    const color = CLUSTER_COLORS[cluster_id] || '#555';

    // Direction-aware positioning: expand along the radial vector from root → parent,
    // so nodes above/left/right the root don't collapse back toward the centre.
    const rootNode = nodesRef.current.find((n) => n.data?.node_type === 'root');
    const rootPos = rootNode?.position || { x: 0, y: 0 };
    const dx = parentPos.x - rootPos.x;
    const dy = parentPos.y - rootPos.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const nx = dx / dist; // radial unit vector
    const ny = dy / dist;

    const RADIAL_STEP = 250; // root → cluster already ~350, so this keeps spacing consistent

    // Build persona label from options
    const pLabel = [
      personaOptions?.political_orientation?.[persona.political_orientation]?.label,
      personaOptions?.generation?.[persona.generation]?.label,
      personaOptions?.country?.[persona.country]?.label,
    ].filter(Boolean).join(' · ');

    const personaNodeId = `persona_${parentId}_${Date.now()}`;
    const personaPos = {
      x: Math.round(parentPos.x + nx * RADIAL_STEP),
      y: Math.round(parentPos.y + ny * RADIAL_STEP),
    };

    // Placeholder persona node while generating
    const placeholderNode = {
      id: personaNodeId,
      type: 'persona',
      position: personaPos,
      data: {
        label: pLabel || 'Persona',
        display_name: targetNode.data.display_name,
        cluster_id,
        description,
        original_statement,
        transformed_statement: '…generating…',
        counter_points,
        persona,
        persona_label: pLabel,
        node_type: 'persona',
        isPotential: false,
      },
      style: nodeStyle(color, false),
    };
    const personaEdge = {
      id: `edge_${parentId}_${personaNodeId}`,
      source: parentId,
      target: personaNodeId,
      label: pLabel || 'Persona',
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { strokeWidth: 1.5, stroke: color, strokeDasharray: '5,3' },
      labelStyle: { fontSize: 9, fill: UN.textMuted },
    };

    // Remove any initial potential technique nodes that were children of this cluster node,
    // since the persona node will spawn its own technique children.
    setNodes((nds) => [...nds.filter((n) => !n.id.startsWith(`pot_${parentId}_`)), placeholderNode]);
    setEdges((eds) => [...eds.filter((e) => !e.id.startsWith(`edge_${parentId}_pot_`)), personaEdge]);
    setExpandingNodeId(personaNodeId);

    try {
      const res = await axios.post(
        `${API_BASE_URL}/transform`,
        { statement: (parentTransformed && parentTransformed !== '…generating…') ? parentTransformed : original_statement, cluster_id, persona, use_llm: true, generator_model_id: selectedModel, content_format: selectedFormat },
        getAxiosConfig(apiKey)
      );
      const transformed = res.data.transformed_statement;
      const promptUsed = res.data.prompt_used || '';

      // Update placeholder with real content
      setNodes((nds) => nds.map((n) =>
        n.id === personaNodeId
          ? { ...n, data: { ...n.data, transformed_statement: transformed, prompt_used: promptUsed } }
          : n
      ));

      // Spawn 3 dashed potential technique child nodes.
      // Place them further along the radial direction, spread perpendicular to it.
      const techniques = (CLUSTER_TECHNIQUES[cluster_id] || []).slice(0, 3);
      const newPotentialNodes = [];
      const newPotentialEdges = [];

      const POT_STEP = 220;   // distance further from persona node along radial
      const POT_SPREAD = 200; // lateral spread (perpendicular to radial)

      techniques.forEach((tech, i) => {
        const spread = (i - 1) * POT_SPREAD; // -200, 0, +200
        // Perpendicular vector to (nx, ny) is (-ny, nx)
        const potId = `pot_${personaNodeId}_${tech}`;
        newPotentialNodes.push({
          id: potId,
          type: 'potential',
          position: {
            x: Math.round(personaPos.x + nx * POT_STEP + (-ny) * spread),
            y: Math.round(personaPos.y + ny * POT_STEP + nx * spread),
          },
          data: {
            label: tech.replace(/_/g, ' '),
            technique_label: tech.replace(/_/g, ' '),
            display_name: targetNode.data.display_name,
            cluster_id,
            technique: tech,
            original_statement,
            parent_transformed: transformed,
            persona,
            counter_points,
            node_type: 'potential',
            isPotential: true,
          },
          style: nodeStyle(color, true),
        });
        newPotentialEdges.push({
          id: `edge_${personaNodeId}_${potId}`,
          source: personaNodeId,
          target: potId,
          markerEnd: { type: MarkerType.ArrowClosed },
          style: { strokeWidth: 1, stroke: color, strokeDasharray: '4,3', opacity: 0.6 },
        });
      });

      setNodes((nds) => [...nds, ...newPotentialNodes]);
      setEdges((eds) => [...eds, ...newPotentialEdges]);
    } catch (err) {
      alert(`Persona expansion failed: ${err.response?.data?.error || err.message}`);
      setNodes((nds) => nds.filter((n) => n.id !== personaNodeId));
      setEdges((eds) => eds.filter((e) => e.target !== personaNodeId));
    } finally {
      setExpandingNodeId(null);
    }
  };

  // ── Format chip drop: re-transform the node's content in a different format ──

  const handleFormatDropExpand = async (targetNode, formatKey) => {
    const { cluster_id, original_statement, transformed_statement, counter_points, description, persona } = targetNode.data;
    if (!cluster_id) return;

    const parentId = targetNode.id;
    const parentPos = targetNode.position;
    const color = CLUSTER_COLORS[cluster_id] || '#555';
    const formatLabel = contentFormats?.[formatKey]?.label || formatKey;

    // Direction-aware positioning (same radial expansion as persona)
    const rootNode = nodesRef.current.find((n) => n.data?.node_type === 'root');
    const rootPos = rootNode?.position || { x: 0, y: 0 };
    const dx = parentPos.x - rootPos.x;
    const dy = parentPos.y - rootPos.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const nx = dx / dist;
    const ny = dy / dist;

    const fmtNodeId = `fmt_${parentId}_${formatKey}_${Date.now()}`;
    const fmtPos = {
      x: Math.round(parentPos.x + nx * 250),
      y: Math.round(parentPos.y + ny * 250),
    };

    const placeholderNode = {
      id: fmtNodeId,
      type: 'disinformed',
      position: fmtPos,
      data: {
        label: formatLabel,
        display_name: `${targetNode.data.display_name || ''} · ${formatLabel}`,
        cluster_id,
        description,
        original_statement,
        transformed_statement: '…generating…',
        counter_points,
        persona: persona || null,
        format: formatKey,
        format_label: formatLabel,
        node_type: 'format',
        isPotential: false,
      },
      style: nodeStyle(color, false),
    };

    const fmtEdge = {
      id: `edge_${parentId}_${fmtNodeId}`,
      source: parentId,
      target: fmtNodeId,
      label: formatLabel,
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { strokeWidth: 1.5, stroke: color, strokeDasharray: '5,3' },
      labelStyle: { fontSize: 9, fill: UN.textMuted },
    };

    setNodes((nds) => [...nds, placeholderNode]);
    setEdges((eds) => [...eds, fmtEdge]);
    setExpandingNodeId(fmtNodeId);

    // Re-transform using the source node's content (already distorted) in the new format
    const inputStatement = transformed_statement && transformed_statement !== '…generating…'
      ? transformed_statement
      : original_statement;

    try {
      const res = await axios.post(
        `${API_BASE_URL}/transform`,
        {
          statement: inputStatement,
          cluster_id,
          persona: persona || null,
          use_llm: true,
          generator_model_id: selectedModel,
          content_format: formatKey,
        },
        getAxiosConfig(apiKey)
      );
      setNodes((nds) => nds.map((n) =>
        n.id === fmtNodeId
          ? { ...n, data: { ...n.data, transformed_statement: res.data.transformed_statement, prompt_used: res.data.prompt_used || '' } }
          : n
      ));
    } catch (err) {
      alert(`Format expansion failed: ${err.response?.data?.error || err.message}`);
      setNodes((nds) => nds.filter((n) => n.id !== fmtNodeId));
      setEdges((eds) => eds.filter((ed) => ed.target !== fmtNodeId));
    } finally {
      setExpandingNodeId(null);
    }
  };

  // ── Click on dashed potential technique node → expand it ───────────────────

  const handlePotentialExpand = async (potNode) => {
    if (expandingNodeId) return;
    const { cluster_id, technique, original_statement, parent_transformed, persona } = potNode.data;
    if (!cluster_id || !technique) return;

    setExpandingNodeId(potNode.id);

    // Mark as loading
    setNodes((nds) => nds.map((n) =>
      n.id === potNode.id
        ? { ...n, data: { ...n.data, transformed_statement: '…generating…', isPotential: false } }
        : n
    ));

    try {
      const res = await axios.post(
        `${API_BASE_URL}/transform`,
        {
          statement: parent_transformed || original_statement,
          cluster_id,
          technique,
          persona,
          use_llm: true,
          generator_model_id: selectedModel,
          content_format: selectedFormat,
        },
        getAxiosConfig(apiKey)
      );
      const transformed = res.data.transformed_statement;
      const promptUsed = res.data.prompt_used || '';

      setNodes((nds) => nds.map((n) =>
        n.id === potNode.id
          ? {
              ...n,
              type: 'disinformed',
              data: {
                ...n.data,
                transformed_statement: transformed,
                prompt_used: promptUsed,
                isPotential: false,
                node_type: 'technique',
              },
              style: nodeStyle(CLUSTER_COLORS[cluster_id], false),
            }
          : n
      ));
    } catch (err) {
      alert(`Technique expansion failed: ${err.response?.data?.error || err.message}`);
      // Revert to potential
      setNodes((nds) => nds.map((n) =>
        n.id === potNode.id
          ? { ...n, data: { ...n.data, isPotential: true }, style: nodeStyle(CLUSTER_COLORS[cluster_id], true) }
          : n
      ));
    } finally {
      setExpandingNodeId(null);
    }
  };

  // ── Node click routing ──────────────────────────────────────────────────────

  const handleNodeClick = useCallback((_, node) => {
    if (node.data?.node_type === 'root') return;
    if (node.data?.isPotential) {
      handlePotentialExpand(node);
      return;
    }
    setSelectedNode(node);
    setDialogOpen(true);
    setPromptOpen(false);
  }, [expandingNodeId]); // eslint-disable-line

  // Update drag-over node border styling
  useEffect(() => {
    setNodes((nds) => nds.map((n) => {
      if (!n.data?.cluster_id || n.data?.isPotential) return n;
      const isDragTarget = n.id === dragOverNodeId;
      return {
        ...n,
        style: nodeStyle(CLUSTER_COLORS[n.data.cluster_id] || '#555', false, isDragTarget),
      };
    }));
  }, [dragOverNodeId]); // eslint-disable-line

  const handleExploreSelect = (entry) => {
    setStatement(entry.title || entry.target_question || entry.statement || '');
    setInputMode('custom');
  };

  const toggleSx = {
    '&.Mui-selected': { backgroundColor: UN.primary, color: '#fff', '&:hover': { backgroundColor: UN.primaryDk } },
    '&:hover': { backgroundColor: '#E8F5EE' },
    fontSize: '0.75rem',
  };

  // Persona category labels
  const CATEGORY_LABELS = {
    country: 'Country',
    generation: 'Generation',
    political_orientation: 'Politics',
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: UN.bg }}>
      {/* Header */}
      <Box sx={{ px: 2, py: 1.25, backgroundColor: UN.headerBg, color: 'white', display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: 0.5, fontSize: '1rem' }}>
          Climate Disinformation Lab
        </Typography>
        <Tabs
          value={mainPage}
          onChange={(_, v) => v && setMainPage(v)}
          sx={{
            minHeight: 40,
            ml: 2,
            '& .MuiTabs-indicator': { backgroundColor: 'white' },
            '& .MuiTab-root': { color: 'rgba(255,255,255,0.8)', minHeight: 36, fontSize: '0.8rem', textTransform: 'none' },
            '& .Mui-selected': { color: 'white !important', fontWeight: 600 },
          }}
        >
          <Tab value="methodology" label="Methodology" />
          <Tab value="lab" label="Lab" />
        </Tabs>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.65)', fontStyle: 'italic', ml: 1 }}>
          {mainPage === 'lab' ? 'Statement Transformation · 5-Cluster Taxonomy' : 'Research approach'}
        </Typography>
        <Box sx={{ ml: 'auto' }}>
          <TextField
            size="small"
            placeholder="API Key (optional)"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            sx={{
              width: 160,
              '& .MuiOutlinedInput-root': {
                color: 'white',
                fontSize: '0.75rem',
                '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.6)' },
              },
            }}
          />
        </Box>
      </Box>

      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {mainPage === 'methodology' ? (
          <Box sx={{ flex: 1, overflowY: 'auto', p: 3, maxWidth: 720, mx: 'auto' }}>
            <DescriptionPanel fullPage />
          </Box>
        ) : (
        <>
        {/* ── Left Panel ── */}
        <Box sx={{ width: 290, flexShrink: 0, p: 1.5, overflowY: 'auto', backgroundColor: UN.panelBg, borderRight: `1px solid ${UN.border}` }}>

          {/* How to use */}
          <Box sx={{ mb: 1.5, border: `1px solid ${UN.border}`, borderRadius: 1, overflow: 'hidden' }}>
            <Box
              onClick={() => setHowToOpen((o) => !o)}
              sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: 1.25, py: 0.75, cursor: 'pointer', backgroundColor: howToOpen ? UN.bg : 'transparent', '&:hover': { backgroundColor: UN.bg }, transition: 'background 0.15s' }}
            >
              <Typography variant="caption" fontWeight={700} sx={{ color: UN.primaryDk, fontSize: '0.72rem', letterSpacing: 0.3 }}>
                How to use
              </Typography>
              <Typography sx={{ fontSize: '0.65rem', color: UN.textMuted, lineHeight: 1 }}>
                {howToOpen ? '▾' : '▸'}
              </Typography>
            </Box>
            <Collapse in={howToOpen}>
              <Box sx={{ px: 1.25, pb: 1.25, pt: 0.25 }}>
                {[
                  { step: '1', text: 'Enter a factual climate statement in the text box, or switch to News to pick a real headline.' },
                  { step: '2', text: 'Choose a content format (Headline, Tweet, Facebook…) to control how the output is written.' },
                  { step: '3', text: 'Click Transform Statement — five cluster nodes appear, each showing a distorted version.' },
                  { step: '4', text: 'Click any node to see the technique, original vs. transformed text, counter-talking points, and the generation prompt.' },
                  { step: '5', text: 'Select persona chips (country · generation · politics), then drag onto a node to generate a demographic-targeted variant.' },
                  { step: '6', text: 'Drag a format chip onto any node to re-package that node\'s content in a different channel (e.g. turn a headline into a tweet).' },
                  { step: '7', text: 'Click a dashed potential node to drill into a specific sub-technique.' },
                  { step: '8', text: 'Drag any node to reposition it — its children move with it.' },
                ].map(({ step, text }) => (
                  <Box key={step} sx={{ display: 'flex', gap: 0.75, mb: 0.85, alignItems: 'flex-start' }}>
                    <Box sx={{ minWidth: 16, height: 16, borderRadius: '50%', backgroundColor: UN.primary, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, mt: 0.1 }}>
                      <Typography sx={{ fontSize: '0.52rem', color: 'white', fontWeight: 700, lineHeight: 1 }}>{step}</Typography>
                    </Box>
                    <Typography variant="caption" sx={{ color: UN.textMuted, lineHeight: 1.55, fontSize: '0.68rem' }}>{text}</Typography>
                  </Box>
                ))}
              </Box>
            </Collapse>
          </Box>

          <ToggleButtonGroup
            value={inputMode}
            exclusive
            onChange={(_, v) => v && setInputMode(v)}
            size="small"
            sx={{ mb: 1.5, width: '100%' }}
          >
            <ToggleButton value="custom" sx={{ ...toggleSx, flex: 1 }}>
              <Create fontSize="small" sx={{ mr: 0.5 }} /> Custom
            </ToggleButton>
            <ToggleButton value="explore" sx={{ ...toggleSx, flex: 1 }}>
              <Search fontSize="small" sx={{ mr: 0.5 }} /> News
            </ToggleButton>
          </ToggleButtonGroup>

          {inputMode === 'custom' ? (
            <>
              <Typography variant="body2" fontWeight={600} sx={{ mb: 0.75, color: UN.textMain }}>
                Factual Climate Statement
              </Typography>
              <TextField
                multiline
                rows={3}
                fullWidth
                size="small"
                placeholder="Enter a factual climate statement…"
                value={statement}
                onChange={(e) => setStatement(e.target.value)}
                sx={{ mb: 1, '& .MuiOutlinedInput-root': { '&.Mui-focused fieldset': { borderColor: UN.primary } } }}
              />
              <Typography variant="caption" sx={{ color: UN.textMuted, display: 'block', mb: 0.5 }}>
                Examples:
              </Typography>
              {EXAMPLE_STATEMENTS.map((ex) => (
                <Button key={ex} size="small" variant="text" onClick={() => setStatement(ex)}
                  sx={{ display: 'block', textAlign: 'left', fontSize: '0.68rem', mb: 0.25, textTransform: 'none', color: UN.textMuted, px: 0 }}>
                  → {ex.slice(0, 55)}…
                </Button>
              ))}

              <Divider sx={{ my: 1.25, borderColor: UN.border }} />

              {/* ── Content Format Chips ── */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.6 }}>
                <TouchApp sx={{ fontSize: 14, color: UN.textMuted }} />
                <Typography variant="caption" fontWeight={700} sx={{ color: UN.textMain, fontSize: '0.72rem' }}>
                  Format — click or drag onto a node
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1.25 }}>
                {(contentFormats
                  ? Object.entries(contentFormats)
                  : [['headline', { label: 'Headline' }], ['facebook', { label: 'Facebook' }], ['tweet', { label: 'Tweet' }], ['reddit', { label: 'Reddit' }], ['blog', { label: 'Blog' }]]
                ).map(([key, fmt]) => {
                  const isSelected = selectedFormat === key;
                  return (
                    <Chip
                      key={key}
                      label={fmt.label}
                      size="small"
                      draggable
                      onDragStart={(e) => handleFormatChipDragStart(e, key)}
                      onClick={() => setSelectedFormat(key)}
                      sx={{
                        fontSize: '0.65rem',
                        height: 22,
                        cursor: 'grab',
                        backgroundColor: isSelected ? UN.primaryDk : '#E8F5EE',
                        color: isSelected ? 'white' : UN.primaryDk,
                        border: `1px solid ${isSelected ? UN.primaryDk : UN.border}`,
                        fontWeight: isSelected ? 700 : 400,
                        transition: 'all 0.15s',
                        '&:hover': { backgroundColor: isSelected ? UN.primary : '#D0EBD8', transform: 'scale(1.05)' },
                        '&:active': { cursor: 'grabbing' },
                        '& .MuiChip-label': { px: 0.9 },
                      }}
                    />
                  );
                })}
              </Box>

              <Divider sx={{ my: 1.25, borderColor: UN.border }} />

              {/* ── Persona Chips ── */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.75 }}>
                <TouchApp sx={{ fontSize: 14, color: UN.textMuted }} />
                <Typography variant="caption" fontWeight={700} sx={{ color: UN.textMain, fontSize: '0.72rem' }}>
                  Persona — drag onto a node
                </Typography>
              </Box>

              {personaOptions && Object.entries(personaOptions).map(([category, values]) => (
                <Box key={category} sx={{ mb: 1 }}>
                  <Typography variant="caption" sx={{ color: UN.textMuted, fontSize: '0.58rem', textTransform: 'uppercase', letterSpacing: 0.6, display: 'block', mb: 0.3 }}>
                    {CATEGORY_LABELS[category] || category}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.4 }}>
                    {Object.entries(values).map(([key, val]) => {
                      const isSelected = selectedPersona[category] === key;
                      return (
                        <Chip
                          key={key}
                          label={val.label}
                          size="small"
                          draggable
                          onDragStart={(e) => handleChipDragStart(e, category, key)}
                          onClick={() => togglePersonaChip(category, key)}
                          sx={{
                            fontSize: '0.6rem',
                            height: 20,
                            cursor: 'grab',
                            backgroundColor: isSelected ? UN.primary : '#E8F5EE',
                            color: isSelected ? 'white' : UN.primaryDk,
                            border: `1px solid ${isSelected ? UN.primary : UN.border}`,
                            transition: 'all 0.15s',
                            '&:hover': { backgroundColor: isSelected ? UN.primaryDk : '#D0EBD8', transform: 'scale(1.05)' },
                            '&:active': { cursor: 'grabbing' },
                            '& .MuiChip-label': { px: 0.75 },
                          }}
                        />
                      );
                    })}
                  </Box>
                </Box>
              ))}

              {/* Active persona summary — draggable as combined persona */}
              {(selectedPersona.country || selectedPersona.generation || selectedPersona.political_orientation) && (
                <Box
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('persona_chip', JSON.stringify(selectedPersona));
                    e.dataTransfer.effectAllowed = 'copy';
                  }}
                  sx={{
                    mb: 1, p: 0.75, backgroundColor: '#E8F5EE', borderRadius: 1,
                    border: `1px solid ${UN.border}`, cursor: 'grab',
                    '&:active': { cursor: 'grabbing' },
                    '&:hover': { backgroundColor: '#D0EBD8', borderColor: UN.primary },
                    transition: 'all 0.15s',
                  }}
                >
                  <Typography variant="caption" sx={{ color: UN.textMuted, fontSize: '0.6rem', display: 'block', mb: 0.25 }}>
                    Combined persona — drag onto a node
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.4, flexWrap: 'wrap' }}>
                    {Object.entries(selectedPersona).filter(([, v]) => v).map(([cat, key]) => (
                      <Chip key={cat} label={personaOptions?.[cat]?.[key]?.label || key} size="small"
                        sx={{ fontSize: '0.6rem', height: 18, backgroundColor: UN.primary, color: 'white', '& .MuiChip-label': { px: 0.6 } }}
                      />
                    ))}
                  </Box>
                </Box>
              )}

              <Divider sx={{ my: 1.25, borderColor: UN.border }} />

              {/* Generator Model */}
              <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5, color: UN.textMain }}>
                Generator Model
              </Typography>
              <FormControl fullWidth size="small" sx={{ mb: 1.5 }}>
                <Select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  sx={{ fontSize: '0.75rem', '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: UN.primary } }}
                >
                  {availableModels.length > 0 ? (
                    availableModels.map((m) => (
                      <MenuItem key={m.id} value={m.id} sx={{ fontSize: '0.75rem' }}>{m.name}</MenuItem>
                    ))
                  ) : (
                    <MenuItem value="us.amazon.nova-pro-v1:0" sx={{ fontSize: '0.75rem' }}>Nova Pro</MenuItem>
                  )}
                </Select>
              </FormControl>

              <Button
                fullWidth
                variant="contained"
                onClick={handleExpandGraph}
                disabled={loading || !statement.trim()}
                startIcon={loading ? <CircularProgress size={16} sx={{ color: 'white' }} /> : null}
                sx={{ backgroundColor: UN.primary, '&:hover': { backgroundColor: UN.primaryDk }, textTransform: 'none', fontWeight: 600 }}
              >
                {loading ? 'Generating…' : 'Transform Statement'}
              </Button>

              {viewMode === 'graph' && (
                <Button fullWidth variant="text" size="small"
                  onClick={() => { setViewMode('input'); setNodes([]); setEdges([]); setSelectedNode(null); }}
                  sx={{ mt: 0.75, color: UN.textMuted, textTransform: 'none' }}>
                  ← New Statement
                </Button>
              )}
            </>
          ) : (
            <ClaimExplorer apiKey={apiKey} onSelectEntry={handleExploreSelect} />
          )}
        </Box>

        {/* ── Center: Graph ── */}
        <Box sx={{ flex: 1, position: 'relative' }}>
          {viewMode === 'input' || nodes.length === 0 ? (
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <Box sx={{ textAlign: 'center', color: UN.textMuted, maxWidth: 480 }}>
                <Typography variant="h5" sx={{ mb: 1, fontWeight: 300, color: UN.textMain }}>
                  Statement Transformation
                </Typography>
                <Typography variant="body2" sx={{ mb: 1.5, lineHeight: 1.6 }}>
                  Enter a factual climate statement to generate 5 disinformation variants across all clusters.
                  Then <strong>drag a persona chip</strong> onto any cluster node to expand it with a
                  demographic-targeted version — which spawns further distortion paths.
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.75, flexWrap: 'wrap' }}>
                  {Object.entries(CLUSTER_COLORS).filter(([k]) => k !== 'root').map(([k, color]) => (
                    <Chip key={k} label={k.replace(/_/g, ' ')} size="small"
                      sx={{ backgroundColor: color, color: 'white', fontSize: '0.68rem', fontWeight: 500 }}
                    />
                  ))}
                </Box>
              </Box>
            </Box>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={handleNodeClick}
              nodeTypes={nodeTypes}
              onInit={setRfInstance}
              onNodeDragStart={handleNodeDragStart}
              onNodeDrag={handleNodeDrag}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              fitView
              nodesDraggable={!expandingNodeId}
              style={{ background: '#F5F9F6' }}
            >
              <Background color="#C8DFC8" gap={20} />
              <Controls style={{ bottom: 16, right: 16, left: 'auto' }} />
              <MiniMap
                nodeColor={(n) => n.style?.background || UN.primary}
                maskColor="rgba(0,107,60,0.08)"
              />
            </ReactFlow>
          )}

          {/* Expanding spinner overlay */}
          {expandingNodeId && (
            <Box sx={{ position: 'absolute', bottom: 16, left: 16, display: 'flex', alignItems: 'center', gap: 1,
              backgroundColor: 'rgba(255,255,255,0.9)', px: 1.5, py: 0.75, borderRadius: 2, boxShadow: 1 }}>
              <CircularProgress size={16} sx={{ color: UN.primary }} />
              <Typography variant="caption" sx={{ color: UN.textMuted }}>Generating…</Typography>
            </Box>
          )}
        </Box>

        {/* ── Right Panel ── */}
        <Box sx={{ width: 330, flexShrink: 0, backgroundColor: UN.panelBg, borderLeft: `1px solid ${UN.border}`, display: 'flex', flexDirection: 'column' }}>
          <Tabs
            value={rightTab}
            onChange={(_, v) => setRightTab(v)}
            sx={{
              borderBottom: `1px solid ${UN.border}`,
              minHeight: 40,
              '& .MuiTabs-indicator': { backgroundColor: UN.primary },
              '& .Mui-selected': { color: `${UN.primary} !important` },
            }}
          >
            <Tab label="Taxonomy" sx={{ fontSize: '0.75rem', minHeight: 40, flex: 1 }} />
            <Tab icon={<Shield fontSize="small" />} iconPosition="start" label="Counter" sx={{ fontSize: '0.75rem', minHeight: 40, flex: 1 }} />
          </Tabs>
          <Box sx={{ flex: 1, overflowY: 'auto' }}>
            {rightTab === 0 && <TaxonomyPanel apiKey={apiKey} />}
            {rightTab === 1 && (
              <CounterNarrativePanel
                clusterId={selectedNode?.data?.cluster_id}
                apiKey={apiKey}
              />
            )}
          </Box>
        </Box>
        </>
        )}
      </Box>

      {/* ── Node Detail Dialog ── */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth
        PaperProps={{ sx: { borderTop: `4px solid ${CLUSTER_COLORS[selectedNode?.data?.cluster_id] || UN.primary}` } }}>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', pb: 1 }}>
          <Box>
            <Typography variant="h6" sx={{ color: UN.textMain }}>
              {selectedNode?.data?.display_name || selectedNode?.data?.technique_label || 'Node Details'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, flexWrap: 'wrap' }}>
              {selectedNode?.data?.cluster_id && (
                <Chip label={selectedNode.data.cluster_id.replace(/_/g, ' ')} size="small"
                  sx={{ backgroundColor: CLUSTER_COLORS[selectedNode.data.cluster_id], color: 'white', fontWeight: 500 }}
                />
              )}
              {selectedNode?.data?.persona_label && (
                <Chip label={selectedNode.data.persona_label} size="small"
                  sx={{ backgroundColor: '#E8F5EE', color: UN.primaryDk, fontSize: '0.65rem' }}
                />
              )}
              {selectedNode?.data?.technique && (
                <Chip label={selectedNode.data.technique.replace(/_/g, ' ')} size="small" variant="outlined"
                  sx={{ borderColor: CLUSTER_COLORS[selectedNode.data.cluster_id], color: CLUSTER_COLORS[selectedNode.data.cluster_id], fontSize: '0.65rem' }}
                />
              )}
            </Box>
          </Box>
          <IconButton onClick={() => setDialogOpen(false)} size="small"><Close /></IconButton>
        </DialogTitle>

        <DialogContent dividers sx={{ borderColor: UN.border }}>
          {selectedNode?.data?.cluster_id && (
            <>
              <Typography variant="subtitle2" gutterBottom sx={{ color: UN.textMain }}>Disinformation Technique</Typography>
              <Typography variant="body2" sx={{ mb: 2.5, color: UN.textMuted }}>{selectedNode.data.description}</Typography>

              <Typography variant="subtitle2" gutterBottom sx={{ color: UN.textMain }}>Original Statement</Typography>
              <Paper sx={{ p: 1.5, mb: 2.5, backgroundColor: '#F5FAF7', borderLeft: '4px solid #2E7D32' }}>
                <Typography variant="body2" sx={{ color: UN.textMain }}>{selectedNode.data.original_statement}</Typography>
              </Paper>

              <Typography variant="subtitle2" gutterBottom sx={{ color: UN.textMain }}>
                Transformed
                {selectedNode.data.node_type === 'persona' ? ' (Persona-Targeted)' : ''}
                {selectedNode.data.technique ? ` · ${selectedNode.data.technique.replace(/_/g, ' ')}` : ''}
              </Typography>
              <Paper sx={{ p: 1.5, mb: 2.5, backgroundColor: '#FFF8F8', borderLeft: `4px solid ${CLUSTER_COLORS[selectedNode.data.cluster_id]}` }}>
                <Typography variant="body2" sx={{ fontStyle: 'italic', color: UN.textMain }}>
                  {selectedNode.data.transformed_statement}
                </Typography>
              </Paper>

              <Typography variant="subtitle2" gutterBottom sx={{ color: UN.textMain }}>Counter Talking Points</Typography>
              {selectedNode.data.counter_points?.map((pt, i) => (
                <Typography key={i} variant="body2" sx={{ mb: 0.75, color: UN.textMuted, pl: 1 }}>• {pt}</Typography>
              ))}

              {selectedNode.data.prompt_used && (
                <Box sx={{ mt: 2 }}>
                  <Button
                    size="small"
                    variant="text"
                    onClick={() => setPromptOpen((o) => !o)}
                    sx={{ fontSize: '0.72rem', color: UN.textMuted, textTransform: 'none', px: 0, mb: 0.5 }}
                  >
                    {promptOpen ? '▾' : '▸'} Generation prompt
                  </Button>
                  <Collapse in={promptOpen}>
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 1.25,
                        backgroundColor: '#F8F8F8',
                        borderColor: UN.border,
                        fontFamily: 'monospace',
                        fontSize: '0.68rem',
                        color: UN.textMuted,
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        lineHeight: 1.6,
                        maxHeight: 320,
                        overflowY: 'auto',
                      }}
                    >
                      {selectedNode.data.prompt_used}
                    </Paper>
                  </Collapse>
                </Box>
              )}
            </>
          )}
        </DialogContent>

        <DialogActions sx={{ borderTop: `1px solid ${UN.border}` }}>
          <Button onClick={() => { setRightTab(1); setDialogOpen(false); }}
            variant="outlined" size="small" startIcon={<Shield fontSize="small" />}
            sx={{ borderColor: UN.primary, color: UN.primary, textTransform: 'none' }}>
            Counter-Messaging
          </Button>
          <Button onClick={() => setDialogOpen(false)} sx={{ color: UN.textMuted, textTransform: 'none' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App;
