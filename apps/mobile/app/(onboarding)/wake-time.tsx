import { router } from 'expo-router';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { StyleSheet, View } from 'react-native';

import { RetryBanner } from '../../src/components/RetryBanner';
import { Screen } from '../../src/components/Screen';
import { Steps } from '../../src/components/Steps';
import { Body, Chip, Display, GoldButton, Row } from '../../src/components/ui';
import { useUpdateProfile } from '../../src/hooks/useProfile';
import { spacing } from '../../src/theme/tokens';

const PRESETS = ['05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30'];

export default function WakeTimeStep() {
  const { t } = useTranslation();
  // null == "по-разному": the morning push has no fixed anchor for this user.
  const [selected, setSelected] = useState<string | null>('07:00');
  const update = useUpdateProfile();

  function next() {
    update.mutate(
      { wake_time: selected },
      { onSuccess: () => router.push('/(onboarding)/lens') },
    );
  }

  return (
    <Screen style={styles.screen}>
      <View style={{ gap: spacing.xl }}>
        <Steps current={1} />
        <Display size={34}>{t('onboarding.wake.title')}</Display>
        <Body muted>{t('onboarding.wake.note')}</Body>

        <Row style={{ gap: 10 }}>
          {PRESETS.map((time) => (
            <Chip
              key={time}
              label={time}
              active={selected === time}
              onPress={() => setSelected(time)}
            />
          ))}
          <Chip
            label={t('onboarding.wake.varies')}
            active={selected === null}
            onPress={() => setSelected(null)}
          />
        </Row>
      </View>

      <View style={{ gap: spacing.sm }}>
        {update.isError && <RetryBanner onRetry={next} />}
        <GoldButton label={t('onboarding.next')} onPress={next} disabled={update.isPending} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { justifyContent: 'space-between', paddingTop: spacing.xxl, paddingBottom: spacing.xxl },
});
