import { router } from 'expo-router';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { RetryBanner } from '../../src/components/RetryBanner';
import { Screen } from '../../src/components/Screen';
import { Steps } from '../../src/components/Steps';
import { Body, Display, GoldButton } from '../../src/components/ui';
import { useUpdateProfile } from '../../src/hooks/useProfile';
import { setLocale, type AppLocale } from '../../src/i18n';
import { colors, fonts, radius, spacing } from '../../src/theme/tokens';

const OPTIONS: { value: AppLocale; label: string; native: string }[] = [
  { value: 'ru', label: 'Русский', native: 'Русский' },
  { value: 'kk', label: 'Қазақша', native: 'Қазақша' },
];

export default function LanguageStep() {
  const { t } = useTranslation();
  const [selected, setSelected] = useState<AppLocale>('ru');
  const update = useUpdateProfile();

  function pick(locale: AppLocale) {
    setSelected(locale);
    // i18n flips immediately — the rest of onboarding is already in their language.
    setLocale(locale);
  }

  function next() {
    update.mutate(
      { locale: selected },
      { onSuccess: () => router.push('/(onboarding)/wake-time') },
    );
  }

  return (
    <Screen style={styles.screen}>
      <View style={{ gap: spacing.xl }}>
        <Steps current={0} />
        <Display size={34}>{t('onboarding.language.title')}</Display>
        <Body muted>{t('onboarding.language.note')}</Body>

        <View style={{ gap: spacing.sm }}>
          {OPTIONS.map((o) => (
            <Pressable
              key={o.value}
              onPress={() => pick(o.value)}
              style={[styles.option, selected === o.value && styles.optionOn]}
            >
              <Text style={[styles.optionLabel, selected === o.value && styles.optionLabelOn]}>
                {o.native}
              </Text>
            </Pressable>
          ))}
        </View>
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
  option: {
    height: 62,
    justifyContent: 'center',
    paddingHorizontal: 20,
    borderRadius: radius.card,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  optionOn: { borderColor: colors.gold, backgroundColor: 'rgba(233,200,126,0.08)' },
  optionLabel: { fontFamily: fonts.semibold, fontSize: 16, color: colors.lilac },
  optionLabelOn: { color: colors.dawn },
});
