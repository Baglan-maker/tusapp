import { useEffect } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import Animated, {
  Easing,
  useAnimatedStyle,
  useReducedMotion,
  useSharedValue,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';
import Svg, { Circle, Defs, RadialGradient, Stop } from 'react-native-svg';

import { colors, moon } from '../theme/tokens';
import { MicIcon, StopIcon } from './Icons';

/** The moon's body: a warm radial gradient sphere. */
function MoonBody({ size }: { size: number }) {
  return (
    <Svg width={size} height={size}>
      <Defs>
        <RadialGradient id="moon" cx="38%" cy="32%" r="70%">
          <Stop offset="0" stopColor="#FBF3E0" />
          <Stop offset="0.58" stopColor={colors.gold} />
          <Stop offset="1" stopColor={colors.goldDeep} />
        </RadialGradient>
      </Defs>
      <Circle cx={size / 2} cy={size / 2} r={size / 2} fill="url(#moon)" />
    </Svg>
  );
}

/**
 * The record button. It breathes (scale 1 → 1.045 over 4.2s) so the screen feels
 * alive at 6am — unless the user asked for reduced motion, in which case it sits still.
 */
export function MoonButton({
  recording,
  onPress,
}: {
  recording: boolean;
  onPress: () => void;
}) {
  const reduced = useReducedMotion();
  const scale = useSharedValue(1);

  useEffect(() => {
    if (reduced) {
      scale.value = 1;
      return;
    }
    scale.value = withRepeat(
      withTiming(moon.scaleTo, {
        duration: moon.breatheMs / 2,
        easing: Easing.inOut(Easing.ease),
      }),
      -1,
      true,
    );
  }, [reduced, scale]);

  const animated = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));

  return (
    <Pressable onPress={onPress} hitSlop={20}>
      <View style={styles.rings}>
        <View style={[styles.ring, styles.ringOuter]} />
        <View style={[styles.ring, styles.ringInner]} />
        <Animated.View style={[styles.moonWrap, animated]}>
          <MoonBody size={moon.size} />
          <View style={styles.icon}>
            {recording ? (
              <StopIcon size={34} color={colors.midnight} strokeWidth={2} />
            ) : (
              <MicIcon size={34} color={colors.midnight} strokeWidth={2} />
            )}
          </View>
        </Animated.View>
      </View>
    </Pressable>
  );
}

/** Interpretation takes 10–20s. Rather than a spinner, the moon "thinks". */
export function MoonThinking() {
  const reduced = useReducedMotion();
  const opacity = useSharedValue(0.55);

  useEffect(() => {
    if (reduced) {
      opacity.value = 0.8;
      return;
    }
    opacity.value = withRepeat(
      withTiming(1, { duration: 1400, easing: Easing.inOut(Easing.ease) }),
      -1,
      true,
    );
  }, [reduced, opacity]);

  const animated = useAnimatedStyle(() => ({ opacity: opacity.value }));

  return (
    <Animated.View style={[styles.thinking, animated]}>
      <MoonBody size={104} />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  rings: {
    width: 320,
    height: 320,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ring: {
    position: 'absolute',
    borderRadius: 999,
    borderWidth: 1,
  },
  ringInner: {
    width: 250,
    height: 250,
    borderColor: 'rgba(233,200,126,0.22)',
  },
  ringOuter: {
    width: 320,
    height: 320,
    borderColor: 'rgba(233,200,126,0.10)',
  },
  moonWrap: {
    width: moon.size,
    height: moon.size,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: moon.size / 2,
    // The glow. Android ignores shadow* — elevation gives it some lift.
    shadowColor: colors.gold,
    shadowOpacity: 0.45,
    shadowRadius: 45,
    shadowOffset: { width: 0, height: 0 },
    elevation: 18,
  },
  icon: { position: 'absolute' },
  thinking: { alignItems: 'center', justifyContent: 'center' },
});
