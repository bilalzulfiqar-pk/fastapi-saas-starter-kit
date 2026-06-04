"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useCurrentUser } from "@/hooks/use-current-user";
import { apiFetch } from "@/lib/api-client";

export default function ProfileSettingsPage() {
  const currentUser = useCurrentUser();
  const queryClient = useQueryClient();
  const user = currentUser.data?.data.user;
  const [name, setName] = useState<string | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const draftName = name ?? user?.name ?? "";
  const draftAvatarUrl = avatarUrl ?? user?.avatar_url ?? "";

  const updateProfile = useMutation({
    mutationFn: () =>
      apiFetch("/api/v1/users/me", {
        method: "PATCH",
        bodyJson: { name: draftName, avatar_url: draftAvatarUrl },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["current-user"] });
    },
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await updateProfile.mutateAsync();
  }

  return (
    <Card>
      <h1>Profile</h1>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Name
          <Input onChange={(event) => setName(event.target.value)} value={draftName} />
        </label>
        <label>
          Avatar URL
          <Input onChange={(event) => setAvatarUrl(event.target.value)} value={draftAvatarUrl} />
        </label>
        {updateProfile.error ? <p className="error">{updateProfile.error.message}</p> : null}
        <Button disabled={updateProfile.isPending} type="submit">
          Save profile
        </Button>
      </form>
    </Card>
  );
}
