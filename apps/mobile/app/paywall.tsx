import { router } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { StyleSheet, View } from 'react-native';

import { MoonThinking } from '../src/components/Moon';
import { Screen } from '../src/components/Screen';
import { Body, Display, GoldButton } from '../src/components/ui';
import { spacing } from '../src/theme/tokens';

/** Placeholder. RevenueCat lands after the beta — for now this just explains. */
export default function Paywall() {
  const { t } = useTranslation();
  return (
    <Screen style={styles.screen} stars={26}>
      <View style={styles.center}>
        <MoonThinking />
        <Display size={40} style={{ marginTop: spacing.xl, textAlign: 'center' }}>
          {t('paywall.title')}
        </Display>
        <Body muted style={{ marginTop: spacing.md, textAlign: 'center' }}>
          {t('paywall.quota')}
        </Body>
        <Body muted size={13} style={{ marginTop: spacing.sm, textAlign: 'center' }}>
          {t('paywall.body')}
        </Body>
      </View>
      <GoldButton
        label={t('paywall.back')}
        onPress={() => (router.canGoBack() ? router.back() : router.replace('/(tabs)'))}
        style={{ marginBottom: spacing.xxl }}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { justifyContent: 'space-between' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
