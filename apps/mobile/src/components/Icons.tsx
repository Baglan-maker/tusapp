/** Line icons only — no emoji anywhere in the UI. Stroke 1.6–2, round caps. */
import Svg, { Circle, Path, Rect } from 'react-native-svg';

import { colors } from '../theme/tokens';

type Props = { size?: number; color?: string; strokeWidth?: number };

const base = ({ size = 22, color = colors.lilac, strokeWidth = 1.6 }: Props) => ({
  width: size,
  height: size,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: color,
  strokeWidth,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
});

export function MicIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Rect x="9" y="3" width="6" height="12" rx="3" />
      <Path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
    </Svg>
  );
}

export function StopIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Rect x="7" y="7" width="10" height="10" rx="2" />
    </Svg>
  );
}

export function BookIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13z" />
    </Svg>
  );
}

export function ChartIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Path d="M3 17l5-6 4 3 6-8 3 4" />
    </Svg>
  );
}

export function UserIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Circle cx="12" cy="8" r="4" />
      <Path d="M4 21c1.5-4 5-6 8-6s6.5 2 8 6" />
    </Svg>
  );
}

export function MoonIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" />
    </Svg>
  );
}

export function LockIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Rect x="5" y="11" width="14" height="9" rx="2" />
      <Path d="M8 11V8a4 4 0 0 1 8 0v3" />
    </Svg>
  );
}

export function BackIcon(p: Props) {
  return (
    <Svg {...base(p)}>
      <Path d="M15 5l-7 7 7 7" />
    </Svg>
  );
}
