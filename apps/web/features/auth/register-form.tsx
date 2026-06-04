"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useRegister } from "@/hooks/use-current-user";
import { buildAuthHref, getPostAuthDestination } from "@/lib/auth-navigation";

export function RegisterForm({ inviteToken, nextUrl }: { inviteToken?: string | null; nextUrl?: string | null }) {
  const router = useRouter();
  const register = useRegister();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await register.mutateAsync({ name, email, password });
    const destination = getPostAuthDestination({ inviteToken, nextUrl, defaultPath: "/onboarding" });
    router.push(destination);
    router.refresh();
  }

  return (
    <Card>
      <h1>Create your account</h1>
      <p className="muted">Start with the shared SaaS foundation and add product logic later.</p>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Name
          <Input onChange={(event) => setName(event.target.value)} value={name} />
        </label>
        <label>
          Email
          <Input onChange={(event) => setEmail(event.target.value)} type="email" value={email} />
        </label>
        <label>
          Password
          <Input onChange={(event) => setPassword(event.target.value)} type="password" value={password} />
        </label>
        {register.error ? <p className="error">{register.error.message}</p> : null}
        <Button disabled={register.isPending} type="submit">
          {register.isPending ? "Creating..." : "Create account"}
        </Button>
      </form>
      <p className="muted">
        Already have an account? <Link href={buildAuthHref("/login", { inviteToken, nextUrl })}>Sign in</Link>
      </p>
    </Card>
  );
}
