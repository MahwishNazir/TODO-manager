import { AuthLayout } from "@/components/auth/auth-layout";
import { SigninForm } from "@/components/auth/signin-form";

export default function SigninPage() {
  return (
    <AuthLayout
      title="Welcome back"
      description="Enter your credentials to sign in to your account"
      footer={{
        text: "Don't have an account?",
        linkText: "Sign up",
        linkHref: "/signup",
      }}
    >
      <SigninForm />
    </AuthLayout>
  );
}
