import { router } from 'expo-router';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { RetryBanner } from '../../src/components/RetryBanner';
import { Screen } from '../../src/components/Screen';
import { Steps } from '../../src/components/Steps';
import { Body, Display, GoldButton } from '../../src/components/ui';
import { useUpdateProfile } from '../../src/hooks/useProfile';
import type { Lens } from '../../src/lib/api';
import { colors, fonts, radius, spacing } from '../../src/theme/tokens';

const LENSES: Lens[] = ['psych', 'classic', 'ibn_sirin', 'science'];

export default function LensStep() {
  const { t } = useTranslation();
  const [selected, setSelected] = useState<Lens>('psych');
  const update = useUpdateProfile();

  function finish() {
    update.mutate(
      { default_lens: selected, onboarding_completed: true },
      { onSuccess: () => router.replace('/(tabs)') },
    );
  }

  return (
    <Screen style={styles.screen}>
      <View style={{ gap: spacing.xl }}>
        <Steps current={2} />
        <Display size={34}>{t('onboarding.lens.title')}</Display>
        <Body muted>{t('onboarding.lens.note')}</Body>

        <View style={{ gap: spacing.sm }}>
          {LENSES.map((lens) => {
            const active = selected === lens;
            return (
              <Pressable
                key={lens}
                onPress={() => setSelected(lens)}
                style={[styles.option, active && styles.optionOn]}
              >
                <Text style={[styles.title, active && styles.titleOn]}>
                  {t(`onboarding.lens.${lens}`)}
                </Text>
                <Text style={styles.note}>{t(`onboarding.lens.${lens}Note`)}</Text>
              </Pressable>
            );
          })}
        </View>
      </View>

      <View style={{ gap: spacing.sm }}>
        {update.isError && <RetryBanner onRetry={finish} />}
        <GoldButton label={t('onboarding.done')} onPress={finish} disabled={update.isPending} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { justifyContent: 'space-between', paddingTop: spacing.xxl, paddingBottom: spacing.xxl },
  option: {
    padding: 18,
    borderRadius: radius.card,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  optionOn: { borderColor: colors.gold, backgroundColor: 'rgba(233,200,126,0.08)' },
  title: { fontFamily: fonts.semibold, fontSize: 15.5, color: colors.lilac },
  titleOn: { color: colors.dawn },
  note: { fontFamily: fonts.body, fontSize: 12.5, color: colors.lilacDim, marginTop: 4 },
});
