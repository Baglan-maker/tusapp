import { useTranslation } from 'react-i18next';
import { StyleSheet, View } from 'react-native';

import { Screen } from '../../src/components/Screen';
import { Body, Display, GhostButton } from '../../src/components/ui';
import { supabase } from '../../src/lib/supabase';
import { spacing } from '../../src/theme/tokens';

/** Placeholder — settings and privacy land later. Sign-out is here so the auth
 * flow is testable end to end. */
export default function ProfileTab() {
  const { t } = useTranslation();
  return (
    <Screen>
      <View style={styles.center}>
        <Display size={40}>{t('soon.title')}</Display>
        <Body muted style={{ marginTop: spacing.md, textAlign: 'center' }}>
          {t('soon.profile')}
        </Body>
        <GhostButton label="Sign out" onPress={() => void supabase.auth.signOut()} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});
