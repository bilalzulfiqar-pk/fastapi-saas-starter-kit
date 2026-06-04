"use client";

import { useMutation } from "@tanstack/react-query";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiFetch } from "@/lib/api-client";

export default function SecuritySettingsPage() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      apiFetch("/api/v1/users/me/change-password", {
        method: "POST",
        bodyJson: { current_password: currentPassword, new_password: newPassword },
      }),
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await mutation.mutateAsync();
    setCurrentPassword("");
    setNewPassword("");
  }

  return (
    <Card>
      <h1>Security</h1>
      <p className="muted">Cookie-first auth with origin validation on unsafe requests is enabled in the API.</p>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Current password
          <Input onChange={(event) => setCurrentPassword(event.target.value)} type="password" value={currentPassword} />
        </label>
        <label>
          New password
          <Input onChange={(event) => setNewPassword(event.target.value)} type="password" value={newPassword} />
        </label>
        {mutation.error ? <p className="error">{mutation.error.message}</p> : null}
        <Button disabled={mutation.isPending} type="submit">
          Update password
        </Button>
      </form>
    </Card>
  );
}

