import { useMutation } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { KeyboardAvoidingView, Platform, StyleSheet, TextInput, View } from 'react-native';

import { RetryBanner } from '../../../src/components/RetryBanner';
import { Screen } from '../../../src/components/Screen';
import { Body, Display, Eyebrow, GoldButton } from '../../../src/components/ui';
import { useProfile } from '../../../src/hooks/useProfile';
import { updateTranscript } from '../../../src/lib/api';
import { colors, fonts, radius, spacing } from '../../../src/theme/tokens';

/**
 * Editable transcript. STT on Kazakh is the weakest link in the pipeline, so the
 * user always gets to fix the text before we spend an interpretation on it.
 */
export default function TranscriptScreen() {
  const { t } = useTranslation();
  const { id, text } = useLocalSearchParams<{ id: string; text?: string }>();
  const { data: profile } = useProfile();
  const [value, setValue] = useState(text ?? '');

  const save = useMutation({
    mutationFn: () => updateTranscript(id, value.trim()),
    onSuccess: () =>
      router.push({
        pathname: '/dream/[id]/result',
        params: { id, lens: profile?.default_lens ?? 'psych' },
      }),
  });

  return (
    <Screen style={styles.screen}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.flex}
      >
        <View style={{ gap: spacing.sm, marginTop: spacing.lg }}>
          <Eyebrow>{t('transcript.title')}</Eyebrow>
          <Display size={30}>{t('transcript.title')}</Display>
          <Body muted size={13}>
            {t('transcript.note')}
          </Body>
        </View>

        <TextInput
          value={value}
          onChangeText={setValue}
          multiline
          textAlignVertical="top"
          placeholder={t('transcript.placeholder')}
          placeholderTextColor={colors.lilacDim}
          style={styles.input}
        />

        <View style={{ gap: spacing.sm, paddingBottom: spacing.md }}>
          {save.isError && <RetryBanner onRetry={() => save.mutate()} />}
          <GoldButton
            label={t('transcript.interpret')}
            onPress={() => save.mutate()}
            disabled={!value.trim() || save.isPending}
          />
        </View>
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { justifyContent: 'space-between' },
  flex: { flex: 1, justifyContent: 'space-between' },
  input: {
    flex: 1,
    marginVertical: spacing.lg,
    padding: 18,
    borderRadius: radius.card,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.dawn,
    fontFamily: fonts.body,
    fontSize: 15.5,
    lineHeight: 25,
  },
});
