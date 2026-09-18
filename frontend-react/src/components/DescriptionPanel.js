import React from 'react';
import { Box, Typography, Divider, Link, Chip } from '@mui/material';
import { REFERENCES } from '../data/references';

const UN = {
  primary:   '#009B55',
  primaryDk: '#006B3C',
  textMain:  '#1A2E1A',
  textMuted: '#4A6550',
  border:    '#C8DFC8',
  bg:        '#F2F7F4',
};

const CLUSTER_COLORS = {
  denial:        '#C62828',
  doubt_casting: '#E65100',
  deflection:    '#6A1B9A',
  delay:         '#0277BD',
  conspiracy:    '#4E342E',
};

function RefLink({ id, children }) {
  const ref = REFERENCES.find((r) => r.id === id);
  if (!ref?.url) return <>{children}</>;
  return (
    <Link href={ref.url} target="_blank" rel="noopener noreferrer" underline="hover" sx={{ color: UN.primary, fontWeight: 500 }}>
      {children}
    </Link>
  );
}

const CLUSTERS = [
  {
    id: 'denial', label: 'Denial',
    frameworks: [
      { ref: 'cook2022', name: 'FLICC', techniques: 'Fake Experts' },
      { ref: 'coan2021', name: 'CARDS', techniques: 'Trend / Attribution Skepticism' },
      { ref: 'lamb2020', name: '4D',    techniques: 'Deny' },
    ],
  },
  {
    id: 'doubt_casting', label: 'Doubt-Casting',
    frameworks: [
      { ref: 'cook2022', name: 'FLICC', techniques: 'Logical Fallacies, Impossible Expectations, Cherry Picking' },
      { ref: 'coan2021', name: 'CARDS', techniques: 'Science Unreliable' },
      { ref: 'lamb2020', name: '4D',    techniques: 'Deceive' },
    ],
  },
  {
    id: 'deflection', label: 'Deflection',
    frameworks: [
      { ref: 'cook2022', name: 'FLICC', techniques: 'Ad Hominem' },
      { ref: 'coan2021', name: 'CARDS', techniques: 'Fossil Fuels Needed' },
      { ref: 'lamb2020', name: '4D',    techniques: 'Deflect' },
    ],
  },
  {
    id: 'delay', label: 'Delay',
    frameworks: [
      { ref: 'cook2022', name: 'FLICC', techniques: 'Impossible Expectations' },
      { ref: 'coan2021', name: 'CARDS', techniques: 'Policy Alternatives' },
      { ref: 'lamb2020', name: '4D',    techniques: 'Delay' },
    ],
  },
  {
    id: 'conspiracy', label: 'Conspiracy',
    frameworks: [
      { ref: 'cook2022', name: 'FLICC', techniques: 'Conspiracy Theories' },
      { ref: 'coan2021', name: 'CARDS', techniques: 'Alarmism & Hidden Agenda' },
      { ref: 'lamb2020', name: '4D',    techniques: 'Deceive' },
    ],
  },
];

function Section({ title, children }) {
  return (
    <Box sx={{ mb: 3.5 }}>
      <Typography variant="h6" sx={{ fontWeight: 700, color: UN.primaryDk, mb: 1, fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: 0.5 }}>
        {title}
      </Typography>
      {children}
    </Box>
  );
}

function Para({ children }) {
  return (
    <Typography variant="body2" sx={{ color: UN.textMuted, lineHeight: 1.8, mb: 1.25 }}>
      {children}
    </Typography>
  );
}

export default function DescriptionPanel({ fullPage }) {
  return (
    <Box sx={{ p: fullPage ? 4 : 2, maxWidth: fullPage ? 780 : 'none', mx: fullPage ? 'auto' : 0 }}>

      {/* Title */}
      <Typography variant={fullPage ? 'h4' : 'h6'} sx={{ fontWeight: 700, color: UN.textMain, mb: 0.5 }}>
        Methodology
      </Typography>
      <Typography variant="body2" sx={{ color: UN.textMuted, mb: 3, fontStyle: 'italic' }}>
        Climate Disinformation Lab · UCL
      </Typography>

      <Divider sx={{ mb: 3, borderColor: UN.border }} />

      {/* Overview */}
      <Section title="Overview">
        <Para>
          This tool is a research instrument for studying how factual climate statements are
          distorted into disinformation. It operationalises <strong style={{ color: UN.textMain }}>inoculation theory</strong>{' '}
          <RefLink id="vanderLinden2020">van der Linden et al., 2020</RefLink>; <RefLink id="cook2017">Cook et al., 2017</RefLink> — the principle that exposure to a
          labelled, weakened form of misinformation builds cognitive resistance to it. By making the
          transformation process transparent and interactive, the lab is designed both as a
          research testbed and as a prebunking education tool (<RefLink id="cook2020">Cook, 2020</RefLink>).
        </Para>
        <Para>
          Given any factual climate statement, the tool generates distorted variants across five
          disinformation clusters using large language models (LLMs). Persona targeting
          (<RefLink id="leite2025">Leite et al., 2025</RefLink>) and format selection (headlines, social posts, blog excerpts)
          allow researchers to study how audience and medium amplify persuasive effect.
        </Para>
      </Section>

      {/* Extreme-event news corpus */}
      <Section title="Extreme-Event News Corpus">
        <Para>
          The <em>News</em> mode seeds the tool with real-world headlines drawn from a
          live corpus of climate and environmental reporting. Headlines are fetched
          automatically from ten RSS feeds spanning scientific, investigative, and
          mainstream outlets:{' '}
          <strong style={{ color: UN.textMain }}>BBC Science &amp; Environment</strong>,{' '}
          <strong style={{ color: UN.textMain }}>The Guardian Climate Crisis</strong>,{' '}
          <strong style={{ color: UN.textMain }}>Inside Climate News</strong>,{' '}
          <strong style={{ color: UN.textMain }}>Climate Home News</strong>,{' '}
          <strong style={{ color: UN.textMain }}>Carbon Brief</strong>,{' '}
          <strong style={{ color: UN.textMain }}>Phys.org Environment</strong>,{' '}
          <strong style={{ color: UN.textMain }}>Mongabay</strong>,{' '}
          <strong style={{ color: UN.textMain }}>Grist</strong>, and{' '}
          <strong style={{ color: UN.textMain }}>ScienceDaily Weather</strong>.
          After deduplication and date-sorting, up to 110 recent articles are retained.
        </Para>
        <Para>
          Articles are filtered using a keyword vocabulary covering discrete extreme
          events (floods, hurricanes, wildfires, heatwaves, droughts), quantitative
          extremes (record temperatures, unprecedented rainfall), long-run climate
          indicators (sea-level rise, glacier melt, arctic ice loss), and human-impact
          terms (death toll, displacement, evacuation). The Guardian's dedicated
          Climate Crisis feed is ingested unfiltered, as all content is already
          editorially classified as climate-relevant.
        </Para>
        <Para>
          The focus on extreme weather and environmental events is a design
          choice. Extreme events are where climate change is most visible in daily
          news: IPCC AR6 Working Group I{' '}
          (<RefLink id="ipccAR6WGI">IPCC, 2021</RefLink>) reports that evidence
          attributing observed changes in heatwaves, heavy precipitation, and
          droughts to human influence has strengthened since AR5, and Working
          Group II (<RefLink id="ipccAR6WGII">IPCC, 2022</RefLink>) documents the
          resulting impacts, losses, and damages. The{' '}
          <strong style={{ color: UN.textMain }}>IPIE Synthesis Report</strong>{' '}
          (<RefLink id="ipie2025">IPIE, 2025</RefLink>), a systematic review of 300
          studies published 2015–2025, finds that coordinated campaigns shape
          climate narratives, that the scientific consensus is frequently
          misrepresented in media, and that delay functions as a "new denial".
          It reviews evidence that technique-based inoculation transfers across
          topics, notes that results on polarised issues are mixed, and identifies
          the role of AI in producing and circulating misinformation as an open
          research need. The report does not rank topics by susceptibility;
          anchoring the corpus to extreme-event coverage is our choice, not a
          finding of the review.
        </Para>
      </Section>

      {/* Taxonomy */}
      <Section title="Disinformation Taxonomy">
        <Para>
          The five-cluster taxonomy unifies three established frameworks: the{' '}
          <strong style={{ color: UN.textMain }}>FLICC taxonomy</strong> (<RefLink id="cook2022">Cook et al., 2018</RefLink>),{' '}
          <strong style={{ color: UN.textMain }}>CARDS</strong> (<RefLink id="coan2021">Coan et al., 2021</RefLink>), and the{' '}
          <strong style={{ color: UN.textMain }}>4D framework</strong> (<RefLink id="lamb2020">Lamb et al., 2020</RefLink>).
          Each cluster groups techniques that share a common rhetorical strategy.
        </Para>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75, mb: 1.25 }}>
          {CLUSTERS.map(({ id, label, frameworks }) => (
            <Box key={id} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.25, p: 1.25, borderRadius: 1, backgroundColor: UN.bg, border: `1px solid ${UN.border}` }}>
              <Chip label={label} size="small" sx={{ backgroundColor: CLUSTER_COLORS[id], color: 'white', fontWeight: 700, fontSize: '0.65rem', flexShrink: 0 }} />
              <Typography variant="caption" sx={{ color: UN.textMuted, lineHeight: 1.5, pt: 0.15 }}>
                {frameworks.map((fw, i) => (
                  <React.Fragment key={fw.name}>
                    {i > 0 && ' · '}
                    <RefLink id={fw.ref}>{fw.name}</RefLink>
                    {': '}{fw.techniques}
                  </React.Fragment>
                ))}
              </Typography>
            </Box>
          ))}
        </Box>
      </Section>

      {/* Persona targeting */}
      <Section title="Persona Targeting (AI-TRAITS)">
        <Para>
          Persona-targeted disinformation is implemented following the{' '}
          <strong style={{ color: UN.textMain }}>AI-TRAITS methodology</strong> (<RefLink id="leite2025">Leite et al., 2025</RefLink>).
          Each persona is a combination of country (US, UK, BR, RU, UA, IN), generation
          (Gen Alpha through Baby Boomer), and political orientation (far-left to far-right),
          yielding 150 unique audience profiles. A personalisation block is appended to the
          generation prompt instructing the model to use cultural and ideological references
          that resonate with the specified audience — mirroring how real-world influence
          campaigns tailor content for demographic segments.
        </Para>
      </Section>

      {/* LLM red-teaming */}
      <Section title="LLM Generation & Red-Teaming">
        <Para>
          Disinformation variants are generated via AWS Bedrock-hosted LLMs. The prompting
          strategy follows a red-teaming paradigm (<RefLink id="perez2022">Perez et al., 2022</RefLink>): each template frames the
          model as a researcher studying distortion mechanisms, instructs it to apply a specific
          disinformation technique, and requests output in a controlled format (headline, tweet,
          etc.). Sub-technique drilling (e.g. <em>fake experts</em>, <em>cherry picking</em> —{' '}
          <RefLink id="cook2022">Cook et al., 2018</RefLink>)
          allows stepwise escalation of distortion depth.
        </Para>
      </Section>

      {/* Content Format Targeting */}
      <Section title="Content Format Targeting (Novel Contribution)">
        <Para>
          A key extension introduced by this lab is the separation of{' '}
          <strong style={{ color: UN.textMain }}>disinformation technique</strong> from{' '}
          <strong style={{ color: UN.textMain }}>distribution channel</strong>. Prior
          work (e.g. <RefLink id="leite2025">Leite et al., 2025</RefLink>; <RefLink id="perez2022">Perez et al., 2022</RefLink>) focused on what distortion
          is applied; this tool additionally controls <em>how</em> it is packaged for
          dissemination. The same rhetorical technique manifests differently across media
          ecosystems: a denial claim that appears as a news headline carries different
          persuasive affordances than the same claim written as a Facebook post, tweet,
          Reddit title, or blog excerpt.
        </Para>
        <Para>
          Five content formats are supported, each with register-specific prompt
          constraints that enforce length, tone, and platform conventions:
        </Para>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75, mb: 1.25 }}>
          {[
            { label: 'Headline', desc: 'News headline, 8–14 words, title case — the default register anchoring all initial transformations.' },
            { label: 'Facebook', desc: 'Casual first-person post, 1–3 sentences, emotionally engaging, optionally ending with a call to share.' },
            { label: 'Tweet', desc: 'Under 240 characters, opinionated and shareable, with 1–2 hashtags — optimised for virality.' },
            { label: 'Reddit', desc: '10–20 word post title in a conversational or provocative question style, suited to discussion forums.' },
            { label: 'Blog', desc: '2–3 sentence opinion excerpt, authoritative in register, presenting the distorted claim as commentary.' },
          ].map(({ label, desc }) => (
            <Box key={label} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.25, p: 1.25, borderRadius: 1, backgroundColor: UN.bg, border: `1px solid ${UN.border}` }}>
              <Chip label={label} size="small" sx={{ backgroundColor: UN.primaryDk, color: 'white', fontWeight: 700, fontSize: '0.65rem', flexShrink: 0 }} />
              <Typography variant="caption" sx={{ color: UN.textMuted, lineHeight: 1.5, pt: 0.15 }}>{desc}</Typography>
            </Box>
          ))}
        </Box>
        <Para>
          Formats can be selected globally (affecting all initial transformations) or
          applied selectively by dragging a format chip onto any existing node, producing
          a child node that re-packages the parent's transformed content in the chosen
          register. This enables researchers to trace how the same distorted claim
          mutates as it moves across platforms — a process central to cross-platform
          influence-campaign analysis.
        </Para>
      </Section>

      {/* Counter-messaging */}
      <Section title="Counter-Messaging">
        <Para>
          Each cluster is paired with prebunking and debunking responses grounded in
          the inoculation literature (<RefLink id="roozenbeek2022">Roozenbeek et al., 2022</RefLink>;{' '}
          <RefLink id="vanderLinden2020">van der Linden et al., 2020</RefLink>). Prebunking warns of the
          rhetorical technique before exposure; debunking corrects the distorted claim after
          (<RefLink id="lewandowsky2021">Lewandowsky et al., 2021</RefLink>).
          Counter talking-points are sourced from peer-reviewed climate literature and
          consensus statements (<RefLink id="cook2013">Cook et al., 2013</RefLink>;{' '}
          <RefLink id="lynas2021">Lynas et al., 2021</RefLink>).
        </Para>
      </Section>

      {/* Limitations */}
      <Section title="Limitations">
        <Para>
          <strong style={{ color: UN.textMain }}>Taxonomic coverage.</strong>{' '}
          The five-cluster taxonomy unifies{' '}
          <RefLink id="cook2022">FLICC</RefLink>,{' '}
          <RefLink id="coan2021">CARDS</RefLink>, and the{' '}
          <RefLink id="lamb2020">4D framework</RefLink>{' '}
          but remains an approximation. Real-world disinformation often blends multiple
          techniques simultaneously, and cluster boundaries are analytically imposed rather
          than empirically sharp. Sub-technique labels inherit the conceptual ambiguities
          present in their source taxonomies.
        </Para>
        <Para>
          <strong style={{ color: UN.textMain }}>LLM generation fidelity.</strong>{' '}
          Outputs are produced by instruction-following language models via a
          red-teaming paradigm (<RefLink id="perez2022">Perez et al., 2022</RefLink>) and reflect the
          model's interpretation of the prompt rather than verified disinformation
          strategies. Generated content may be implausible, overly explicit, or fail to
          replicate the subtlety of authentic influence-campaign material. Model safety
          filters may suppress some outputs, introducing systematic gaps.
        </Para>
        <Para>
          <strong style={{ color: UN.textMain }}>Persona targeting validity.</strong>{' '}
          The <RefLink id="leite2025">AI-TRAITS</RefLink> persona methodology maps demographic dimensions (country,
          generation, political orientation) onto prompt attributes. This is a proxy
          operationalisation: it does not guarantee that outputs would resonate with
          actual members of the target group, and cultural stereotypes embedded in
          training data may produce inaccurate or reductive representations.
        </Para>
        <Para>
          <strong style={{ color: UN.textMain }}>Inoculation efficacy assumptions.</strong>{' '}
          The prebunking and debunking responses are grounded in published inoculation
          research but have not been independently validated for this specific tool or
          content domain. Effect sizes in inoculation studies vary substantially across
          populations, platforms, and message formats (<RefLink id="roozenbeek2022">Roozenbeek et al., 2022</RefLink>).
        </Para>
        <Para>
          <strong style={{ color: UN.textMain }}>Scope.</strong>{' '}
          The tool is designed for English-language climate disinformation research.
          Linguistic, cultural, and political dynamics in other languages and regions
          are not captured. Headlines are anchored to a Western media register and
          may not transfer to other media ecosystems.
        </Para>
      </Section>

      <Divider sx={{ mb: 3, borderColor: UN.border }} />

      {/* References */}
      <Section title="References">
        <Box id="references" sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {REFERENCES.map((ref) => (
            <Box key={ref.id} sx={{ pl: 2, borderLeft: `3px solid ${UN.border}` }}>
              <Typography variant="caption" sx={{ color: UN.textMain, display: 'block', lineHeight: 1.6 }}>
                <strong>{ref.authors}</strong>{' '}({ref.year}).{' '}
                {ref.url ? (
                  <Link href={ref.url} target="_blank" rel="noopener" underline="hover" sx={{ color: UN.primary }}>
                    {ref.title}
                  </Link>
                ) : (
                  <em>{ref.title}</em>
                )}
                {ref.journal && <>{' '}<em>{ref.journal}</em></>}
                {ref.vol && <>{' '}{ref.vol}</>}
              </Typography>
            </Box>
          ))}
        </Box>
      </Section>

    </Box>
  );
}
