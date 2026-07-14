import { LinearGradient } from 'expo-linear-gradient';
import { useEffect, useMemo, type ReactNode } from 'react';
import { StyleSheet, View, type ViewStyle } from 'react-native';
import Animated, {
  Easing,
  useAnimatedStyle,
  useReducedMotion,
  useSharedValue,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';
import Svg, { Defs, RadialGradient, Rect, Stop } from 'react-native-svg';
import { SafeAreaView } from 'react-native-safe-area-context';

import { backgroundGradient, backgroundLocations, colors } from '../theme/tokens';

/** Nebula glows — the mock's two radial blobs (warm gold, cool violet). */
function Nebula() {
  return (
    <Svg style={StyleSheet.absoluteFill} pointerEvents="none">
      <Defs>
        <RadialGradient id="warm" cx="12%" cy="8%" r="55%">
          <Stop offset="0" stopColor={colors.gold} stopOpacity="0.10" />
          <Stop offset="1" stopColor={colors.gold} stopOpacity="0" />
        </RadialGradient>
        <RadialGradient id="cool" cx="92%" cy="88%" r="60%">
          <Stop offset="0" stopColor="#7A62D0" stopOpacity="0.16" />
          <Stop offset="1" stopColor="#7A62D0" stopOpacity="0" />
        </RadialGradient>
      </Defs>
      <Rect x="0" y="0" width="100%" height="100%" fill="url(#warm)" />
      <Rect x="0" y="0" width="100%" height="100%" fill="url(#cool)" />
    </Svg>
  );
}

function Star({
  top,
  left,
  size,
  twinkles,
}: {
  top: string;
  left: string;
  size: number;
  twinkles: boolean;
}) {
  const reduced = useReducedMotion();
  const opacity = useSharedValue(0.45);

  useEffect(() => {
    if (twinkles && !reduced) {
      opacity.value = withRepeat(
        withTiming(0.85, { duration: 4500, easing: Easing.inOut(Easing.ease) }),
        -1,
        true,
      );
    } else {
      opacity.value = 0.45;
    }
  }, [twinkles, reduced, opacity]);

  const style = useAnimatedStyle(() => ({ opacity: opacity.value }));

  return (
    <Animated.View
      pointerEvents="none"
      style={[
        {
          position: 'absolute',
          top: top as unknown as number,
          left: left as unknown as number,
          width: size,
          height: size,
          borderRadius: size / 2,
          backgroundColor: colors.champagne,
        },
        style,
      ]}
    />
  );
}

function Starfield({ count = 16 }: { count?: number }) {
  // Positions are stable for the life of the screen — a re-randomising sky is
  // distracting, and this runs on every render otherwise.
  const stars = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        key: i,
        top: `${Math.round(Math.random() * 70)}%`,
        left: `${Math.round(Math.random() * 92)}%`,
        size: Math.random() > 0.7 ? 2.5 : 1.5,
        twinkles: i % 3 === 0,
      })),
    [count],
  );
  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {stars.map((s) => (
        <Star key={s.key} top={s.top} left={s.left} size={s.size} twinkles={s.twinkles} />
      ))}
    </View>
  );
}

export function Screen({
  children,
  style,
  stars = 16,
}: {
  children: ReactNode;
  style?: ViewStyle;
  stars?: number;
}) {
  return (
    <View style={styles.root}>
      <LinearGradient
        colors={backgroundGradient}
        locations={backgroundLocations}
        style={StyleSheet.absoluteFill}
      />
      <Nebula />
      <Starfield count={stars} />
      <SafeAreaView style={[styles.safe, style]}>{children}</SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.midnight },
  safe: { flex: 1, paddingHorizontal: 24 },
});
