import { useMutation } from '@tanstack/react-query';
import {
  AudioModule,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorder,
} from 'expo-audio';
import { router } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ScrollView, StyleSheet, View } from 'react-native';

import { MoonButton } from '../../src/components/Moon';
import { RetryBanner } from '../../src/components/RetryBanner';
import { Screen } from '../../src/components/Screen';
import { Body, Chip, Display, Eyebrow, GhostButton, GoldButton, Row } from '../../src/components/ui';
import { useProfile } from '../../src/hooks/useProfile';
import { createDreamFromAudio, type AppLocale } from '../../src/lib/api';
import { MAX_RECORDING_SECONDS, spacing } from '../../src/theme/tokens';

const EMOTIONS = [
  'fear',
  'anxiety',
  'sadness',
  'anger',
  'shame',
  'confusion',
  'surprise',
  'joy',
  'peace',
  'love',
  'excitement',
  'disgust',
] as const;

type Phase = 'idle' | 'recording' | 'emotions';

function mmss(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

export default function RecordScreen() {
  const { t } = useTranslation();
  const { data: profile } = useProfile();
  const language: AppLocale = profile?.locale ?? 'ru';

  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const [phase, setPhase] = useState<Phase>('idle');
  const [seconds, setSeconds] = useState(0);
  const [uri, setUri] = useState<string | null>(null);
  const [denied, setDenied] = useState(false);
  const [inDream, setInDream] = useState<string[]>([]);
  const [onWaking, setOnWaking] = useState<string[]>([]);
  const tick = useRef<ReturnType<typeof setInterval> | null>(null);

  const stop = useCallback(async () => {
    if (tick.current) clearInterval(tick.current);
    tick.current = null;
    await recorder.stop();
    setUri(recorder.uri ?? null);
    setPhase('emotions');
  }, [recorder]);

  // The 120s cap is enforced here, not just in the UI copy.
  useEffect(() => {
    if (phase !== 'recording') return;
    if (seconds >= MAX_RECORDING_SECONDS) void stop();
  }, [phase, seconds, stop]);

  useEffect(() => () => (tick.current ? clearInterval(tick.current) : undefined), []);

  async function start() {
    const permission = await AudioModule.requestRecordingPermissionsAsync();
    if (!permission.granted) return setDenied(true);
    setDenied(false);

    await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
    await recorder.prepareToRecordAsync();
    recorder.record();

    setSeconds(0);
    setPhase('recording');
    tick.current = setInterval(() => setSeconds((s) => s + 1), 1000);
  }

  const submit = useMutation({
    mutationFn: () => {
      if (!uri) throw new Error('no recording');
      return createDreamFromAudio({
        uri,
        language,
        emotionsInDream: inDream,
        emotionsOnWaking: onWaking,
      });
    },
    onSuccess: (dream) => {
      reset();
      router.push(`/dream/${dream.dream_id}/transcript`);
    },
  });

  function reset() {
    setPhase('idle');
    setSeconds(0);
    setUri(null);
    setInDream([]);
    setOnWaking([]);
  }

  function toggle(list: string[], set: (v: string[]) => void, slug: string) {
    set(list.includes(slug) ? list.filter((s) => s !== slug) : [...list, slug]);
  }

  if (phase === 'emotions') {
    return (
      <Screen style={styles.screen}>
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ gap: spacing.xl }}>
          <Display size={30} style={{ marginTop: spacing.lg }}>
            {t('emotions.title')}
          </Display>

          <View style={{ gap: spacing.sm }}>
            <Eyebrow>{t('emotions.inDream')}</Eyebrow>
            <Row>
              {EMOTIONS.map((e) => (
                <Chip
                  key={`in-${e}`}
                  label={t(`emotions.${e}`)}
                  active={inDream.includes(e)}
                  onPress={() => toggle(inDream, setInDream, e)}
                />
              ))}
            </Row>
          </View>

          <View style={{ gap: spacing.sm }}>
            <Eyebrow>{t('emotions.onWaking')}</Eyebrow>
            <Row>
              {EMOTIONS.map((e) => (
                <Chip
                  key={`on-${e}`}
                  label={t(`emotions.${e}`)}
                  active={onWaking.includes(e)}
                  onPress={() => toggle(onWaking, setOnWaking, e)}
                />
              ))}
            </Row>
          </View>
        </ScrollView>

        <View style={{ gap: spacing.xs, paddingBottom: spacing.md }}>
          {submit.isError && <RetryBanner onRetry={() => submit.mutate()} />}
          <GoldButton
            label={t('emotions.send')}
            onPress={() => submit.mutate()}
            disabled={submit.isPending}
          />
          <GhostButton label={t('emotions.skip')} onPress={reset} />
        </View>
      </Screen>
    );
  }

  return (
    <Screen style={styles.screen} stars={20}>
      <View style={styles.header}>
        <Display size={34}>{t('record.greeting')}</Display>
      </View>

      <View style={styles.center}>
        <MoonButton recording={phase === 'recording'} onPress={() => (phase === 'recording' ? void stop() : void start())} />
        <Body muted size={13} style={{ marginTop: spacing.md }}>
          {phase === 'recording'
            ? `${mmss(seconds)} · ${t('record.tapToStop')}`
            : t('record.hint')}
        </Body>
        {denied && (
          <Body size={12} style={{ marginTop: spacing.sm }}>
            {t('record.permission')}
          </Body>
        )}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { justifyContent: 'space-between' },
  header: { marginTop: spacing.lg },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', marginBottom: 60 },
});
