import { LoginForm } from "@/features/auth/login-form";

type LoginPageProps = {
  searchParams: Promise<{
    invite?: string | string[];
    next?: string | string[];
  }>;
};

function pickFirst(value: string | string[] | undefined): string | null {
  if (Array.isArray(value)) {
    return value[0] ?? null;
  }
  return value ?? null;
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const params = await searchParams;
  return <LoginForm inviteToken={pickFirst(params.invite)} nextUrl={pickFirst(params.next)} />;
}
