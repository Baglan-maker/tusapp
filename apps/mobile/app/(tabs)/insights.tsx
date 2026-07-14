import { useTranslation } from 'react-i18next';
import { StyleSheet, View } from 'react-native';

import { Screen } from '../../src/components/Screen';
import { Body, Display } from '../../src/components/ui';
import { spacing } from '../../src/theme/tokens';

/** Placeholder — the pattern engine lands after the beta. */
export default function InsightsTab() {
  const { t } = useTranslation();
  return (
    <Screen>
      <View style={styles.center}>
        <Display size={40}>{t('soon.title')}</Display>
        <Body muted style={{ marginTop: spacing.md, textAlign: 'center' }}>
          {t('soon.insights')}
        </Body>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
