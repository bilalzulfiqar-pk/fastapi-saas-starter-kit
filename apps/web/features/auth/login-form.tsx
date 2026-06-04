"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useLogin } from "@/hooks/use-current-user";
import { buildAuthHref, getPostAuthDestination } from "@/lib/auth-navigation";

export function LoginForm({ inviteToken, nextUrl }: { inviteToken?: string | null; nextUrl?: string | null }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await login.mutateAsync({ email, password });
    const destination = getPostAuthDestination({ inviteToken, nextUrl, defaultPath: "/dashboard" });
    router.push(destination);
    router.refresh();
  }

  return (
    <Card>
      <h1>Welcome back</h1>
      <p className="muted">Sign in to access your dashboard.</p>
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Email
          <Input onChange={(event) => setEmail(event.target.value)} type="email" value={email} />
        </label>
        <label>
          Password
          <Input onChange={(event) => setPassword(event.target.value)} type="password" value={password} />
        </label>
        {login.error ? <p className="error">{login.error.message}</p> : null}
        <Button disabled={login.isPending} type="submit">
          {login.isPending ? "Signing in..." : "Sign in"}
        </Button>
      </form>
      <p className="muted">
        Need an account? <Link href={buildAuthHref("/register", { inviteToken, nextUrl })}>Create one</Link>
      </p>
    </Card>
  );
}
