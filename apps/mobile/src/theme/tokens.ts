/**
 * Design tokens — "Предрассветный час". Mirrors tus-ui-v2.html.
 * Dark theme is the only theme. Gold is the only accent. No neon, no emoji.
 */

export const colors = {
  midnight: '#0F0B22',
  deep: '#151030',
  depth: '#221A4A',
  haze: '#2E2559',

  gold: '#E9C87E',
  goldDeep: '#CEA45A',
  champagne: '#F6E9CC',

  dawn: '#F5F2FB', // primary text
  lilac: '#A79BC8', // secondary text
  lilacDim: '#7B6FA0', // dim text

  surface: 'rgba(46,37,89,0.38)',
  surfaceStrong: 'rgba(46,37,89,0.55)',
  border: 'rgba(167,155,200,0.16)',
  borderChip: 'rgba(167,155,200,0.28)',
  borderGold: 'rgba(233,200,126,0.40)',
} as const;

/** Background gradient of every screen (178deg in the mock ≈ top → bottom). */
export const backgroundGradient = ['#221A4A', '#120D2C', '#0F0B22'] as const;
export const backgroundLocations = [0, 0.52, 1] as const;

/** Gold gradient — buttons and the moon. */
export const goldGradient = [colors.champagne, colors.gold, colors.goldDeep] as const;

export const radius = {
  card: 24,
  button: 28,
  chip: 18,
  tag: 14,
} as const;

export const spacing = {
  xs: 6,
  sm: 10,
  md: 16,
  lg: 22,
  xl: 28,
  xxl: 40,
} as const;

/** Alice ships a single weight (400) — there is no bold display face. */
export const fonts = {
  display: 'Alice_400Regular',
  body: 'Manrope_400Regular',
  medium: 'Manrope_500Medium',
  semibold: 'Manrope_600SemiBold',
  bold: 'Manrope_700Bold',
  extrabold: 'Manrope_800ExtraBold',
} as const;

export const moon = {
  size: 176,
  breatheMs: 4200,
  scaleTo: 1.045,
} as const;

export const MAX_RECORDING_SECONDS = 120;
