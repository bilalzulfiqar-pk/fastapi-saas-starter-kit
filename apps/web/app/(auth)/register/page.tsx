import { RegisterForm } from "@/features/auth/register-form";

type RegisterPageProps = {
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

export default async function RegisterPage({ searchParams }: RegisterPageProps) {
  const params = await searchParams;
  return <RegisterForm inviteToken={pickFirst(params.invite)} nextUrl={pickFirst(params.next)} />;
}
