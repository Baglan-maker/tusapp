import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useTranslation } from 'react-i18next';

import { colors, fonts, radius } from '../theme/tokens';

/**
 * Network failures are never swallowed: the user sees what broke and a way to
 * retry, instead of an empty screen.
 */
export function RetryBanner({ onRetry, message }: { onRetry: () => void; message?: string }) {
  const { t } = useTranslation();
  return (
    <View style={styles.banner}>
      <Text style={styles.text}>{message ?? t('error.network')}</Text>
      <Pressable onPress={onRetry} hitSlop={10}>
        <Text style={styles.retry}>{t('error.retry')}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderRadius: radius.chip,
    backgroundColor: 'rgba(46,37,89,0.7)',
    borderWidth: 1,
    borderColor: colors.borderGold,
  },
  text: { flex: 1, fontFamily: fonts.medium, fontSize: 13, color: colors.dawn },
  retry: { fontFamily: fonts.extrabold, fontSize: 13, color: colors.gold },
});
