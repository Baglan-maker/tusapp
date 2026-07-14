import { StyleSheet, View } from 'react-native';

import { colors } from '../theme/tokens';

/** Onboarding progress — three dots, gold for the active one. */
export function Steps({ current, total = 3 }: { current: number; total?: number }) {
  return (
    <View style={styles.row}>
      {Array.from({ length: total }, (_, i) => (
        <View key={i} style={[styles.dot, i === current && styles.dotOn]} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: 8 },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(167,155,200,0.28)',
  },
  dotOn: { backgroundColor: colors.gold, width: 22 },
});
