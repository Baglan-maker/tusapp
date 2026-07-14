import { LinearGradient } from 'expo-linear-gradient';
import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View, type TextStyle, type ViewStyle } from 'react-native';

import { colors, fonts, goldGradient, radius, spacing } from '../theme/tokens';

/** Large serif heading. Alice has one weight — never ask for bold here. */
export function Display({
  children,
  size = 34,
  style,
}: {
  children: ReactNode;
  size?: number;
  style?: TextStyle;
}) {
  return (
    <Text
      style={[
        { fontFamily: fonts.display, fontSize: size, lineHeight: size * 1.12, color: colors.dawn },
        style,
      ]}
    >
      {children}
    </Text>
  );
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return <Text style={styles.eyebrow}>{children}</Text>;
}

export function Body({
  children,
  muted,
  size = 14,
  style,
}: {
  children: ReactNode;
  muted?: boolean;
  size?: number;
  style?: TextStyle;
}) {
  return (
    <Text
      style={[
        {
          fontFamily: fonts.body,
          fontSize: size,
          lineHeight: size * 1.6,
          color: muted ? colors.lilac : colors.dawn,
        },
        style,
      ]}
    >
      {children}
    </Text>
  );
}

export function Card({ children, style }: { children: ReactNode; style?: ViewStyle }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

/** The one gold call-to-action. There is never more than one on a screen. */
export function GoldButton({
  label,
  onPress,
  disabled,
  style,
}: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  style?: ViewStyle;
}) {
  return (
    <Pressable onPress={onPress} disabled={disabled} style={[{ opacity: disabled ? 0.4 : 1 }, style]}>
      <LinearGradient
        colors={goldGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.cta}
      >
        <Text style={styles.ctaLabel}>{label}</Text>
      </LinearGradient>
    </Pressable>
  );
}

export function GhostButton({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <Pressable onPress={onPress} style={styles.ghostWrap}>
      <Text style={styles.ghost}>{label}</Text>
    </Pressable>
  );
}

export function Chip({
  label,
  active,
  locked,
  onPress,
  icon,
}: {
  label: string;
  active?: boolean;
  locked?: boolean;
  onPress?: () => void;
  icon?: ReactNode;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={[styles.chip, active && styles.chipOn, locked && styles.chipLocked]}
    >
      {icon}
      <Text style={[styles.chipLabel, active && styles.chipLabelOn]}>{label}</Text>
    </Pressable>
  );
}

export function Tag({ label }: { label: string }) {
  return (
    <View style={styles.tag}>
      <Text style={styles.tagLabel}>{label}</Text>
    </View>
  );
}

export function Row({ children, style }: { children: ReactNode; style?: ViewStyle }) {
  return <View style={[styles.row, style]}>{children}</View>;
}

const styles = StyleSheet.create({
  eyebrow: {
    fontFamily: fonts.bold,
    fontSize: 10.5,
    letterSpacing: 2.4,
    color: colors.gold,
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.card,
    padding: spacing.lg,
  },
  cta: {
    height: 56,
    borderRadius: radius.button,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ctaLabel: {
    fontFamily: fonts.extrabold,
    fontSize: 15,
    color: colors.midnight,
  },
  ghostWrap: { paddingVertical: spacing.md, alignItems: 'center' },
  ghost: { fontFamily: fonts.semibold, fontSize: 14, color: colors.lilac },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: radius.chip,
    borderWidth: 1,
    borderColor: colors.borderChip,
  },
  chipOn: { backgroundColor: colors.gold, borderColor: colors.gold },
  chipLocked: { opacity: 0.55 },
  chipLabel: { fontFamily: fonts.semibold, fontSize: 12.5, color: colors.lilac },
  chipLabelOn: { fontFamily: fonts.extrabold, color: colors.midnight },
  tag: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: radius.tag,
    backgroundColor: colors.surfaceStrong,
  },
  tagLabel: { fontFamily: fonts.semibold, fontSize: 11.5, color: colors.lilac },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
});
