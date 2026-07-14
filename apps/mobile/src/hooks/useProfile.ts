import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { getProfile, updateProfile, type Profile } from '../lib/api';

export const profileKey = ['profile'] as const;

export function useProfile(enabled = true) {
  return useQuery({ queryKey: profileKey, queryFn: getProfile, enabled });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (patch: Partial<Profile>) => updateProfile(patch),
    onSuccess: (profile) => qc.setQueryData(profileKey, profile),
  });
}
