import React from 'react';
import { Box, Typography } from '@mui/material';

const UN = {
  primary:   '#009B55',
  textMain:  '#1A2E1A',
  textMuted: '#4A6550',
  border:    '#C8DFC8',
};

export default function DescriptionPanel({ fullPage }) {
  const titleVariant = fullPage ? 'h5' : 'h6';
  const bodyVariant = fullPage ? 'body1' : 'body2';
  const spacing = fullPage ? { p: 0, '& .MuiTypography-root + .MuiTypography-root': { mt: 2.5 } } : { p: 2, '& .MuiTypography-root + .MuiTypography-root': { mt: 1.5 } };

  return (
    <Box sx={spacing}>
      <Typography variant={titleVariant} sx={{ fontWeight: 700, color: UN.textMain, mb: fullPage ? 2.5 : 1 }}>
        Methodology
      </Typography>

      <Typography variant={bodyVariant} sx={{ color: UN.textMuted, lineHeight: 1.7 }}>
        This lab uses <strong style={{ color: UN.textMain }}>inoculation theory</strong>: exposing people to weakened or labelled forms of misinformation helps them recognise and resist it later. We present a <strong style={{ color: UN.textMain }}>technique-based toolkit</strong> that shows how accurate information is warped into disinformation.
      </Typography>

      <Typography variant={bodyVariant} sx={{ color: UN.textMuted, lineHeight: 1.7 }}>
        We draw on <strong style={{ color: UN.textMain }}>several taxonomies</strong> of disinformation techniques (e.g. FLICC, CARDS, 4D) unified into a single schema. The toolkit highlights how <strong style={{ color: UN.textMain }}>traits and content types</strong>—such as persona targeting and format (headlines, social posts)—enhance the persuasive effect of disinformation.
      </Typography>

      <Typography variant={bodyVariant} sx={{ color: UN.textMuted, lineHeight: 1.7 }}>
        Headlines are sourced from <strong style={{ color: UN.textMain }}>real news</strong> on extreme events and environmental topics. Research shows these domains are among the most susceptible to disinformation, so they provide a realistic testbed for inoculation and counter-messaging.
      </Typography>
    </Box>
  );
}
