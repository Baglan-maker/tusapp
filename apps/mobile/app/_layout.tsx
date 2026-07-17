import { Alice_400Regular } from '@expo-google-fonts/alice';
import {
  Manrope_400Regular,
  Manrope_500Medium,
  Manrope_600SemiBold,
  Manrope_700Bold,
  Manrope_800ExtraBold,
} from '@expo-google-fonts/manrope';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import { View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import '../src/i18n';
import { LocaleSync } from '../src/components/LocaleSync';
import { QuotaError } from '../src/lib/api';
import { colors } from '../src/theme/tokens';

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    Alice_400Regular,
    Manrope_400Regular,
    Manrope_500Medium,
    Manrope_600SemiBold,
    Manrope_700Bold,
    Manrope_800ExtraBold,
  });

  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Retry transient network failures, but never a spent quota.
            retry: (count, error) => !(error instanceof QuotaError) && count < 2,
            staleTime: 30_000,
          },
          mutations: { retry: 0 },
        },
      }),
  );

  if (!fontsLoaded) {
    return <View style={{ flex: 1, backgroundColor: colors.midnight }} />;
  }

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <LocaleSync />
        <StatusBar style="light" />
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: colors.midnight },
            animation: 'fade',
          }}
        >
          <Stack.Screen name="paywall" options={{ presentation: 'modal' }} />
        </Stack>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}
