import { useQuery } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Pressable, ScrollView, StyleSheet, View } from 'react-native';
import Markdown from 'react-native-markdown-display';

import { BackIcon, LockIcon } from '../../../src/components/Icons';
import { MoonThinking } from '../../../src/components/Moon';
import { RetryBanner } from '../../../src/components/RetryBanner';
import { Screen } from '../../../src/components/Screen';
import { Body, Card, Chip, Display, Eyebrow, Row } from '../../../src/components/ui';
import { useProfile } from '../../../src/hooks/useProfile';
import { interpretDream, QuotaError, type Lens } from '../../../src/lib/api';
import { colors, fonts, spacing } from '../../../src/theme/tokens';

const LENSES: Lens[] = ['psych', 'classic', 'ibn_sirin', 'science'];

export default function ResultScreen() {
  const { t } = useTranslation();
  const params = useLocalSearchParams<{ id: string; lens?: Lens }>();
  const { data: profile } = useProfile();
  const [lens, setLens] = useState<Lens>(params.lens ?? profile?.default_lens ?? 'psych');

  const query = useQuery({
    queryKey: ['interpretation', params.id, lens],
    queryFn: () => interpretDream(params.id, lens),
  });

  // A spent quota is not an error state — it's the paywall.
  useEffect(() => {
    if (query.error instanceof QuotaError) router.replace('/paywall');
  }, [query.error]);

  const unlockedLens = profile?.default_lens ?? 'psych';

  return (
    <Screen style={styles.screen}>
      <Pressable onPress={() => router.back()} hitSlop={12} style={styles.back}>
        <BackIcon color={colors.lilac} />
      </Pressable>

      {query.isPending ? (
        <View style={styles.thinking}>
          <MoonThinking />
          <Body muted size={14} style={{ marginTop: spacing.lg, textAlign: 'center' }}>
            {t('result.thinking')}
          </Body>
          <Body muted size={12} style={{ marginTop: spacing.xs, textAlign: 'center' }}>
            {t('result.thinkingNote')}
          </Body>
        </View>
      ) : query.isError ? (
        <View style={styles.thinking}>
          <RetryBanner onRetry={() => void query.refetch()} />
        </View>
      ) : (
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.body}>
          <Eyebrow>{t('result.eyebrow')}</Eyebrow>

          <Row style={{ marginTop: spacing.md }}>
            {LENSES.map((l) => {
              const locked = l !== unlockedLens;
              return (
                <Chip
                  key={l}
                  label={t(`onboarding.lens.${l}`)}
                  active={l === lens}
                  locked={locked}
                  icon={locked ? <LockIcon size={12} color={colors.lilacDim} /> : undefined}
                  onPress={() => (locked ? router.push('/paywall') : setLens(l))}
                />
              );
            })}
          </Row>

          <Card style={{ marginTop: spacing.lg }}>
            <Markdown style={markdownStyles}>{query.data.content_md}</Markdown>
          </Card>
        </ScrollView>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: {},
  back: { paddingVertical: spacing.md },
  thinking: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  body: { paddingBottom: spacing.xxl },
});

const markdownStyles = {
  body: { color: colors.dawn, fontFamily: fonts.body, fontSize: 15, lineHeight: 25 },
  heading1: { color: colors.dawn, fontFamily: fonts.display, fontSize: 28, lineHeight: 34, marginBottom: 10 },
  heading2: { color: colors.dawn, fontFamily: fonts.display, fontSize: 22, lineHeight: 28, marginTop: 14, marginBottom: 8 },
  heading3: { color: colors.gold, fontFamily: fonts.semibold, fontSize: 13, marginTop: 12, marginBottom: 6 },
  strong: { fontFamily: fonts.bold, color: colors.champagne },
  em: { fontFamily: fonts.medium, color: colors.lilac },
  bullet_list: { marginTop: 6 },
  paragraph: { marginTop: 0, marginBottom: 12 },
} as const;
