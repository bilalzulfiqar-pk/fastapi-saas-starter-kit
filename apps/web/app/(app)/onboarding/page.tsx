"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useCreateWorkspace } from "@/hooks/use-workspaces";

export default function OnboardingPage() {
  const [name, setName] = useState("");
  const router = useRouter();
  const createWorkspace = useCreateWorkspace();
  const { setWorkspaceId } = useActiveWorkspace();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const response = (await createWorkspace.mutateAsync({ name })) as { data: { workspace: { id: string } } };
    setWorkspaceId(response.data.workspace.id);
    router.push("/dashboard");
    router.refresh();
  }

  return (
    <Card>
      <h1>Create your first workspace</h1>
      <p className="muted">Every future product module in this starter will be scoped to a workspace.</p>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Workspace name
          <Input onChange={(event) => setName(event.target.value)} placeholder="Acme Labs" value={name} />
        </label>
        {createWorkspace.error ? <p className="error">{createWorkspace.error.message}</p> : null}
        <Button disabled={createWorkspace.isPending} type="submit">
          {createWorkspace.isPending ? "Creating..." : "Create workspace"}
        </Button>
      </form>
    </Card>
  );
}
