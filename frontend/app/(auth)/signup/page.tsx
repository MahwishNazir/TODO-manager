import { AuthLayout } from "@/components/auth/auth-layout";
import { SignupForm } from "@/components/auth/signup-form";

export default function SignupPage() {
  return (
    <AuthLayout
      title="Create an account"
      description="Enter your details below to create your account"
      footer={{
        text: "Already have an account?",
        linkText: "Sign in",
        linkHref: "/signin",
      }}
    >
      <SignupForm />
    </AuthLayout>
  );
}
